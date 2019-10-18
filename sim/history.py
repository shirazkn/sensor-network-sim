"""
Class object stores simulation results (as time series data)
"""
import logging
import matplotlib.pyplot as plt
import sim.network
import numpy.linalg as la

FIGURE_SIZE = (12, 7)


class History:
    def __init__(self, network: sim.network.Network):
        """
        Currently only designing for 2D (to keep this project within scope)
        """

        # 'History of target x_0, x_1'
        self.target = {"x_0": [], "x_1": []}

        # 'History of sensors[ID] quantities'
        self.sensors = {}
        sensor_IDs = network.sensors.keys()
        for ID in sensor_IDs:
            self.sensors[ID] = {"x_0": [], "x_1": [], "z_0": [], "z_1": [], "ErrCov": []}

    def add_target(self, target_x=None):
        if target_x is not None:
            self.target["x_0"].append(target_x[0])
            self.target["x_1"].append(target_x[1])
            logging.debug(f"Target is at {target_x}.")

    def add_estimates(self, network: sim.network.Network = None):
        if network:
            for id, sensor in network.sensors.items():
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
            print(f"Plotted history of target coordinates.")

        if measurements_of:
            plt.plot(self.sensors[measurements_of]["z_0"], self.sensors[measurements_of]["z_1"], 'g-',
                     label=f"Measurement of sensor {measurements_of}", linewidth=0.3)
            print(f"Plotted history of sensor {measurements_of}'s measurements.")

        if estimates_of:
            plt.plot(self.sensors[estimates_of]["x_0"], self.sensors[estimates_of]["x_1"], 'r--',
                     label=f"Estimate of sensor {estimates_of}", linewidth=1.2)
            print(f"Plotted history of sensor {estimates_of}'s estimates.")

        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend(loc='upper right')
        plt.show()

    def plot_timeseries(self, ErrCov_of: str = None):
        plt.rcParams["figure.figsize"] = FIGURE_SIZE
        y_vals = [la.norm(_matrix, 'fro') for _matrix in self.sensors[ErrCov_of]["ErrCov"]]
        plt.plot(y_vals, label=f"Sensor {ErrCov_of}")
        if ErrCov_of:
            plt.title("Estimated Error Covariance")
        plt.xlabel("Iteration")
        plt.ylabel("Err Cov. (Frob. Norm)")
        plt.legend(loc='lower right')
        plt.show()


def create(network):
    return History(network)


