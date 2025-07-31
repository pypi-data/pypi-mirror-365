"""
Define the Simulation class.

Example usage:

    >>> from llg3d.main import Simulation
    >>> from llg3d.parameters import parameters
    >>> run_parameters = {name: value["default"] for name, value in parameters.items()}
    >>> sim = Simulation(run_parameters)
    >>> sim.run()
    >>> sim.save()

"""

import inspect

from . import rank, size
from .element import get_element_class
from .parameters import Parameter
from .output import write_json


class Simulation:
    """
    Class to encapsulate the simulation logic.
    """

    json_file = "run.json"  #: JSON file to store the results

    def __init__(self, params: dict[str, Parameter]):
        """
        Initializes the simulation with parameters.

        Args:
            params: Dictionary of simulation parameters.
        """
        self.params: dict[str, Parameter] = params.copy()  #: simulation parameters
        self.simulate: callable = self._get_simulate_function_from_name(
            self.params["solver"]
        )  #: simulation function imported from the solver module
        self.total_time: None | float = None  #: total simulation time
        self.filenames: list[str] = []  #: list of output filenames
        self.m1_mean: None | float = None  #: space and time average of m1
        self.params["np"] = size  # Add a parameter for the number of processes
        # Reference the element class from the element string
        self.params["element_class"] = get_element_class(params["element"])

    def run(self):
        """
        Runs the simulation and store the results.
        """
        self.total_time, self.filenames, self.m1_mean = self.simulate(**self.params)

    def _get_simulate_function_from_name(self, name: str) -> callable:
        """
        Retrieves the simulation function for a given solver name.

        Args:
            name: Name of the solver

        Returns:
            callable: The simulation function

        Example:

            >>> simulate = self.get_simulate_function_from_name("mpi")

            Will return the `simulate` function from the `llg3d.solver.mpi` module.
        """

        module = __import__(f"llg3d.solver.{name}", fromlist=["simulate"])
        return inspect.getattr_static(module, "simulate")

    def save(self):
        """
        Saves the results of the simulation to a JSON file.
        """
        params = self.params.copy()  # save the parameters
        del params["element_class"]  # remove class object before serialization
        if rank == 0:
            results = {"total_time": self.total_time}
            # Export the integral of m1
            if len(self.filenames) > 0:
                results["integral_file"] = self.filenames[0]
                print(f"Integral of m1 in {self.filenames[0]}")
            # Export the x-profiles of m1, m2 and m3
            for i, filename in enumerate(self.filenames[1:]):
                results[f"xprofile_m{i}"] = filename
                print(f"x-profile of m{i} in {filename}")

            print(
                f"""\
N iterations      = {params["N"]}
total_time [s]    = {self.total_time:.03f}
time/ite [s/iter] = {self.total_time / params["N"]:.03e}\
"""
            )
            # Export the mean of m1
            if params["N"] > params["start_averaging"]:
                print(f"m1_mean           = {self.m1_mean:e}")
                results["m1_mean"] = float(self.m1_mean)

            write_json(self.json_file, {"params": params, "results": results})
            print(f"Summary in {self.json_file}")
