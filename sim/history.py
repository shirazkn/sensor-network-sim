"""
Class object stores simulation results (as time series data)
"""
import matplotlib.pyplot as plt
import numpy as np
from sim.helpers import FIGURE_SIZE


class History:
    def __init__(self, sensor_ids):
        """
        Currently only supports a 2D target
        :param sensor_ids: list(str)
        """
        # History of target x_0, x_1
        self.target = {"x_0": [], "x_1": []}

        # History of sensor measurements, estimates etc.
        self.sensors = {}
        for ID in sensor_ids:
            self.sensors[ID] = {"x_0": [], "x_1": [], "z_0": [], "z_1": [], "ErrCov": []}

    def add_target(self, target_x=None):
        if target_x is not None:
            self.target["x_0"].append(target_x[0])
            self.target["x_1"].append(target_x[1])

    def add_estimates(self, sensors):
        for id, sensor in sensors.items():
            self.sensors[id]["x_0"].append(sensor.estimate[0])
            self.sensors[id]["x_1"].append(sensor.estimate[1])

            self.sensors[id]["z_0"].append(sensor.measurement[0])
            self.sensors[id]["z_1"].append(sensor.measurement[1])
            self.sensors[id]["ErrCov"].append(sensor.ErrCov)

    def plot_xy(self, target=True, estimates_of: str = None, measurements_of: str = None):
        plt.rcParams["figure.figsize"] = FIGURE_SIZE
        plt.gca().set_aspect('equal', adjustable='box')

        if target:
            plt.plot(self.target["x_0"], self.target["x_1"], 'b-', label=f"Target", linewidth=1.2)

        if measurements_of:
            plt.plot(self.sensors[measurements_of]["z_0"], self.sensors[measurements_of]["z_1"], 'g-',
                     label=f"Measurement of sensor {measurements_of}", linewidth=0.3)

        if estimates_of:
            plt.plot(self.sensors[estimates_of]["x_0"], self.sensors[estimates_of]["x_1"], 'r--',
                     label=f"Estimate of sensor {estimates_of}", linewidth=1.2)

        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend(loc='upper right')
        plt.show()

    def get_error_squared(self, s: str = None):
        """
        :param s: ID of sensor
        :return: List of estimation error sq.
        """
        errors = []
        length = len(self.sensors[s]["x_0"])

        for i in range(length):
            estimate = [self.sensors[s]["x_0"][i], self.sensors[s]["x_1"][i]]
            target = [self.target["x_0"][i], self.target["x_1"][i]]
            errors.append(np.array(estimate) - np.array(target))

        return [float(error.T @ error) for error in errors]


def create(network):
    return History(network)
