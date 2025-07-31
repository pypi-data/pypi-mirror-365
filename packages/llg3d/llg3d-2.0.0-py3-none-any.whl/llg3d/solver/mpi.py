"""
LLG3D Solver using MPI

The parallelization is done in the x direction.
"""

import argparse
import sys
import time

import numpy as np
from mpi4py import MPI

from .. import comm, rank, size, status
from ..output import progress_bar, get_output_files, close_output_files
from ..grid import Grid
from ..element import Element
from .solver import cross_product, compute_H_anisotropy


def get_boundaries_x(
    g: Grid, m: np.ndarray, blocking: bool = False
) -> tuple[np.ndarray, np.ndarray, MPI.Request, MPI.Request]:
    """
    Returns the boundaries asynchronously:
    allows overlapping communication time of boundaries
    with calculations

    Args:
        g: Grid object
        m: Magnetization array (shape (3, nx, ny, nz))
        blocking: Whether to use blocking communication for boundaries

    Returns:
        - m_i_x_start: Start boundary in x direction
        - m_i_x_end: End boundary in x direction
        - request_start: Request for start boundary
        - request_end: Request for end boundary
    """

    # Extract slices for Neumann boundary conditions

    m_i_x_start = np.empty((1, g.Jy, g.Jz))
    m_i_x_end = np.empty_like(m_i_x_start)

    # Prepare ring communication:
    # Even if procs 0 and size - 1 shouldn't receive anything from left
    # and right respectively, it's simpler to express it like this
    right = (rank + 1) % size
    left = (rank - 1 + size) % size

    if blocking:
        # Wait for boundaries to be available
        comm.Sendrecv(
            m[:1, :, :], dest=left, sendtag=0, recvbuf=m_i_x_end, source=right
        )
        comm.Sendrecv(
            m[-1:, :, :], dest=right, sendtag=1, recvbuf=m_i_x_start, source=left
        )
        return m_i_x_start, m_i_x_end, None, None
    else:
        request_start = comm.Irecv(m_i_x_start, source=left, tag=201)
        request_end = comm.Irecv(m_i_x_end, source=right, tag=202)
        comm.Isend(m[-1:, :, :], dest=right, tag=201)
        comm.Isend(m[:1, :, :], dest=left, tag=202)

        return m_i_x_start, m_i_x_end, request_start, request_end


def laplacian3D(
    m_i: np.ndarray,
    dx2_inv: float,
    dy2_inv: float,
    dz2_inv: float,
    center_coeff: float,
    m_i_x_start: np.ndarray,
    m_i_x_end: np.ndarray,
    request_end: MPI.Request,
    request_start: MPI.Request,
) -> np.ndarray:
    """
    Returns the Laplacian of m_i in 3D.
    We start by calculating contributions in y and z, to wait
    for the end of communications in x.

    Args:
        m_i: i-component of the magnetization array (shape (nx, ny, nz))
        dx2_inv: inverse of the squared grid spacing in x direction
        dy2_inv: inverse of the squared grid spacing in y direction
        dz2_inv: inverse of the squared grid spacing in z direction
        center_coeff: center coefficient for the Laplacian
        m_i_x_start: start boundary in x direction
        m_i_x_end: end boundary in x direction
        request_start: request for start boundary
        request_end: request for end boundary

    Returns:
        Laplacian of m_i (shape (nx, ny, nz))
    """

    # Extract slices for Neumann boundary conditions
    m_i_y_start = m_i[:, 1:2, :]
    m_i_y_end = m_i[:, -2:-1, :]

    m_i_z_start = m_i[:, :, 1:2]
    m_i_z_end = m_i[:, :, -2:-1]

    m_i_y_plus = np.concatenate((m_i[:, 1:, :], m_i_y_end), axis=1)
    m_i_y_minus = np.concatenate((m_i_y_start, m_i[:, :-1, :]), axis=1)
    m_i_z_plus = np.concatenate((m_i[:, :, 1:], m_i_z_end), axis=2)
    m_i_z_minus = np.concatenate((m_i_z_start, m_i[:, :, :-1]), axis=2)

    laplacian = (
        dy2_inv * (m_i_y_plus + m_i_y_minus)
        + dz2_inv * (m_i_z_plus + m_i_z_minus)
        + center_coeff * m_i
    )

    # Wait for x-boundaries to be available (communications completed)
    try:
        request_end.Wait(status)
        request_start.Wait(status)
    except AttributeError:
        pass  # Blocking case

    # For extreme procs, apply Neumann boundary conditions in x
    if rank == size - 1:
        m_i_x_end = m_i[-2:-1, :, :]
    if rank == 0:
        m_i_x_start = m_i[1:2, :, :]

    m_i_x_plus = np.concatenate((m_i[1:, :, :], m_i_x_end), axis=0)
    m_i_x_minus = np.concatenate((m_i_x_start, m_i[:-1, :, :]), axis=0)

    laplacian += dx2_inv * (m_i_x_plus + m_i_x_minus)

    return laplacian


def compute_laplacian(
    g: Grid,
    m: np.ndarray,
    boundaries: tuple[np.ndarray, np.ndarray, MPI.Request, MPI.Request],
) -> np.ndarray:
    """
    Compute the laplacian of m in 3D

    Args:
        g: Grid object
        m: Magnetization array (shape (3, nx, ny, nz))
        boundaries: Boundaries for x direction

    Returns:
        Laplacian of m (shape (3, nx, ny, nz))
    """

    dx2_inv, dy2_inv, dz2_inv, center_coeff = g.get_laplacian_coeff()

    return np.stack(
        [
            laplacian3D(m[0], dx2_inv, dy2_inv, dz2_inv, center_coeff, *boundaries[0]),
            laplacian3D(m[1], dx2_inv, dy2_inv, dz2_inv, center_coeff, *boundaries[1]),
            laplacian3D(m[2], dx2_inv, dy2_inv, dz2_inv, center_coeff, *boundaries[2]),
        ],
        axis=0,
    )


def compute_slope(
    e: Element,
    g: Grid,
    m: np.ndarray,
    R_random: np.ndarray,
    boundaries: tuple[np.ndarray, np.ndarray, MPI.Request, MPI.Request],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute the slope of the LLG equation

    Args:
        g: Grid object
        e: Element object
        m: Magnetization array (shape (3, nx, ny, nz))
        R_random: Random field array (shape (3, nx, ny, nz))
        boundaries: Boundaries for x direction

    Returns:
        Slope array (shape (3, nx, ny, nz))
    """

    # Precalculate terms used multiple times

    H_aniso = compute_H_anisotropy(e, m)

    laplacian_m = compute_laplacian(g, m, boundaries)
    R_eff = e.coeff_1 * laplacian_m + R_random + H_aniso
    R_eff[0] += e.coeff_3

    m_cross_R_eff = cross_product(m, R_eff)
    m_cross_m_cross_R_eff = cross_product(m, m_cross_R_eff)

    s = -(m_cross_R_eff + e.lambda_G * m_cross_m_cross_R_eff)

    return s


def space_average(g: Grid, m: np.ndarray) -> float:
    """
    Returns the spatial average of m with shape (g.dims)
    using the midpoint method.
    Performs the local sum on each process and then reduces it to process 0.

    Args:
        g: Grid object
        m: Array to be integrated (shape (x, y, z))

    Returns:
        Spatial average of m
    """

    # Make a copy of m to avoid modifying its value
    mm = m.copy()

    # On y and z edges, divide the contribution by 2
    mm[:, 0, :] /= 2
    mm[:, -1, :] /= 2
    mm[:, :, 0] /= 2
    mm[:, :, -1] /= 2

    # On x edges (only on extreme procs), divide the contribution by 2
    if rank == 0:
        mm[0] /= 2
    if rank == size - 1:
        mm[-1] /= 2
    local_sum = mm.sum()

    # Sum across all processes gathered by process 0
    global_sum = comm.reduce(local_sum)

    # Spatial average is the global sum divided by the number of cells
    return global_sum / g.ncell if rank == 0 else 0.0


def integral_yz(m: np.ndarray) -> np.ndarray:
    """
    Returns the spatial average of shape (g.dims[0],)
    in y and z of m of shape (g.dims) using the midpoint method

    Args:
        m: Array to be integrated

    Returns:
        np.ndarray: Spatial average of m in y and z
    """

    # Make a copy of m to avoid modifying its value
    mm = m.copy()

    # On y and z edges, divide the contribution by 2
    mm[:, 0, :] /= 2
    mm[:, -1, :] /= 2
    mm[:, :, 0] /= 2
    mm[:, :, -1] /= 2

    n_cell_yz = (mm.shape[1] - 1) * (mm.shape[2] - 1)
    return mm.sum(axis=(1, 2)) / n_cell_yz


def profile(m: np.ndarray, m_xprof: np.ndarray):
    """
    Retrieves the x profile of the average of m in y and z

    Args:
        m: Array to be integrated
        m_xprof: Array to store the x profile
    """

    # Gather m in mglob
    m_mean_yz = integral_yz(m)
    comm.Gather(m_mean_yz, m_xprof)


def theta_init(t: float, g: Grid) -> np.ndarray:
    """Initialization of theta"""
    x, y, z = g.get_mesh(local=True)
    return np.zeros(g.dims)


def phi_init(t: float, g: Grid, e: Element) -> np.ndarray:
    """Initialization of phi"""
    # return np.zeros(shape) + e.coeff_3 * t
    return np.zeros(g.dims) + e.gamma_0 * e.H_ext * t


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
    seed: int,
    blocking: bool,
    **_,
) -> tuple[float, str, float]:
    """
    Simulates the system for N iterations

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
        blocking: Whether to use blocking communication for boundaries
        seed: Random seed for temperature fluctuations

    Returns:
        - The grid object
        - The time taken for the simulation
        - The output filename
    """

    if Jx % size != 0:
        if rank == 0:
            print(
                f"Error: Jx must be divisible by the number of processes"
                f"({Jx = }, np = {size})"
            )
        comm.barrier()
        MPI.Finalize()
        exit(2)

    # Initialize a sequence of random seeds
    # See: https://numpy.org/doc/stable/reference/random/parallel.html
    ss = np.random.SeedSequence(seed)

    # Deploy size x SeedSequence to pass to child processes
    child_seeds = ss.spawn(size)
    streams = [np.random.default_rng(s) for s in child_seeds]
    rng = streams[rank]

    # Create the grid
    g = Grid(Jx, Jy, Jz, dx)

    if rank == 0:
        print(g)

    e = element_class(T, H_ext, g, dt)
    if rank == 0:
        print(f"CFL = {e.get_CFL()}")

    m_n = np.zeros((3,) + g.dims)

    theta = theta_init(0, g)
    phi = phi_init(0, g, e)

    m_n[0] = np.cos(theta)
    m_n[1] = np.sin(theta) * np.cos(phi)
    m_n[2] = np.sin(theta) * np.sin(phi)

    m_xprof = np.zeros(g.Jx)  # global coordinates

    f_mean, f_profiles, output_filenames = get_output_files(g, T, n_mean, n_profile)

    t = 0.0
    m1_average = 0.0

    start_time = time.perf_counter()

    for n in progress_bar(range(1, N + 1), "Iteration: ", 40):
        t += dt

        # Prediction phase
        x_boundaries = [
            get_boundaries_x(g, m_n[i], blocking=blocking) for i in range(3)
        ]

        # adding randomness: effect of temperature
        R_random = e.coeff_4 * rng.standard_normal((3, *g.dims))

        s_pre = compute_slope(e, g, m_n, R_random, x_boundaries)
        m_pre = m_n + dt * s_pre

        # correction phase
        x_boundaries = [
            get_boundaries_x(g, m_pre[i], blocking=blocking) for i in range(3)
        ]

        s_cor = compute_slope(e, g, m_pre, R_random, x_boundaries)
        m_n += dt * 0.5 * (s_pre + s_cor)

        # renormalize to verify the constraint of being on the sphere
        norm = np.sqrt(m_n[0] ** 2 + m_n[1] ** 2 + m_n[2] ** 2)
        m_n /= norm

        # Export the average of m1 to a file
        if n_mean != 0 and n % n_mean == 0:
            m1_mean = space_average(g, m_n[0])
            if rank == 0:
                if n >= start_averaging:
                    m1_average += m1_mean * n_mean
                f_mean.write(f"{t:10.8e} {m1_mean:10.8e}\n")
        # Export the x profiles of the averaged m_i in y and z
        if n_profile != 0 and n % n_profile == 0:
            for i in 0, 1, 2:
                profile(m_n[i], m_xprof)
                if rank == 0:
                    # add an x profile to the file
                    np.save(f_profiles[i], m_xprof)

    total_time = time.perf_counter() - start_time

    if rank == 0:
        close_output_files(f_mean, f_profiles)

        if n > start_averaging:
            m1_average /= N - start_averaging

    return total_time, output_filenames, m1_average


class ArgumentParser(argparse.ArgumentParser):
    """An argument parser compatible with MPI"""

    def _print_message(self, message, file=None):
        if rank == 0 and message:
            if file is None:
                file = sys.stderr
            file.write(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        comm.barrier()
        MPI.Finalize()
        exit(status)
