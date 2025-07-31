"""
LLG3D Solver using NumPy
"""

import time

import numpy as np

from ..output import progress_bar, get_output_files, close_output_files
from ..grid import Grid
from ..element import Element
from .solver import space_average, cross_product, compute_H_anisotropy


def laplacian3D(
    m_i: np.ndarray, dx2_inv: float, dy2_inv: float, dz2_inv: float, center_coeff: float
) -> np.ndarray:
    """
    Returns the laplacian of m in 3D

    Args:
        m_i: Magnetization array (shape (nx, ny, nz))
        dx2_inv: Inverse of the square of the grid spacing in x direction
        dy2_inv: Inverse of the square of the grid spacing in y direction
        dz2_inv: Inverse of the square of the grid spacing in z direction
        center_coeff: Coefficient for the center point in the laplacian

    Returns:
        Laplacian of m (shape (nx, ny, nz))
    """

    m_i_padded = np.pad(m_i, ((1, 1), (1, 1), (1, 1)), mode="reflect")

    laplacian = (
        dx2_inv * (m_i_padded[2:, 1:-1, 1:-1] + m_i_padded[:-2, 1:-1, 1:-1])
        + dy2_inv * (m_i_padded[1:-1, 2:, 1:-1] + m_i_padded[1:-1, :-2, 1:-1])
        + dz2_inv * (m_i_padded[1:-1, 1:-1, 2:] + m_i_padded[1:-1, 1:-1, :-2])
        + center_coeff * m_i
    )
    return laplacian


def compute_laplacian(g: Grid, m: np.ndarray) -> np.ndarray:
    """
    Compute the laplacian of m in 3D

    Args:
        g: Grid object
        m: Magnetization array (shape (3, nx, ny, nz))

    Returns:
        Laplacian of m (shape (3, nx, ny, nz))
    """

    dx2_inv, dy2_inv, dz2_inv, center_coeff = g.get_laplacian_coeff()

    return np.stack(
        [
            laplacian3D(m[0], dx2_inv, dy2_inv, dz2_inv, center_coeff),
            laplacian3D(m[1], dx2_inv, dy2_inv, dz2_inv, center_coeff),
            laplacian3D(m[2], dx2_inv, dy2_inv, dz2_inv, center_coeff),
        ],
        axis=0,
    )


def compute_slope(
    g: Grid, e: Element, m: np.ndarray, R_random: np.ndarray
) -> np.ndarray:
    """
    Compute the slope of the LLG equation
    Args:
        g: Grid object
        e: Element object
        m: Magnetization array (shape (3, nx, ny, nz))
        R_random: Random field array (shape (3, nx, ny, nz))

    Returns:
        Slope array (shape (3, nx, ny, nz))
    """

    H_aniso = compute_H_anisotropy(e, m)

    laplacian_m = compute_laplacian(g, m)
    R_eff = e.coeff_1 * laplacian_m + R_random + H_aniso
    R_eff[0] += e.coeff_3

    m_cross_R_eff = cross_product(m, R_eff)
    m_cross_m_cross_R_eff = cross_product(m, m_cross_R_eff)

    s = -(m_cross_R_eff + e.lambda_G * m_cross_m_cross_R_eff)

    return s


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
    **_,
) -> tuple[float, str, float]:
    """
    Simulates the system for N iterations

    Args:
        N: Number of iterations
        Jx: Number of grid points in x direction
        Jy: Number of grid points in y direction
        Jz: Number of grid points in z direction        dx: Grid spacing
        T: Temperature in Kelvin
        H_ext: External magnetic field strength
        dt: Time step for the simulation
        start_averaging: Number of iterations for averaging
        n_mean: Number of iterations for integral output
        n_profile: Number of iterations for profile output
        element_class: Element of the sample (default: Cobalt)
        precision: Precision of the simulation (single or double)
        seed: Random seed for temperature fluctuations

    Returns:
        - The time taken for the simulation
        - The output filenames
        - The average magnetization
    """
    np_float = np.float64 if precision == "double" else np.float32
    # Initialize a sequence of random seeds
    # See: https://numpy.org/doc/stable/reference/random/parallel.html#seedsequence-spawning
    ss = np.random.SeedSequence(seed)

    # Deploy size x SeedSequence to be passed to child processes
    child_seeds = ss.spawn(1)
    rng = np.random.default_rng(child_seeds[0])

    g = Grid(Jx, Jy, Jz, dx)

    dims = g.dims

    e = element_class(T, H_ext, g, dt)
    print(f"CFL = {e.get_CFL()}")

    # --- Initialization ---

    def theta_init(shape):
        """Initialization of theta"""
        return np.zeros(shape, dtype=np_float)

    def phi_init(t, shape):
        """Initialization of phi"""
        return np.zeros(shape, dtype=np_float) + e.gamma_0 * H_ext * t

    m_n = np.zeros((3,) + dims, dtype=np_float)

    theta = theta_init(dims)
    phi = phi_init(0, dims)

    m_n[0] = np.cos(theta)
    m_n[1] = np.sin(theta) * np.cos(phi)
    m_n[2] = np.sin(theta) * np.sin(phi)

    f_mean, f_profiles, output_filenames = get_output_files(g, T, n_mean, n_profile)

    t = 0.0
    m1_average = 0.0

    start_time = time.perf_counter()

    for n in progress_bar(range(1, N + 1), "Iteration : ", 40):
        t += dt

        # Adding randomness: temperature effect
        R_random = e.coeff_4 * rng.standard_normal((3,) + dims, dtype=np_float)

        # Prediction phase
        s_pre = compute_slope(g, e, m_n, R_random)
        m_pre = m_n + dt * s_pre

        # Correction phase
        s_cor = compute_slope(g, e, m_pre, R_random)
        m_n += dt * 0.5 * (s_pre + s_cor)

        # We renormalize to check the constraint of being on the sphere
        norm = np.sqrt(m_n[0] ** 2 + m_n[1] ** 2 + m_n[2] ** 2)
        m_n /= norm

        # Export the average of m1 to a file
        if n_mean != 0 and n % n_mean == 0:
            m1_mean = space_average(g, m_n[0])
            if n >= start_averaging:
                m1_average += m1_mean * n_mean
            f_mean.write(f"{t:10.8e} {m1_mean:10.8e}\n")

    total_time = time.perf_counter() - start_time

    close_output_files(f_mean, f_profiles)

    if n > start_averaging:
        m1_average /= N - start_averaging

    return total_time, output_filenames, m1_average
