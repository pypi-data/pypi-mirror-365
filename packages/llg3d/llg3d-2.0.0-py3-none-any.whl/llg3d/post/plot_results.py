"""
Plot 1D curves from several files

Usage:

python plot_results.py file1.txt
or
python plot_results.py file1.txt file2.txt file3.txt

"""

import argparse
from matplotlib import pyplot as plt
import numpy as np


DEFAULT_OUTPUT_FILE = "results.png"


def plot(*files: tuple[str], output_file: str = DEFAULT_OUTPUT_FILE):
    """
    Plot the results from the given files.

    Args:
        files (tuple[str]): Paths to the result files.
        output_file (str): Path to the output image file.
    """

    fig, ax = plt.subplots()
    for file in files:
        if not file.endswith(".txt"):
            raise ValueError(f"File {file} does not end with .txt")
        data = np.loadtxt(file)
        ax.plot(data[:, 0], data[:, 1], label=file)

    ax.set_xlabel("time")
    ax.set_ylabel(r"$<m_1>$")
    ax.legend()
    ax.set_title(r"Space average of $m_1$ according to time")
    fig.savefig(output_file)
    print(f"Written to {output_file}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot results from one or more files."
    )
    parser.add_argument(
        "files", nargs="+", type=str, help="Path to the result files."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Path to the output image file (default: {DEFAULT_OUTPUT_FILE}).",
    )
    args = parser.parse_args()

    plot(*args.files, output_file=args.output)


if __name__ == "__main__":
    main()
