"""
Module to define the grid for the simulation
"""

from dataclasses import dataclass
import numpy as np

from .solver import rank, size


@dataclass
class Grid:
    """Stores grid data"""

    # Parameter values correspond to the global grid
    Jx: int  #: number of points in x direction
    Jy: int  #: number of points in y direction
    Jz: int  #: number of points in z direction
    dx: float  #: grid spacing in x direction

    def __post_init__(self) -> None:
        """Compute grid characteristics"""
        self.dy = self.dz = self.dx  # Setting dx = dy = dz
        self.Lx = (self.Jx - 1) * self.dx
        self.Ly = (self.Jy - 1) * self.dy
        self.Lz = (self.Jz - 1) * self.dz
        # shape of the local array to the process
        self.dims = self.Jx // size, self.Jy, self.Jz
        # elemental volume of a cell
        self.dV = self.dx * self.dy * self.dz
        # total volume
        self.V = self.Lx * self.Ly * self.Lz
        # total number of points
        self.ntot = self.Jx * self.Jy * self.Jz
        self.ncell = (self.Jx - 1) * (self.Jy - 1) * (self.Jz - 1)

    def __str__(self) -> str:
        """Print grid information"""

        header = "\t\t".join(("x", "y", "z"))
        s = f"""\
\t{header}
J\t{self.Jx}\t\t{self.Jy}\t\t{self.Jz}
L\t{self.Lx:.08e}\t{self.Ly:.08e}\t{self.Lz:.08e}
d\t{self.dx:.08e}\t{self.dy:.08e}\t{self.dz:.08e}

dV    = {self.dV:.08e}
V     = {self.V:.08e}
ntot  = {self.ntot:d}
ncell = {self.ncell:d}
"""
        return s

    def get_filename(
        self, T: float, name: str = "m1_mean", extension: str = "txt"
    ) -> str:
        """
        Returns the output file name for a given temperature

        Args:
            T: temperature
            name: file name
            extension: file extension

        Returns:
            file name

        >>> g = Grid(Jx=300, Jy=21, Jz=21, dx=1.e-9)
        >>> g.get_filename(1100)
        'm1_mean_T1100_300x21x21.txt'
        """
        suffix = f"T{int(T)}_{self.Jx}x{self.Jy}x{self.Jz}"
        return f"{name}_{suffix}.{extension}"

    def get_mesh(
        self, local: bool = True, dtype=np.float64
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns a meshgrid of the coordinates.

        Args:
            local: if True, returns the local coordinates,
                   otherwise the global coordinates
            dtype: data type of the coordinates)

        Returns:
            tuple of 3D arrays with the coordinates
        """
        x_global = np.linspace(0, self.Lx, self.Jx, dtype=dtype)  # global coordinates
        y = np.linspace(0, self.Ly, self.Jy, dtype=dtype)
        z = np.linspace(0, self.Lz, self.Jz, dtype=dtype)
        if local:
            x_local = np.split(x_global, size)[rank]  # local coordinates
            return np.meshgrid(x_local, y, z, indexing="ij")
        else:
            return np.meshgrid(x_global, y, z, indexing="ij")

    def to_dict(self) -> dict:
        """
        Export grid parameters to a dictionary for JAX JIT compatibility

        Returns:
            Dictionary containing grid parameters needed for computations
        """
        return {
            "dx": self.dx,
            "dy": self.dy,
            "dz": self.dz,
            "Jx": self.Jx,
            "Jy": self.Jy,
            "Jz": self.Jz,
            "dV": self.dV,
        }

    def get_laplacian_coeff(self) -> tuple[float, float, float, float]:
        """
        Returns the coefficients for the laplacian computation

        Returns:
            Tuple of coefficients (dx2_inv, dy2_inv, dz2_inv, center_coeff)
        """
        dx2_inv = 1 / self.dx**2
        dy2_inv = 1 / self.dy**2
        dz2_inv = 1 / self.dz**2
        center_coeff = -2 * (dx2_inv + dy2_inv + dz2_inv)
        return dx2_inv, dy2_inv, dz2_inv, center_coeff
