r"""
Module containing the definition of the chemical elements
"""

import numpy as np

from .grid import Grid

k_B = 1.38e-23  #: Boltzmann constant :math:`[J.K^{-1}]`
mu_0 = 4 * np.pi * 1.0e-7  #: Vacuum permeability :math:`[H.m^{-1}]`
gamma = 1.76e11  #: Gyromagnetic ratio :math:`[rad.s^{-1}.T^{-1}]`


class Element:
    """Abstract class for chemical elements"""

    A = 0.0
    K = 0.0
    lambda_G = 0.0
    M_s = 0.0
    a_eff = 0.0
    anisotropy: str = ""

    def __init__(self, T: float, H_ext: float, g: Grid, dt: float) -> None:
        """Initializes the Element class with given parameters

        Args:
            T: Temperature in Kelvin
            H_ext: External magnetic field strength
            g: Grid object representing the simulation grid
            dt: Time step for the simulation
        """
        self.H_ext = H_ext
        self.g = g
        self.dt = dt
        self.gamma_0 = gamma * mu_0  #: Rescaled gyromagnetic ratio [mA^-1.s^-1]

        # --- Characteristic Scales ---
        self.coeff_1 = self.gamma_0 * 2.0 * self.A / (mu_0 * self.M_s)
        self.coeff_2 = self.gamma_0 * 2.0 * self.K / (mu_0 * self.M_s)
        self.coeff_3 = self.gamma_0 * H_ext

        # corresponds to the temperature actually put into the random field
        T_simu = T * self.g.dx / self.a_eff
        # calculation of the random field related to temperature
        # (we only take the volume over one mesh)
        h_alea = np.sqrt(
            2 * self.lambda_G * k_B / (self.gamma_0 * mu_0 * self.M_s * self.g.dV)
        )
        H_alea = h_alea * np.sqrt(T_simu) * np.sqrt(1.0 / self.dt)
        self.coeff_4 = H_alea * self.gamma_0

    def get_CFL(self) -> float:
        """
        Returns the value of the CFL

        Returns:
            float: The CFL value
        """
        return self.dt * self.coeff_1 / self.g.dx**2

    def to_dict(self) -> dict:
        """
        Export element parameters to a dictionary for JAX JIT compatibility

        Returns:
            Dictionary containing element parameters needed for computations
        """
        # Map anisotropy string to integer for JIT compatibility
        aniso_map = {"uniaxial": 0, "cubic": 1}

        return {
            "coeff_1": self.coeff_1,
            "coeff_2": self.coeff_2,
            "coeff_3": self.coeff_3,
            "coeff_4": self.coeff_4,
            "lambda_G": self.lambda_G,
            "anisotropy": aniso_map[self.anisotropy],
            "gamma_0": self.gamma_0,
        }


class Cobalt(Element):
    A = 30.0e-12  #: Exchange constant :math:`[J.m^{-1}]`
    K = 520.0e3  #: Anisotropy constant :math:`[J.m^{-3}]`
    lambda_G = 0.5  #: Damping parameter :math:`[1]`
    M_s = 1400.0e3  #: Saturation magnetization :math:`[A.m^{-1}]`
    a_eff = 0.25e-9  #: Effective lattice constant :math:`[m]`
    anisotropy = "uniaxial"  #: Type of anisotropy (e.g., "uniaxial", "cubic")


class Iron(Element):
    A = 21.0e-12  #: Exchange constant :math:`[J.m^{-1}]`
    K = 48.0e3  #: Anisotropy constant :math:`[J.m^{-3}]`
    lambda_G = 0.5  #: Damping parameter :math:`[1]`
    M_s = 1700.0e3  #: Saturation magnetization :math:`[A.m^{-1}]`
    a_eff = 0.286e-9  #: Effective lattice constant :math:`[m]`
    anisotropy = "cubic"  #: Type of anisotropy (e.g., "uniaxial", "cubic")


class Nickel(Element):
    A = 9.0e-12  #: Exchange constant :math:`[J.m^{-1}]`
    K = -5.7e3  #: Anisotropy constant :math:`[J.m^{-3}]`
    lambda_G = 0.5  #: Damping parameter :math:`[1]`
    M_s = 490.0e3  #: Saturation magnetization :math:`[A.m^{-1}]`
    a_eff = 0.345e-9  #: Effective lattice constant :math:`[m]`
    anisotropy = "cubic"  #: Type of anisotropy (e.g., "uniaxial", "cubic")


def get_element_class(element_name: str | type[Element]) -> type[Element]:
    """
    Get the class of the chemical element by its name.

    Args:
        element_name: The name of the element or its class

    Returns:
        The class of the element

    Raises:
        ValueError: If the element is not found
    """
    if isinstance(element_name, type):
        return element_name
    for cls in Element.__subclasses__():
        if cls.__name__ == element_name:
            return cls
    raise ValueError(f"Element '{element_name}' not found in {__file__}.")
