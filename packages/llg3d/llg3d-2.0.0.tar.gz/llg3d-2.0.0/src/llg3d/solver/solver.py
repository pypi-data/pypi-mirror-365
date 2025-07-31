"""
Common functions for the LLG3D solver
"""

import numpy as np

from ..grid import Grid
from ..element import Element


def cross_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    r"""
    Compute cross product :math:`a \times b`.

    This implementation is faster than np.cross for large arrays.

    Args:
        a: First vector (shape (3, nx, ny, nz))
        b: Second vector (shape (3, nx, ny, nz))

    Returns:
        Cross product :math:`a \times b` (shape (3, nx, ny, nz))
    """

    return np.stack(
        [
            a[1] * b[2] - a[2] * b[1],  # x-component
            a[2] * b[0] - a[0] * b[2],  # y-component
            a[0] * b[1] - a[1] * b[0],  # z-component
        ],
        axis=0,
    )


def compute_H_anisotropy(e: Element, m: np.ndarray) -> np.ndarray:
    """
    Compute the anisotropy field
    Args:
        e: Element object
        m: Magnetization array (shape (3, nx, ny, nz))
    Returns:
        Anisotropy field array (shape (3, nx, ny, nz))
    """

    m1, m2, m3 = m

    m1m1 = m1 * m1
    m2m2 = m2 * m2
    m3m3 = m3 * m3

    if e.anisotropy == "uniaxial":
        aniso_1 = m1
        aniso_2 = np.zeros_like(m1)
        aniso_3 = np.zeros_like(m1)

    if e.anisotropy == "cubic":
        aniso_1 = -(1 - m1m1 + m2m2 * m3m3) * m1
        aniso_2 = -(1 - m2m2 + m1m1 * m3m3) * m2
        aniso_3 = -(1 - m3m3 + m1m1 * m2m2) * m3

    return e.coeff_2 * np.stack([aniso_1, aniso_2, aniso_3], axis=0)


def space_average(g: Grid, m: np.ndarray, copy: bool = True) -> float:
    """
    Returns the spatial average of m with shape (g.dims)
    using the midpoint method

    Args:
        g: Grid object
        m: Array to be integrated
        copy: If True, copy m to avoid modifying its value

    Returns:
        float: Spatial average of m
    """

    # copy m to avoid modifying its value
    mm = m.copy() if copy else m

    # on the edges, we divide the contribution by 2
    # x
    mm[0, :, :] /= 2
    mm[-1, :, :] /= 2
    # y
    mm[:, 0, :] /= 2
    mm[:, -1, :] /= 2
    # z
    mm[:, :, 0] /= 2
    mm[:, :, -1] /= 2

    average = mm.sum() / g.ncell
    return average
