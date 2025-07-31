"""
Define a CLI for the llg3d package.
"""

import argparse


from . import rank, size, LIB_AVAILABLE
from .parameters import parameters, get_parameter_list
from .simulation import Simulation

if LIB_AVAILABLE["mpi4py"]:
    # Use the MPI version of the ArgumentParser
    from .solver.mpi import ArgumentParser
else:
    # Use the original version of the ArgumentParser
    from argparse import ArgumentParser


def parse_args(args: list[str] | None) -> argparse.Namespace:
    """
    Argument parser for llg3d.
    Automatically adds arguments from the parameter dictionary.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    if size > 1:
        parameters["solver"]["default"] = "mpi"

    # Automatically add arguments from the parameter dictionary
    for name, parameter in parameters.items():
        if "action" not in parameter:
            parameter["type"] = type(parameter["default"])
        parser.add_argument(f"--{name}", **parameter)

    return parser.parse_args(args)


def main(arg_list: list[str] = None):
    """
    Evaluates the command line and runs the simulation
    """

    args = parse_args(arg_list)

    if size > 1 and args.solver != "mpi":
        raise ValueError(f"Solver method {args.solver} is not compatible with MPI.")
    if args.solver == "mpi" and not LIB_AVAILABLE["mpi4py"]:
        raise ValueError(
            "The MPI solver method requires to install the mpi4py package, "
            "for example using pip: pip install mpi4py"
        )

    if rank == 0:
        # Display parameters as a list
        print(get_parameter_list(vars(args)))

    simulation = Simulation(vars(args))
    simulation.run()
    simulation.save()
