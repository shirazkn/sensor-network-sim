"""
Class object stores simulation results (as time series data)
"""
import logging
import matplotlib.pyplot as plt
import sim.network


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
            self.sensors[ID] = {"x_0": [], "x_1": []}

    def add(self, target_x=None, estimates_of_sensors=None, cross_covs_of_sensors=None):
        if target_x is not None:
            self.target["x_0"].append(target_x[0])
            self.target["x_1"].append(target_x[1])
            logging.debug(f"Added target_x to history.")

        if estimates_of_sensors:
            for sensor_ID, estimate in estimates_of_sensors.items():
                self.sensors[sensor_ID]["x_0"].append(estimate[0])
                self.sensors[sensor_ID]["x_1"].append(estimate[1])
            logging.debug(f"Added sensor estimates to history.")

        if cross_covs_of_sensors:
            for sensor_ID, cross_cov in cross_covs_of_sensors:
                self.sensors[sensor_ID]["cross_cov"].append(cross_cov)
            logging.debug(f"Added sensor cross_covariances to history.")

    def plot_xy(self, target=True, estimates_of_sensors=[]):
        if target:
            plt.plot(self.target["x_0"], self.target["x_1"], 'bo')
            print(f"Plotted history of target coordinates.")

        for sensor_ID in estimates_of_sensors:
            plt.plot(self.sensors[sensor_ID]["x_0"], self.sensors[sensor_ID]["x_1"], 'r+')
            print(f"Plotted history of sensor estimates {sensor_ID}.")

        print("Showing plot...")
        plt.show()
