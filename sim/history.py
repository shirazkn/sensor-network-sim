"""
Class object stores simulation results (as time series data)
"""
import os
import logging
import datetime
import json
import matplotlib.pyplot as plt
import sim.network
import numpy.linalg as la
from sim.helpers import make_dir

FIGURE_SIZE = (10, 10)


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

    def plot_xy(self, target=True, estimates_of: str = None, measurements_of: str = None):
        plt.rcParams["figure.figsize"] = FIGURE_SIZE
        if target:
            plt.plot(self.target["x_0"], self.target["x_1"], 'g-', label=f"Target")
            print(f"Plotted history of target coordinates.")

        if measurements_of:
            plt.plot(self.sensors[measurements_of]["z_0"], self.sensors[measurements_of]["z_1"], 'r-',
                     label=f"Measurement of sensor {measurements_of}")
            print(f"Plotted history of sensor estimates {measurements_of}.")

        if estimates_of:
            plt.plot(self.sensors[estimates_of]["x_0"], self.sensors[estimates_of]["x_1"], 'b-',
                     label=f"Estimate of sensor {estimates_of}")
            print(f"Plotted history of sensor estimates {estimates_of}.")

        print("Showing plot...")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend(loc='lower right')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    def plot_timeseries(self, ErrCov_of: str = None):
        plt.rcParams["figure.figsize"] = FIGURE_SIZE
        y_vals = [la.norm(_matrix, 'fro') for _matrix in self.sensors[ErrCov_of]["ErrCov"]]
        plt.plot(y_vals, label=f"Sensor {ErrCov_of}")
        plt.xlabel("Iteration")
        plt.ylabel("Err Cov. (Frob. Norm)")
        plt.legend(loc='lower right')
        plt.show()


def monte_carlo_avg(mc_history: sim.history.History, new_history: sim.history.History, count):
            """
            TODO add method to average two histories (so you can do mc_avg_history.add(sim.history.average, 1000) )
            :return:
            """
            raise NotImplementedError


def save(info: dict = None, history: sim.history.History = None, name=None, timestamp=True,
         by_date=True, by_scheme=True):
    """
    :param info: Send the 'input_data' dict here, which is the dict created after input json file is parsed
    :param history: Simulation history
    :param name: Optional name ( must be unique if timestamp is set to False)
    :param timestamp: Whether to append a timestamp to name
    :param by_date: Whether to sort data by date (folder)
    :param by_scheme: Whether to sort by estimation scheme (sub-folder)
    :return Location of saved file
    """

    saved_data = {"info": None, "history": None}

    estimation_scheme = "Unknown"
    if info is not None:
        saved_data["info"] = info
        estimation_scheme = info["scheme"]

    if not isinstance(history, sim.history.History):
        raise ValueError
    saved_data["history"] = vars(history)

    # Determine save path
    save_location = "output/"
    if by_date:
        today = datetime.date.today()
        today_text = today.strftime("%B %d, %Y")
        save_location += today_text + "/"
        make_dir(save_location)

    if by_scheme:
        save_location += estimation_scheme + "/"
        make_dir(save_location)

    # Determine save filename
    if timestamp:
        _time = datetime.datetime.now()
        _time_text = _time.strftime("%H:%M:%S")
        save_location+= f"({_time_text}) "

    if name:
        save_location += name

    else:
        save_location += "Untitled"

    saved_json = json.dumps(saved_data)
    with open(save_location, "w") as json_file:
        json_file.write(saved_json)

    print(f"Saved simulation data to {save_location}.")
    return save_location
