import pytest

from llg3d import size, LIB_AVAILABLE
from llg3d import main

cli_args_set = (["--N", "100", "--element", "Cobalt"], ["--N", "10", "--element", "Iron"])


def test_parse_args():
    args = main.parse_args(["--N", "100"])
    assert args.N == 100


@pytest.mark.parametrize("cli_args", cli_args_set)
@pytest.mark.xfail(not LIB_AVAILABLE["mpi4py"], reason="mpi4py is not installed")
def test_main_mpi(run_args, cli_args):
    cli_args.extend(["--solver", "mpi"])
    main.main(cli_args)


@pytest.mark.parametrize("cli_args", cli_args_set)
@pytest.mark.xfail(size > 1, reason="Serial version is not supported with MPI")
def test_main_numpy(run_args, cli_args):
    cli_args.extend(["--solver", "numpy"])
    main.main(cli_args)


@pytest.mark.parametrize(
    "cli_args",
    [
        cli_args_set[0],
        pytest.param(
            cli_args_set[1],
            marks=pytest.mark.skipif(
                "Iron" in cli_args_set[1], reason="Only Cobalt is supported with OpenCL"
            ),
        ),
    ],
)
@pytest.mark.xfail(size > 1, reason="OpenCL version is not supported with MPI")
def test_main_opencl(run_args, cli_args):
    cli_args.extend(["--solver", "opencl", "--precision", "single"])
    main.main(cli_args)


@pytest.mark.parametrize("cli_args", cli_args_set)
@pytest.mark.xfail(not LIB_AVAILABLE["jax"], reason="jax is not installed")
def test_main_jax(run_args, cli_args):
    cli_args.extend(["--solver", "jax"])
    main.main(cli_args)
