"""
Solver module for LLG3D

This module contains different solver implementations.
"""

import importlib.util


__all__ = ["numpy", "solver", "rank", "size", "comm", "status"]

LIB_AVAILABLE: dict[str, bool] = {}

# Check for other solver availability
for lib in "opencl", "jax", "mpi4py":
    if importlib.util.find_spec(lib, package=__package__) is not None:
        LIB_AVAILABLE[lib] = True
        __all__.append(lib)
    else:
        LIB_AVAILABLE[lib] = False


# MPI utilities
if LIB_AVAILABLE["mpi4py"]:
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    status = MPI.Status()
else:
    # MPI library is not available: use dummy values
    class DummyComm:
        pass

    comm = DummyComm()
    rank = 0
    size = 1

    class DummyStatus:
        pass

    status = DummyStatus()

from . import numpy, solver
