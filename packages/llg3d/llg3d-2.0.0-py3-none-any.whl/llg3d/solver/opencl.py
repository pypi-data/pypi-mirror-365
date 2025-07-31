"""
LLG3D Solver using OpenCL
"""

import time
from pathlib import Path

import numpy as np
import pyopencl as cl
from pyopencl import clrandom
from pyopencl import array as clarray

from ..output import progress_bar, get_output_files, close_output_files
from ..grid import Grid
from ..element import Element, Cobalt


def get_context_and_device(device_selection: str = "auto") -> tuple[cl.Context, cl.Device]:
    """
    Get the OpenCL context and device

    Args:
        device_selection:
            
            - ``"auto"``: Let OpenCL choose automatically
            - ``"cpu"``: Select CPU device  
            - ``"gpu"``: Select first available GPU
            - ``"gpu:N"``: Select specific GPU by index (e.g., ``"gpu:0"``, ``"gpu:1"``)

    Returns:
        - The OpenCL context
        - The OpenCL device
    """
    if device_selection == "auto":
        context = cl.create_some_context(interactive=False)
        device = context.devices[0]
        return context, device
    
    # Get all platforms and devices
    platforms = cl.get_platforms()
    all_devices = []
    
    for platform in platforms:
        all_devices.extend(platform.get_devices())
    
    if not all_devices:
        raise RuntimeError("No OpenCL devices found")
    
    # Filter devices based on selection
    if device_selection == "cpu":
        cpu_devices = [d for d in all_devices if d.type & cl.device_type.CPU]
        if not cpu_devices:
            raise RuntimeError("No CPU devices found")
        selected_device = cpu_devices[0]
    elif device_selection == "gpu":
        gpu_devices = [d for d in all_devices if d.type & cl.device_type.GPU]
        if not gpu_devices:
            raise RuntimeError("No GPU devices found")
        selected_device = gpu_devices[0]
    elif device_selection.startswith("gpu:"):
        gpu_devices = [d for d in all_devices if d.type & cl.device_type.GPU]
        if not gpu_devices:
            raise RuntimeError("No GPU devices found")
        
        gpu_index = int(device_selection.split(":")[1])
        if gpu_index >= len(gpu_devices):
            raise RuntimeError(f"GPU index {gpu_index} not available. Found {len(gpu_devices)} GPU(s)")
        selected_device = gpu_devices[gpu_index]
    else:
        raise ValueError(f"Invalid device selection: {device_selection}")
    
    # Create context with selected device
    context = cl.Context([selected_device])
    print(f"Selected OpenCL device: {selected_device.name} ({selected_device.type})")
    
    return context, selected_device


def get_precision(device: cl.Device, precision: str) -> np.dtype:
    """
    Get the numpy float type based on the precision

    Args:
        precision: Precision of the simulation (single or double)

    Returns:
        The numpy float type (float32 or float64)

    Raises:
        RuntimeError: If double precision is asked while the device does not support it
    """
    # Check that cl device supports double precision
    if precision == "double" and not device.double_fp_config:
        raise RuntimeError("The selected device does not support double precision.")

    return np.float64 if precision == "double" else np.float32


class Program:
    """
    Class to manage the OpenCL kernels for the LLG3D simulation
    """

    def __init__(self, g: Grid, context: cl.Context, np_float: np.dtype):
        self.grid = g
        self.context = context
        self.np_float = np_float
        self.cl_program = self._get_built_program()

    def _get_built_program(self) -> cl.Program:
        """
        Return the OpenCL program built from the source code

        Returns:
            The OpenCL program object
        """

        opencl_code = (Path(__file__).parent / "llg3d.cl").read_text()
        build_options = "-D USE_DOUBLE_PRECISION" if self.np_float == np.float64 else ""
        build_options += (
            f" -D NX={self.grid.Jx} -D NY={self.grid.Jy} -D NZ={self.grid.Jz}"
        )
        return cl.Program(self.context, opencl_code).build(options=build_options)

    def get_kernel(self, kernel_name: str, arg_types: list = [None]) -> cl.Kernel:
        """
        Returns the specified kernel by name.

        Args:
            kernel_name: Name of the kernel to retrieve
            arg_types: List of argument types for the kernel

        Returns:
            The OpenCL kernel object
        """
        kernel: cl.Kernel = getattr(self.cl_program, kernel_name)
        kernel.set_arg_types(arg_types)
        return kernel


def simulate(
    N: int,
    Jx: int,
    Jy: int,
    Jz: int,
    dx: float,
    T: float,
    H_ext: float,
    dt: float,
    start_averaging: int,
    n_mean: int,
    n_profile: int,
    element_class: Element,
    precision: str,
    seed: int,
    device: str = "auto",
    **_,
) -> tuple[float, str, float]:
    """
    Simulates the system over N iterations

    Args:
        N: Number of iterations
        Jx: Number of grid points in x direction
        Jy: Number of grid points in y direction
        Jz: Number of grid points in z direction        
        dx: Grid spacing
        T: Temperature in Kelvin
        H_ext: External magnetic field strength
        dt: Time step for the simulation
        start_averaging: Number of iterations for averaging
        n_mean: Number of iterations for integral output
        n_profile: Number of iterations for profile output
        element_class: Element of the sample (default: Cobalt)
        precision: Precision of the simulation (single or double)
        seed: Random seed for temperature fluctuations
        device: Device to use ('cpu', 'gpu', 'gpu:0', 'gpu:1', etc., or 'auto')

    Returns:
        - The grid object
        - The time taken for the simulation
        - The output filename
    """

    context, opencl_device = get_context_and_device(device)
    np_float = get_precision(opencl_device, precision)

    g = Grid(Jx, Jy, Jz, dx)
    print(g)

    e = element_class(T, H_ext, g, dt)
    if not isinstance(e, Cobalt):
        raise NotImplementedError(f"Element is {type(e)} but only {Cobalt} is supported at the moment.")
    print(f"CFL = {e.get_CFL()}")

    # --- Initialization ---

    def theta_init(shape):
        """Initialization of theta"""
        return np.zeros(shape, dtype=np_float)

    def phi_init(t, shape):
        """Initialization of phi"""
        return np.zeros(shape, dtype=np_float) + e.gamma_0 * H_ext * t

    m_n = np.zeros((3,) + g.dims, dtype=np_float)

    theta = theta_init(g.dims)
    phi = phi_init(0, g.dims)

    m_n[0] = np.cos(theta)
    m_n[1] = np.sin(theta) * np.cos(phi)
    m_n[2] = np.sin(theta) * np.sin(phi)

    queue = cl.CommandQueue(context)

    program = Program(g, context, np_float)
    slope_kernel = program.get_kernel("slope", [None] * 3 + [np_float] * 8)
    update_1_kernel = program.get_kernel("update_1", [None] * 3 + [np_float])
    update_2_kernel = program.get_kernel("update_2", [None] * 4 + [np_float])
    normalize_kernel = program.get_kernel("normalize")
    
    # Create a CL array for m1 component in order to compute averages
    d_m1 = clarray.empty(queue, g.ntot, np_float)
    copy_m1_kernel = program.get_kernel("copy_m1", [None, None])

    mf = cl.mem_flags
    mem_size = m_n.nbytes

    d_m_n = cl.Buffer(context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=m_n)
    d_R_alea = cl.array.Array(queue, (3,) + g.dims, np_float)
    d_m_np1 = cl.Buffer(context, mf.READ_WRITE, mem_size)
    d_s_pre = cl.Buffer(context, mf.READ_WRITE, mem_size)
    d_s_cor = cl.Buffer(context, mf.READ_WRITE, mem_size)

    rng = clrandom.PhiloxGenerator(context, seed=seed)

    f_mean, f_profiles, output_filenames = get_output_files(g, T, n_mean, n_profile)

    t = 0.0
    m1_average = 0.0

    start_time = time.perf_counter()

    for n in progress_bar(range(1, N + 1), "Iteration : ", 40):
        t += dt

        rng.fill_normal(d_R_alea)
        queue.finish()  # ensure the array is filled

        # Prediction phase

        # calculate s_i_pre from m_i^n
        slope_kernel(
            queue,
            g.dims,
            None,
            d_m_n,
            d_R_alea.data,
            d_s_pre,
            g.dx,
            g.dy,
            g.dz,
            e.coeff_1,
            e.coeff_2,
            e.coeff_3,
            e.coeff_4,
            e.lambda_G,
        )

        # m_i^n+1 = m_i^n + dt * s_i_pre
        update_1_kernel(queue, (3 * g.ntot,), None, d_m_n, d_m_np1, d_s_pre, dt)
        queue.finish()

        # # Correction phase

        # calculate s_i_cor from m_i^n+1
        slope_kernel(
            queue,
            g.dims,
            None,
            d_m_np1,
            d_R_alea.data,
            d_s_cor,
            g.dx,
            g.dy,
            g.dz,
            e.coeff_1,
            e.coeff_2,
            e.coeff_3,
            e.coeff_4,
            e.lambda_G,
        )
        # m_i^n+1 = m_i^n + dt * (s_i_pre + s_i_cor) / 2
        # Update using the corrected values
        update_2_kernel(
            queue, (3 * g.ntot,), None, d_m_n, d_m_np1, d_s_pre, d_s_cor, dt
        )
        queue.finish()

        # Normalization
        normalize_kernel(queue, (g.ntot,), None, d_m_np1).wait()

        # Swap the buffers for the next iteration
        d_m_n, d_m_np1 = d_m_np1, d_m_n

        # Space average of m_1 using the midpoint method with OpenCL sum
        if n_mean != 0 and n % n_mean == 0:
            # Copy only the first component from d_m_n to d_m1 with weights applied
            # d_m_n contains [m1, m2, m3] interleaved, we want only m1
            copy_m1_kernel(queue, g.dims, None, d_m_n, d_m1.data)
            
            # Use PyOpenCL array sum to compute the weighted sum
            weighted_sum = clarray.sum(d_m1).get()
            m1_mean = weighted_sum / g.ncell
            
            if n >= start_averaging:
                m1_average += m1_mean * n_mean

            f_mean.write(f"{t:10.8e} {m1_mean:10.8e}\n")

    total_time = time.perf_counter() - start_time

    close_output_files(f_mean, f_profiles)

    if n > start_averaging:
        m1_average /= N - start_averaging

    return total_time, output_filenames, m1_average
