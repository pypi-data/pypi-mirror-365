"""
For parallel tests, it is preferable to use a number of processes that is a divisor of 60 (2, 3, 6, etc.).
"""

from llg3d import size
from llg3d.grid import Grid


def test_Grid():
    g = Grid(Jx=301, Jy=11, Jz=21, dx=2.0)

    assert g.dx == 2.0
    assert g.dy == 2.0
    assert g.dz == 2.0
    assert g.dV == 8.0
    assert g.V == 480000.0
    assert g.ntot == 301 * 11 * 21
    assert g.get_filename(1234) == "m1_mean_T1234_301x11x21.txt"


def test_get_mesh():
    g = Grid(Jx=3 * size, Jy=3, Jz=3, dx=1.0)
    x, y, z = g.get_mesh(local=True)
    assert x.shape == (3, 3, 3)
    assert y.shape == (3, 3, 3)
    assert z.shape == (3, 3, 3)
    xg, yg, zg = g.get_mesh(local=False)
    assert xg.shape == (3 * size, 3, 3)
    assert yg.shape == (3 * size, 3, 3)
    assert zg.shape == (3 * size, 3, 3)


def test_grid_to_dict():
    g = Grid(Jx=301, Jy=11, Jz=21, dx=2.0)
    d = g.to_dict()

    assert d["Jx"] == 301
    assert d["Jy"] == 11
    assert d["Jz"] == 21
    assert d["dx"] == 2.0
    assert d["dy"] == 2.0
    assert d["dz"] == 2.0
    assert d["dV"] == 8.0


def test_get_laplacian_coeff():
    g = Grid(Jx=301, Jy=11, Jz=21, dx=2.0)

    dx2_inv, dy2_inv, dz2_inv, center_coeff = g.get_laplacian_coeff()

    assert dx2_inv == 0.25
    assert dy2_inv == 0.25
    assert dz2_inv == 0.25
    assert center_coeff == -1.5

    g = Grid(Jx=3 * size, Jy=3, Jz=3, dx=1.0)
    dx2_inv, dy2_inv, dz2_inv, center_coeff = g.get_laplacian_coeff()

    assert dx2_inv == 1.0
    assert dy2_inv == 1.0
    assert dz2_inv == 1.0
    assert center_coeff == -6.0
