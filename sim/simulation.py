import sim.target
import sim.network
import sim.history
from sim.helpers import line_plot, column
from tqdm import tqdm

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from sim.estimator import EST_SCHEMES


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

        self.results = {EST_SCHEMES[n.est_scheme]["short-name"]: {} for n in self.networks}
        for res, net in zip(self.results.values(), self.networks):
            res["error_squared"] = {sensor: np.zeros(self.duration, dtype=float) for sensor in net.sensors.keys()}

        # In camera-like sensor networks, check whether target's moved out of sensor's FOV
        self.if_fov_checking = False  # Whether sensors' field-of-view is tracked
        self.fov_checker = {}

    def add_sensor_event(self, iteration: int, attribute: str, value, sensors: [str] = None):
        new_event = {"target": {}, "sensors": {}}
        if not sensors:
            sensors = self.networks[0].sensors.keys()

        for sensor in sensors:
            new_event["sensors"][sensor] = {attribute: value}

        if iteration not in self.events:
            self.events.update({iteration: new_event})

        else:
            self.events[iteration]["target"].update(new_event["target"])
            for sensor in sensors:
                self.events[iteration]["sensors"][sensor].update(new_event["sensors"][sensor])

    def add_target_event(self, iteration: int, attribute: str, value, sensors: [str] = None):
        new_event = {"target": {attribute: value},
                     "sensors": {s: {} for s in self.networks[0].sensors.keys()}}
        if iteration not in self.events:
            self.events.update({iteration: new_event})

        else:
            self.events[iteration]["target"].update(new_event["target"])

    def check_for_events(self, current_iteration):
        if current_iteration in self.events.keys():
            self.apply_event(self.events[current_iteration])

            if current_iteration == 0:
                for network in self.networks:
                    _ = [sensor.initialize() for sensor in network.sensors.values()]

        if self.if_fov_checking:
            sensor_naivety = self.check_fov_2D()
            if np.all(sensor_naivety):
                return True
            changes = [(old - new) % 2 for old, new in zip(self.fov_checker["naivety"], sensor_naivety)]
            self.fov_checker["naivety"] = sensor_naivety
            for i, change in enumerate(changes):
                if change:
                    self.set_sensor_naivety(i)

        return False

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
            discard = False
            for network in self.networks:
                network.initialize(self.input_data)

            for time_step in range(self.duration):
                discard = self.check_for_events(time_step)
                for network in self.networks:
                    network.do_iteration(self.target)
                self.target.update()

                if discard:
                    #print(f"Discarded at timestep {time_step}.")
                    break

            if not discard:
                self.update_results(n=sim_number+1)

    def update_results(self, n):
        for res, net in zip(self.results.values(), self.networks):
            for sensor in net.sensors.keys():
                res["error_squared"][sensor] = incremental_mean(res["error_squared"][sensor],
                                                                net.history.get_error_squared(sensor),
                                                                n)

    def plot_error_squared(self, sensor, xlim=None, ylim=None):
        values = []
        labels = []
        for name, res in self.results.items():
            values.append(res["error_squared"][sensor])
            labels.append(name)

        line_plot(values, range(self.duration),
                  ylabel="Mean Squared Error", xlabel="Time Step",
                  labels=labels,
                  xlim=xlim,
                  ylim=ylim,
                  legend_loc='upper left')

    def plot_xy(self, sensor: str, fov_on=True, sensors_on=True):
        print_line()
        for n in self.networks:
            if self.if_fov_checking:
                self.plot_sensors(fov_on, sensors_on)
            print(f"Estimates of Sensor {sensor} using {n.est_scheme} : ")
            n.history.plot_xy(target=True, estimates_of=sensor, legend_loc="lower right")

    def plot_sensors(self, fov_on, sensors_on):
        plt.rcParams["figure.figsize"] = (9, 9)
        if sensors_on:
            # Connectivity
            anchors = np.array(self.fov_checker["anchors"] + [self.fov_checker["anchors"][0]]).T
            plt.plot(anchors[0][0], anchors[0][1], linestyle=(0, (1, 8)), color="black", lw=1,
                     label="Communication Link")
            plt.xlabel("x-coordinate")
            plt.ylabel("y-coordinate")
            for i, _ in enumerate(self.fov_checker["sensors"]):
                direction = 15*self.fov_checker["normals"][i]
                plt.annotate(str(i+1),
                             (anchors[0][0][i], anchors[0][1][i]),
                             textcoords="offset points",
                             xytext=(direction[0], direction[1] - 4),
                             ha='center')

            print("Plot is being limited to 400 units in either axis.")
            plt.xlim([-220, 220])
            plt.ylim([-220, 220])
            plt.plot(230, 230, marker=(3, 0, 0),
                     markersize=15, color="black", linestyle='None', label="Sensor")
            for i, _id in enumerate(self.fov_checker["sensors"]):
                anchor = self.fov_checker["anchors"][i]
                normal = self.fov_checker["normals"][i]
                ang = self.fov_checker["angles"][i]

                # Sensors
                plt.plot(float(anchor[0]), float(anchor[1]), marker=(3, 0, ang - 90),
                         markersize=15, color="black", linestyle='None')

                if fov_on:
                    # FOVs
                    self.plot_fov(anchor, normal)


    def setup_fov_2D(self, positions: dict, angles: dict, fov_angle: float, fov_range: float):
        """
        Assumes list of sensors is ordered
        """
        assert len(positions) == len(self.networks[0].sensors.keys())
        angles_radians = [np.deg2rad(a) for a in angles]

        self.if_fov_checking = True
        print("Field-of-view will be checked during this simulation. "
              "Measurement noise covariance will be overwritten by simulation specifications.")

        self.fov_checker["sensors"] = list(self.networks[0].sensors.keys())
        self.fov_checker["anchors"] = [column(p) for p in positions]
        self.fov_checker["angles"] = angles
        self.fov_checker["normals"] = [column([np.cos(a), np.sin(a)]) for a in angles_radians]
        self.fov_checker["NoiseCov_low"] = deepcopy(self.networks[0].sensors["1"].NoiseCov)
        self.fov_checker["NoiseCov_high"] = 1000*self.fov_checker["NoiseCov_low"]
        self.fov_checker["naivety"] = [0 for _ in self.networks[0].sensors.keys()]
        self.fov_checker["fov_angle_cos"] = np.cos(np.deg2rad(fov_angle)*0.5)
        self.fov_checker["fov_range"] = fov_range
        return

    def check_fov_2D(self):
        target_x = column(self.target.x[0:2])
        naive_sensors = []
        for i in range(len(self.fov_checker["sensors"])):
            position = self.fov_checker["anchors"][i]
            normal = self.fov_checker["normals"][i]
            d = target_x - position
            if float(d.T @ normal) > self.fov_checker["fov_range"]:
                naive_sensors.append(1)
                continue

            d_unit = d/np.sqrt(float(d.T @ d))
            if float(d_unit.T @ normal) < self.fov_checker["fov_angle_cos"]:
                naive_sensors.append(1)
                continue
            naive_sensors.append(0)

        return naive_sensors

    def set_sensor_naivety(self, i):
        _id = self.fov_checker["sensors"][i]
        NoiseCov = self.fov_checker["NoiseCov_high"] if self.fov_checker["naivety"][i] \
            else self.fov_checker["NoiseCov_low"]

        event = {"target": {}, "sensors": {_id: {"NoiseCov": NoiseCov}}}
        self.apply_event(event)

        #if i == 0:
        #    print("Sensor i has experienced : ", event["sensors"][_id], "Target is at ", self.target.x)

    def plot_fov(self, anchor, normal):
        opposite_midpoint = anchor + self.fov_checker["fov_range"]*normal
        cos = self.fov_checker["fov_angle_cos"]
        # opposite_half/range = tan(angle/2)
        opposite_half = self.fov_checker["fov_range"] * (np.sqrt(1-cos**2)/cos)
        perp = np.array([normal[1], -normal[0]])
        p1 = opposite_midpoint - opposite_half * perp
        p2 = opposite_midpoint + opposite_half * perp
        plt.fill([anchor[0], p1[0], p2[0]], [anchor[1], p1[1], p2[1]], "#e2c22220")


def incremental_mean(mean_arr: np.array, new_arr: np.array, n):
    for i in range(len(mean_arr)):
        mean_arr[i] = mean_arr[i] + (new_arr[i] - mean_arr[i])/float(n)

    return mean_arr


def print_line():
    print("\n------------------------------------\n")
