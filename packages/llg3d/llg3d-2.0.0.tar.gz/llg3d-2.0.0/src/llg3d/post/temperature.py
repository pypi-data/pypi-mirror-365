#!/usr/bin/env python3
"""
Plot the magnetization vs temperature and determine the Curie temperature.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from .process import MagData


def plot_m_vs_T(m: MagData, show: bool):
    """
    Plots the data (T, <m>), interpolates the values,
    calculates the Curie temperature.
    Exports to PNG.

    Args:
        data: numpy array (T, <m>)
        parentdir: path to the directory containing the runs
        run: descriptive dictionary of the run
        show: display the graph in a graphical window
    """

    print(f"T_Curie = {m.T_Curie:.0f} K")

    fig, ax = plt.subplots()
    fig.suptitle("Average magnetization vs Temperature")
    params = m.run["params"]
    ax.set_title(
        params["element"]
        + rf", ${params['Jx']}\times{params['Jy']}\times{params['Jz']}$"
        rf" ($dx = ${params['dx']})",
        fontdict={"size": 10},
    )
    ax.plot(m.temperature, m.m1_mean, "o", label="computed")
    ax.plot(m.T, m.interp(m.T), label="interpolated (cubic)")
    ax.annotate(
        "$T_{{Curie}} = {:.0f} K$".format(m.T_Curie),
        xy=(m.T_Curie, m.interp(m.T_Curie)),
        xytext=(m.T_Curie + 20, m.interp(m.T_Curie) + 0.01),
    )
    ax.axvline(x=m.T_Curie, color="k")
    ax.set_xlabel("Temperature [K]")
    ax.set_ylabel("Magnetization")
    ax.legend()

    if show:
        plt.show()

    image_filename = m.parentpath / "m1_mean.png"
    fig.savefig(image_filename)
    print(f"Image saved in {image_filename}")


def main():
    """
    Parses the command line to execute processing functions
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job_dir", type=Path, help="Slurm main job directory")
    parser.add_argument(
        "--run_file", type=Path, default="run.json", help="Path to the run.json file"
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        default=False,
        help="Display the graph in a graphical window",
    )
    args = parser.parse_args()
    if args.job_dir:
        m = MagData(job_dir=args.job_dir)
    else:
        m = MagData(run_file=args.run_file)
    plot_m_vs_T(m, args.show)


if __name__ == "__main__":
    main()
