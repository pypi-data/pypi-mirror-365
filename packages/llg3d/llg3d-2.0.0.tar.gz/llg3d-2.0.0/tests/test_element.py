import pytest

from llg3d import element

T = 1100
H_ext = 0.0
g = element.Grid(10, 10, 10, 1e-9)
dt = 1e-12


def test_Colbalt():

    cobalt = element.Cobalt(T, H_ext, g, dt)
    assert cobalt.A == 30.0e-12
    assert cobalt.K == 520.0e3
    assert cobalt.gamma_0 == element.gamma * element.mu_0
    assert cobalt.lambda_G == 0.5
    assert cobalt.M_s == 1400.0e3
    assert cobalt.a_eff == 0.25e-9
    assert cobalt.anisotropy == "uniaxial"


def test_element_to_dict():
    """Test that element parameters can be converted to a dictionary"""

    iron = element.Iron(T, H_ext, g, dt)

    assert iron.to_dict() == {
        "coeff_1": iron.coeff_1,
        "coeff_2": iron.coeff_2,
        "coeff_3": iron.coeff_3,
        "coeff_4": iron.coeff_4,
        "lambda_G": iron.lambda_G,
        "anisotropy": 1,  # Cubic is mapped to 1
        "gamma_0": iron.gamma_0,
    }


def test_get_element_class():
    """Test that the correct element class is returned"""

    cobalt_class = element.get_element_class("Cobalt")
    assert cobalt_class == element.Cobalt

    iron_class = element.get_element_class("Iron")
    assert iron_class == element.Iron

    nickel_class = element.get_element_class("Nickel")
    assert nickel_class == element.Nickel

    # Test with an invalid name
    with pytest.raises(ValueError):
        element.get_element_class("UnknownElement")