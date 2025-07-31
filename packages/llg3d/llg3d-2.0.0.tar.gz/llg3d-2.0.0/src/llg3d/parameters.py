"""Parameters for the LLG3D simulation."""

import numpy as np

# Parameters: default value and description
Parameter = dict[str, str | int | float | bool]  #: Type for a parameter

parameters: dict[str, Parameter] = {
    "element": {
        "help": "Chemical element of the sample",
        "default": "Cobalt",
        "choices": ["Cobalt", "Iron", "Nickel"],
    },
    "N": {"help": "Number of time iterations", "default": 5000},
    "dt": {"help": "Time step", "default": 1.0e-14},
    "Jx": {"help": "Number of points in x", "default": 300},
    "Jy": {"help": "Number of points in y", "default": 21},
    "Jz": {"help": "Number of points in z", "default": 21},
    "dx": {"help": "Step in x", "default": 1.0e-9},
    "T": {"help": "Temperature (K)", "default": 0.0},
    "H_ext": {"help": "External field (A/m)", "default": 0.0 / (4 * np.pi * 1.0e-7)},
    "start_averaging": {"help": "Start index of time average", "default": 4000},
    "n_mean": {
        "help": "Spatial average frequency (number of iterations)",
        "default": 1,
    },
    "n_profile": {
        "help": "x-profile save frequency (number of iterations)",
        "default": 0,
    },
    "solver": {
        "help": "Solver to use for the simulation",
        "default": "numpy",
        "choices": ["opencl", "mpi", "numpy", "jax"],
    },
    "precision": {
        "help": "Precision of the simulation (single or double)",
        "default": "double",
        "choices": ["single", "double"],
    },
    "blocking": {
        "help": "Use blocking communications",
        "default": False,
        "action": "store_true",
    },
    "seed": {
        "help": "Random seed for temperature fluctuations",
        "default": 12345,
        "type": int,
    },
    "device": {
        "help": "Device to use ('cpu', 'gpu', or 'auto')",
        "default": "auto",
        "type": str,
    },
}  #: simulation parameters


def get_parameter_list(parameters: dict) -> str:
    """
    Returns parameter values as a string

    Args:
        d: Dictionary of parameters parsed by argparse

    Returns:
        str: Formatted string of parameters
    """
    width = max([len(name) for name in parameters])
    s = ""
    for name, value in parameters.items():
        # the seprator is ":" for strings and "=" for others
        sep = ":" if isinstance(value, str) else "="
        s += "{0:<{1}} {2} {3}\n".format(name, width, sep, value)
    return s
