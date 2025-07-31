from llg3d.parameters import get_parameter_list


def test_parameter_list():
    d = {
        "element": "Cobalt",
        "blocking": False,
        "N": 500,
        "dt": 1e-14,
        "Jx": 300,
        "Jy": 21,
        "Jz": 21,
        "Lx": 3e-07,
        "Ly": 2e-08,
        "Lz": 2e-08,
        "T": 1100,
        "H_ext": 0.0,
        "start_averaging": 2000,
        "n_mean": 1,
        "n_profile": 100,
    }
    expected = """\
element         : Cobalt
blocking        = False
N               = 500
dt              = 1e-14
Jx              = 300
Jy              = 21
Jz              = 21
Lx              = 3e-07
Ly              = 2e-08
Lz              = 2e-08
T               = 1100
H_ext           = 0.0
start_averaging = 2000
n_mean          = 1
n_profile       = 100
"""
    assert get_parameter_list(d) == expected
