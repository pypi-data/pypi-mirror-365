"""
Utility functions for LLG3D
"""

import json
import sys
from typing import Iterable, TextIO

from .solver import rank
from .grid import Grid


def progress_bar(it: Iterable, prefix: str = "", size: int = 60, out: TextIO = sys.stdout):
    """
    Displays a progress bar

    (Source: https://stackoverflow.com/a/34482761/16593179)

    Args:
        it: Iterable object to iterate over
        prefix: Prefix string for the progress bar
        size: Size of the progress bar (number of characters)
        out: Output stream (default is sys.stdout)
    """

    count = len(it)

    def show(j):
        x = int(size * j / count)
        if rank == 0:
            print(
                f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}",
                end="\r",
                file=out,
                flush=True,
            )

    show(0)
    for i, item in enumerate(it):
        yield item
        # To avoid slowing down the computation, we do not display at every iteration
        if i % 5 == 0:
            show(i + 1)
    show(i + 1)
    if rank == 0:
        print("\n", flush=True, file=out)


def write_json(json_file: str, run: dict):
    """
    Writes the run dictionary to a JSON file

    Args:
        json_file: Name of the JSON file
        run: Dictionary containing the run information
    """
    with open(json_file, "w") as f:
        json.dump(run, f, indent=4)


def get_output_files(g: Grid, T: float, n_mean: int, n_profile: int) -> tuple:
    """
    Open files and list them

    Args:
        g: Grid object
        T: temperature
        n_mean: Number of iterations for integral output
        n_profile: Number of iterations for profile output

    Returns:
        - a file handler for storing m space integral over time
        - a file handler for storing x-profiles of m_i
        - a list of output filenames
    """
    f_mean = None
    f_profiles = None
    output_filenames = []
    if n_mean != 0:
        output_filenames.append(g.get_filename(T, extension="txt"))
    if n_profile != 0:
        output_filenames.extend(
            [g.get_filename(T, name=f"m{i + 1}", extension="npy") for i in range(3)]
        )
    if rank == 0:
        if n_mean != 0:
            f_mean = open(output_filenames[0], "w")  # integral of m1
        if n_profile != 0:
            f_profiles = [
                open(output_filename, "wb") for output_filename in output_filenames[1:]
            ]  # x profiles of m_i

    return f_mean, f_profiles, output_filenames


def close_output_files(f_mean: TextIO, f_profiles: list[TextIO] = None):
    """
    Close all output files

    Args:
        f_mean: file handler for storing m space integral over time
        f_profiles: file handlers for storing x-profiles of m_i
    """
    if f_mean is not None:
        f_mean.close()
    if f_profiles is not None:
        for f_profile in f_profiles:
            f_profile.close()
