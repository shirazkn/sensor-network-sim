import sim.target
import sim.network
import sim.history
from sim.helpers import line_plot
from tqdm import tqdm

import numpy as np
from copy import deepcopy


class Simulation:
    def __init__(self, input_data, est_schemes, duration):
        """
        Each Simulation object has exactly one target, and multiple estimation schemes
        :param input_data: Output of settings.input.read()
        :param est_schemes: list of strings
        """
        self.input_data = input_data

        self.target = sim.target.create(input_data)
        self.networks = [sim.network.create(input_data, es) for es in est_schemes]
        self.duration = duration
        self.events = {}

        self.results = {n.est_scheme: {} for n in self.networks}
        for res, net in zip(self.results.values(), self.networks):
            res["error_squared"] = {sensor: np.zeros(self.duration, dtype=float) for sensor in net.sensors.keys()}

    def add_event(self, iteration: int, attribute: str, value, sensors: [str] = None):
        new_event = {"target": {}, "sensors": {}}
        if not sensors:
            sensors = self.networks[0].sensors.keys()

        for sensor in sensors:
            new_event["sensors"][sensor] = {attribute: value}

        self.events.update({iteration: new_event})

    def check_for_events(self, current_iteration):
        if current_iteration in self.events.keys():
            self.apply_event(self.events[current_iteration])

    def apply_event(self, event):
        for attr, value in event["target"].items():
            self.target[attr] = value

        for sensor_id, change in event["sensors"].items():
            for attr, value in change.items():
                for network in self.networks:
                    network.sensors[sensor_id][attr] = deepcopy(value)

    def run(self, n_simulations=1):
        """
        :param n_simulations: No. of monte-carlo simulations to average over
        :return: None
        """
        print("\n")
        for sim_number in tqdm(range(n_simulations)):
            for network in self.networks:
                network.initialize(self.input_data)

            for time_step in range(self.duration):
                self.check_for_events(time_step)
                for network in self.networks:
                    network.do_iteration(self.target)
                self.target.update()

            self.update_results(n=sim_number+1)

    def update_results(self, n):
        for res, net in zip(self.results.values(), self.networks):
            for sensor in net.sensors.keys():
                res["error_squared"][sensor] = incremental_mean(res["error_squared"][sensor],
                                                                net.history.get_error_squared(sensor),
                                                                n)

    def plot_error_squared(self, sensor, ylim=None):
        values = []
        labels = []
        for name, res in self.results.items():
            values.append(res["error_squared"][sensor])
            labels.append(name)

        line_plot(values, range(self.duration),
                  ylabel="Est. Error Squared", xlabel="Iteration",
                  title=f"Est. Error Squared of sensor {sensor}",
                  labels=labels,
                  ylim=ylim)

    def plot_xy(self, sensor: str):
        print_line()
        for n in self.networks:
            print(f"Estimates of sensor {sensor} using {n.est_scheme} : ")
            n.history.plot_xy(target=True, estimates_of=sensor)


def incremental_mean(mean_arr: np.array, new_arr: np.array, n):
    for i in range(len(mean_arr)):
        mean_arr[i] = mean_arr[i] + (new_arr[i] - mean_arr[i])/float(n)

    return mean_arr


def print_line():
    print("\n------------------------------------\n")
