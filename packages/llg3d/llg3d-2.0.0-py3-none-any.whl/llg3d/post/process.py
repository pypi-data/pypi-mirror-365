#!/usr/bin/env python3
"""
Post-processes a set of runs grouped into a `run.json` file or
into a set of SLURM job arrays:

1. Extracts result data,
2. Plots the computed average magnetization against temperature,
3. Interpolates the computed points using cubic splines,
4. Determines the Curie temperature as the value corresponding to the minimal (negative) slope of the interpolated curve.
"""

import json
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d


class MagData:
    """
    Class to handle magnetization data and interpolation according to temperature
    """

    n_interp = 200

    def __init__(self, job_dir: Path = None, run_file: Path = Path("run.json")) -> None:

        if job_dir:
            self.parentpath = job_dir
            data, self.run = self.process_slurm_jobs()
        elif run_file:
            self.parentpath = run_file.parent
            data, self.run = self.process_json(run_file)

        self.temperature = data[:, 0]
        self.m1_mean = data[:, 1]
        self.interp = interp1d(self.temperature, self.m1_mean, kind="cubic")
        self.T = np.linspace(
            self.temperature.min(), self.temperature.max(), self.n_interp
        )

    def process_slurm_jobs(self) -> tuple[np.array, dict]:
        """
        Iterates through calculation directories to assemble data.

        Args:
            parentdir (str): path to the directory containing the runs

        Returns:
            tuple: (data, run) where data is a numpy array (T, <m>) and run
            is a descriptive dictionary of the run
        """
        json_filename = "run.json"

        # List of run directories
        jobdirs = [f for f in self.parentpath.iterdir() if f.is_dir()]
        if len(jobdirs) == 0:
            exit(f"No job directories found in {self.parentpath}")
        data = []
        # Iterating through run directories
        for jobdir in jobdirs:
            try:
                # Reading the JSON file
                with open(jobdir / json_filename) as f:
                    run = json.load(f)
                    # Adding temperature and averaging value to the data list
                    data.extend(
                        [[float(T), res["m1_mean"]] for T, res in run["results"].items()]
                    )
            except FileNotFoundError:
                print(f"Warning: {json_filename} file not found " f"in {jobdir.as_posix()}")

        data.sort()  # Sorting by increasing temperatures

        return np.array(data), run


    def process_json(json_filepath: Path) -> tuple[np.array, dict]:
        """
        Reads the run.json file and extracts result data.

        Args:
            json_filepath: path to the run.json file

        Returns:
            tuple: (data, run) where data is a numpy array (T, <m>) and run
            is a descriptive dictionary of the run
        """
        with open(json_filepath) as f:
            run = json.load(f)

        data = [[int(T), res["m1_mean"]] for T, res in run["results"].items()]

        data.sort()  # Sorting by increasing temperatures

        return np.array(data), run

    @property
    def T_Curie(self) -> float:
        """
        Return the Curie temperature defined as the temperature at
        which the magnetization is below 0.1
        """
        i_max = np.where(0.1 - self.interp(self.T) > 0)[0].min()
        return self.T[i_max]