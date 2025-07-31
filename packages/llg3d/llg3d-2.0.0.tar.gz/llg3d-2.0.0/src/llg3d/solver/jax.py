"""
LLG3D solver using XLA compilation
"""

import os
import time

import jax
import jax.numpy as jnp
from jax import random

from ..output import progress_bar, get_output_files, close_output_files
from ..grid import Grid
from ..element import Element


# JIT compile individual components for better performance and modularity
@jax.jit
def compute_H_anisotropy(
    m: jnp.ndarray, coeff_2: float, anisotropy: int
) -> jnp.ndarray:
    """
    Compute anisotropy field (JIT compiled)
    
    Args:
        m: Magnetization array (shape (3, nx, ny, nz))
        coeff_2: Coefficient for anisotropy
        anisotropy: Anisotropy type (0: uniaxial, 1: cubic)

    Returns:
        Anisotropy field array (shape (3, nx, ny, nz))
    """

    m1, m2, m3 = m

    m1m1 = m1 * m1
    m2m2 = m2 * m2
    m3m3 = m3 * m3

    # Uniaxial anisotropy
    aniso_1_uniaxial = m1
    aniso_2_uniaxial = jnp.zeros_like(m1)
    aniso_3_uniaxial = jnp.zeros_like(m1)

    # Cubic anisotropy
    aniso_1_cubic = -(1 - m1m1 + m2m2 * m3m3) * m1
    aniso_2_cubic = -(1 - m2m2 + m1m1 * m3m3) * m2
    aniso_3_cubic = -(1 - m3m3 + m1m1 * m2m2) * m3

    # Select based on anisotropy type
    aniso_1 = jnp.where(
        anisotropy == 0,
        aniso_1_uniaxial,
        jnp.where(anisotropy == 1, aniso_1_cubic, jnp.zeros_like(m1)),
    )
    aniso_2 = jnp.where(
        anisotropy == 0,
        aniso_2_uniaxial,
        jnp.where(anisotropy == 1, aniso_2_cubic, jnp.zeros_like(m1)),
    )
    aniso_3 = jnp.where(
        anisotropy == 0,
        aniso_3_uniaxial,
        jnp.where(anisotropy == 1, aniso_3_cubic, jnp.zeros_like(m1)),
    )

    return coeff_2 * jnp.stack([aniso_1, aniso_2, aniso_3], axis=0)


@jax.jit
def laplacian3D(
    m_i: jnp.ndarray, dx2_inv: float, dy2_inv: float, dz2_inv: float, center_coeff: float
) -> jnp.ndarray:
    """
    Compute Laplacian for a single component with Neumann boundary conditions (JIT compiled)
    
    Args:
        m_i: Single component of magnetization (shape (nx, ny, nz))
        dx2_inv: Inverse of squared grid spacing in x direction
        dy2_inv: Inverse of squared grid spacing in y direction
        dz2_inv: Inverse of squared grid spacing in z direction
        center_coeff: Coefficient for the center point

    Returns:
        Laplacian of m_i (shape (nx, ny, nz))
    """
    m_i_padded = jnp.pad(m_i, ((1, 1), (1, 1), (1, 1)), mode="reflect")
    return (
        dx2_inv * (m_i_padded[2:, 1:-1, 1:-1] + m_i_padded[:-2, 1:-1, 1:-1])
        + dy2_inv * (m_i_padded[1:-1, 2:, 1:-1] + m_i_padded[1:-1, :-2, 1:-1])
        + dz2_inv * (m_i_padded[1:-1, 1:-1, 2:] + m_i_padded[1:-1, 1:-1, :-2])
        + center_coeff * m_i
    )


@jax.jit
def compute_laplacian(
    m: jnp.ndarray, dx: float, dy: float, dz: float
) -> jnp.ndarray:
    """
    Compute 3D Laplacian with Neumann boundary conditions (JIT compiled)
    
    Args:
        m: Magnetization array (shape (3, nx, ny, nz))
        dx: Grid spacing in x direction
        dy: Grid spacing in y direction
        dz: Grid spacing in z direction

    Returns:
        Laplacian of m (shape (3, nx, ny, nz))
    """
    dx2_inv, dy2_inv, dz2_inv = 1 / dx**2, 1 / dy**2, 1 / dz**2
    center_coeff = -2 * (dx2_inv + dy2_inv + dz2_inv)
    
    return jnp.stack(
        [
            laplacian3D(m[0], dx2_inv, dy2_inv, dz2_inv, center_coeff),
            laplacian3D(m[1], dx2_inv, dy2_inv, dz2_inv, center_coeff),
            laplacian3D(m[2], dx2_inv, dy2_inv, dz2_inv, center_coeff),
        ],
        axis=0,
    )


@jax.jit
def compute_space_average_jax(m1: jnp.ndarray) -> float:
    """
    Compute space average using midpoint method on GPU (JIT compiled)
    
    Args:
        m1: First component of magnetization (shape (nx, ny, nz))
        
    Returns:
        Space average of m1
    """
    # Get dimensions directly from the array shape
    Jx, Jy, Jz = m1.shape
    
    # Create 3D coordinate grids using the shape
    i_coords = jnp.arange(Jx)
    j_coords = jnp.arange(Jy) 
    k_coords = jnp.arange(Jz)
    
    # Create 3D coordinate grids
    ii, jj, kk = jnp.meshgrid(i_coords, j_coords, k_coords, indexing='ij')
    
    # Apply midpoint weights (0.5 on edges, 1.0 elsewhere)
    weights = jnp.ones_like(m1)
    weights = jnp.where((ii == 0) | (ii == Jx-1), weights * 0.5, weights)
    weights = jnp.where((jj == 0) | (jj == Jy-1), weights * 0.5, weights)
    weights = jnp.where((kk == 0) | (kk == Jz-1), weights * 0.5, weights)
    
    # Compute weighted sum and normalize
    weighted_sum = jnp.sum(weights * m1)
    
    # Compute ncell from the weights (this is the effective cell count)
    ncell = jnp.sum(weights)
    
    return weighted_sum / ncell


@jax.jit
def cross_product(a: jnp.ndarray, b: jnp.ndarray) -> jnp.ndarray:
    r"""
    Compute cross product :math:`a \times b` (JIT compiled)

    Args:
        a: First vector (shape (3, nx, ny, nz))
        b: Second vector (shape (3, nx, ny, nz))

    Returns:
        Cross product :math:`a \times b` (shape (3, nx, ny, nz))
    """
    # Use JAX's optimized cross product function directly on axis 0
    return jnp.cross(a, b, axis=0)


# JIT compile the slope computation for performance
@jax.jit
def compute_slope(
    g_params: dict, e_params: dict, m: jnp.ndarray, R_random: jnp.ndarray
) -> jnp.ndarray:
    """
    JIT-compiled version of compute_slope_jax using modular sub-functions

    Args:
        g_params: Grid parameters dict (dx, dy, dz)
        e_params: Element parameters dict (coeff_1, coeff_2, coeff_3, lambda_G, anisotropy)
        m: Magnetization array (shape (3, nx, ny, nz))
        R_random: Random field array (shape (3, nx, ny, nz))

    Returns:
        Slope array (shape (3, nx, ny, nz))
    """
    # Extract parameters
    dx, dy, dz = g_params["dx"], g_params["dy"], g_params["dz"]
    coeff_1 = e_params["coeff_1"]
    coeff_2 = e_params["coeff_2"]
    coeff_3 = e_params["coeff_3"]
    lambda_G = e_params["lambda_G"]
    anisotropy = e_params["anisotropy"]

    # Compute components using modular sub-functions
    H_aniso = compute_H_anisotropy(m, coeff_2, anisotropy)
    laplacian_m = compute_laplacian(m, dx, dy, dz)

    # Effective field
    R_eff = coeff_1 * laplacian_m + R_random + H_aniso
    R_eff = R_eff.at[0].add(coeff_3)

    # Cross products using modular functions
    m_cross_R_eff = cross_product(m, R_eff)
    m_cross_m_cross_R_eff = cross_product(m, m_cross_R_eff)

    return -(m_cross_R_eff + lambda_G * m_cross_m_cross_R_eff)


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
    Simulates the system for N iterations using JAX

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
        - The time taken for the simulation
        - The output filenames
        - The average magnetization
    """

    # Configure JAX
    if device == "auto":
        # Let JAX choose the best available device
        pass
    elif device == "cpu":
        jax.config.update("jax_platform_name", "cpu")
    elif device == "gpu":
        jax.config.update("jax_platform_name", "gpu")
    elif device.startswith("gpu:"):
        # Select specific GPU using environment variable
        jax.config.update("jax_platform_name", "gpu")
        gpu_id = device.split(":")[1]
        # Check if CUDA_VISIBLE_DEVICES is already set externally
        if "CUDA_VISIBLE_DEVICES" not in os.environ:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
            print(f"Set CUDA_VISIBLE_DEVICES={gpu_id}")
        else:
            print(f"Using external CUDA_VISIBLE_DEVICES={os.environ['CUDA_VISIBLE_DEVICES']}")

    # Set precision
    if precision == "double":
        jax.config.update("jax_enable_x64", True)
        jnp_float = jnp.float64
    else:
        jax.config.update("jax_enable_x64", False)
        jnp_float = jnp.float32

    print(f"Available JAX devices: {jax.devices()}")
    print(f"Using JAX on device: {jax.devices()[0]}")
    print(f"Precision: {precision} ({jnp_float})")

    # Initialize random key for JAX
    key = random.PRNGKey(seed)

    g = Grid(Jx, Jy, Jz, dx)
    dims = g.dims

    e = element_class(T, H_ext, g, dt)
    print(f"CFL = {e.get_CFL()}")

    # Prepare parameters for JIT compilation using to_dict methods
    g_params = g.to_dict()
    e_params = e.to_dict()

    # --- Initialization ---
    def theta_init(shape):
        """Initialization of theta"""
        return jnp.zeros(shape, dtype=jnp_float)

    def phi_init(t, shape):
        """Initialization of phi"""
        return jnp.zeros(shape, dtype=jnp_float) + e.gamma_0 * H_ext * t

    m_n = jnp.zeros((3,) + dims, dtype=jnp_float)

    theta = theta_init(dims)
    phi = phi_init(0, dims)

    m_n = m_n.at[0].set(jnp.cos(theta))
    m_n = m_n.at[1].set(jnp.sin(theta) * jnp.cos(phi))
    m_n = m_n.at[2].set(jnp.sin(theta) * jnp.sin(phi))

    f_mean, f_profiles, output_filenames = get_output_files(g, T, n_mean, n_profile)

    t = 0.0
    m1_average = 0.0

    # === JIT WARMUP: Pre-compile all functions to exclude compilation time ===
    print("Warming up JIT compilation...")
    
    # Generate dummy random field for warmup
    warmup_key = random.PRNGKey(42)
    R_warmup = e.coeff_4 * random.normal(warmup_key, (3,) + dims, dtype=jnp_float)
    
    # Warmup all JIT functions with actual data shapes
    _ = compute_slope(g_params, e_params, m_n, R_warmup)
    if n_mean != 0:
        _ = compute_space_average_jax(m_n[0])
    
    # Force compilation and execution to complete
    jax.block_until_ready(m_n)
    print("JIT warmup completed.")

    start_time = time.perf_counter()

    for n in progress_bar(range(1, N + 1), "Iteration : ", 40):
        t += dt

        # Generate random field for temperature effect
        key, subkey = random.split(key)
        R_random = e.coeff_4 * random.normal(subkey, (3,) + dims, dtype=jnp_float)

        # Use JIT-compiled version for better performance
        s_pre = compute_slope(g_params, e_params, m_n, R_random)
        m_pre = m_n + dt * s_pre
        s_cor = compute_slope(g_params, e_params, m_pre, R_random)

        # Update magnetization
        m_n = m_n + dt * 0.5 * (s_pre + s_cor)

        # Renormalize to unit sphere
        norm = jnp.sqrt(m_n[0] ** 2 + m_n[1] ** 2 + m_n[2] ** 2)
        m_n = m_n / norm

        # Export the average of m1 to a file (optimized for GPU)
        if n_mean != 0 and n % n_mean == 0:
            # Compute space average directly on GPU without CPU transfer
            m1_mean = compute_space_average_jax(m_n[0])
            # Convert to Python float for file writing
            m1_mean = float(m1_mean)
            if n >= start_averaging:
                m1_average += m1_mean * n_mean
            f_mean.write(f"{t:10.8e} {m1_mean:10.8e}\n")

    total_time = time.perf_counter() - start_time

    close_output_files(f_mean, f_profiles)

    if n > start_averaging:
        m1_average /= N - start_averaging

    return total_time, output_filenames, m1_average
