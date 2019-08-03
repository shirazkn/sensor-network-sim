"""
Class object stores simulation results (as time series data)
"""
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import classes.network


class History:
    def __init__(self, network: classes.network.Network):
        """
        Currently only designing for 2D (to keep this project within scope)
        """
        self.target_x = {"0": [], "1": []}
        sensor_IDs = network.get_sensors().keys()
        self.sensor_estimates = {}
        for ID in sensor_IDs:
            self.sensor_estimates[ID] = {"x_1": [], "x_2": []}

    def add(self, target_x=None, estimates=None):
        if target_x:
            self.target_x["0"].append(target_x[0])
            self.target_x["1"].append(target_x[1])

        # Note : Might have to split this into prior and post
        if estimates:
            raise NotImplementedError
