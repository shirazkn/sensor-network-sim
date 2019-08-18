"""
Class object stores simulation results (as time series data)
"""
import logging
import matplotlib.pyplot as plt
import sim.network
import numpy.linalg as la


def create(network):
    """
    Abstraction of __init__ method
    """
    return History(network)


class History:
    def __init__(self, network: sim.network.Network):
        """
        Currently only designing for 2D (to keep this project within scope)
        """

        # 'History of target x_0, x_1'
        self.target = {"x_0": [], "x_1": []}

        # 'History of sensors[ID] quantities'
        self.sensors = {}
        sensor_IDs = network.get_sensors().keys()
        for ID in sensor_IDs:
            self.sensors[ID] = {"x_0": [], "x_1": [], "z_0": [], "z_1": [], "ErrCov": []}

    def add_target(self, target_x=None):
        if target_x is not None:
            self.target["x_0"].append(target_x[0])
            self.target["x_1"].append(target_x[1])
            logging.debug(f"Added target_x to history.")

    def add_estimates(self, network: sim.network.Network = None):
        if network:
            for id, sensor in network.sensors.items():
                self.sensors[id]["x_0"].append(sensor.estimate[0])
                self.sensors[id]["x_1"].append(sensor.estimate[1])

                self.sensors[id]["z_0"].append(sensor.measurement[0])
                self.sensors[id]["z_1"].append(sensor.measurement[1])
                self.sensors[id]["ErrCov"].append(sensor.ErrCov)
            logging.debug(f"Added sensor estimates to history.")

    def plot_xy(self, target=True, estimates_of: str = None, measurement_of: str = None):
        if target:
            plt.plot(self.target["x_0"], self.target["x_1"], 'g-')
            print(f"Plotted history of target coordinates.")

        if measurement_of:
            plt.plot(self.sensors[measurement_of]["z_0"], self.sensors[measurement_of]["z_1"], 'r-')
            print(f"Plotted history of sensor estimates {measurement_of}.")

        if estimates_of:
            plt.plot(self.sensors[estimates_of]["x_0"], self.sensors[estimates_of]["x_1"], 'b-')
            print(f"Plotted history of sensor estimates {estimates_of}.")

        print("Showing plot...")
        plt.show()

    def plot_timeseries(self, ErrCov_of: str = None):
        y_vals = [la.norm(_matrix) for _matrix in self.sensors[ErrCov_of]["ErrCov"]]
        plt.plot(y_vals)
        plt.show()