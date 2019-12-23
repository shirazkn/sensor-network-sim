"""
Function to deal with sensor creation, update etc
"""
import sim.sensor
import sim.estimator
import sim.mailbox
import sim.errors
import sim.helpers
import sim.history
from sim.estimator import EST_SCHEMES
from copy import deepcopy

from typing import Dict


class Network:
    """
    Triggers network-wide operations such as 'do_estimation'
    (Synchronous, and hence fundamentally flawed implementation since it assumes the presence of a supervisor)
    """

    def __init__(self, estimation_scheme=None):
        # Dict of {sensor_ID : Sensor object}
        self.sensors: Dict[str, sim.sensor.Sensor] = {}
        self.history = None

        if estimation_scheme in EST_SCHEMES:
            self.est_scheme = estimation_scheme
        else:
            raise ValueError(f"Invalid estimation scheme. Available schemes : {[_s for _s in EST_SCHEMES.keys()]}")

        self.SensorClass, self.sensor_params = sim.estimator.get_estimator(self.est_scheme)

        # Messages shared between sensors in the network are put in the 'mailbox'
        self.mailbox: sim.mailbox.Mailbox = None

        # Info needed about the target at every time-step
        self.target_info = {key: None for key in self.SensorClass.INFO_NEEDED_FROM_TARGET}

    def initialize(self, input_data):
        self.sensors = {}
        self.create_sensors(input_data["network"])
        for sensor in self.sensors.values():
            sensor.initialize()

        self.mailbox = sim.mailbox.Mailbox(self)
        self.history = sim.history.create(self.sensors.keys())

    def create_sensors(self, data: dict):
        """
        Make all sensors in the network
        """
        adjacency_matrix = data["adjacency"]

        # Use uniquely 'named' sensor objects
        sensor_ids = sim.helpers.get_unique_ids(data["n_sensors"])

        # Check if sensor requires global information
        if self.SensorClass.REQUIRES_GLOBAL_INFO:
            self.sensor_params["all_sensor_ids"] = sensor_ids.copy()

        # Create and add sensors to network
        for index in range(data["n_sensors"]):
            # Get own ID
            _id = sensor_ids[index]

            # Get neighbors' IDs
            neighbor_indices = _get_neighbor_indices(index, adjacency_matrix[index][:])
            neighbors = [sensor_ids[_i] for _i in neighbor_indices]

            # Get observation model
            obs_matrix = data["observation_matrices"][_id]
            cov_matrix = data["noise_covariances"][_id]

            self.add_sensor(_id, neighbors, obs_matrix, cov_matrix, **self.sensor_params)

    def add_sensor(self, id, neighbors, obs_matrix, noise_cov_matrix, **kwargs):
        """
        :param id: Sensor ID (unique)
        :param neighbors: IDs of neighboring sensors
        :param obs_matrix: numpy nd array, Observability matrix
        :param noise_cov_matrix: numpy nd array, Noise co-variance
        """
        assert str(id) not in self.sensors, "Duplicate sensor ID!"
        sensor_object = self.SensorClass(sensor_id=id, neighbors=neighbors, obs_matrix=obs_matrix,
                                         noise_cov_matrix=noise_cov_matrix, **kwargs)
        self.sensors[str(id)] = sensor_object

    def do_iteration(self, target):
        """
        Does one time-step of estimation
        """
        self.history.add_target(target.x)

        # Single time-step of estimation algorithm
        self.make_measurements(target.x)
        self.share_info_with_neighbors()
        self.get_info_about_target(target)
        self.do_estimations()

        self.history.add_estimates(self.sensors)

    def make_measurements(self, target_x):
        """
        All sensors make (noisy) measurements
        """
        for sensor in self.sensors.values():
            sensor.make_measurement(target_x)

    def share_info_with_neighbors(self):
        """
        All sensors share information and prepare for estimation
        """
        for sensor_ID, sensor in self.sensors.items():
            payload = {key: sensor[key] for key in self.SensorClass.INFO_NEEDED_FROM_NEIGHBORS}
            self.mailbox.send(sensor_ID, payload.copy())

    def get_info_about_target(self, target):
        """
        Sensors may access target's state-space matrices
        """
        for key in self.target_info:
            self.target_info[key] = target[key]

    def do_estimations(self):
        """
        All sensors do estimation
        """
        if not self.SensorClass.REQUIRES_GLOBAL_INFO:
            for sensor in self.sensors.values():
                neighbor_info = {}
                for neighbor_ID in sensor.neighbors:
                    neighbor_info[neighbor_ID] = self.mailbox.receive_from_sensor(neighbor_ID)
                sensor.do_estimation(self.target_info, neighbor_info)

        else:
            for sensor in self.sensors.values():
                sensor.do_estimation(self.target_info, self.sensors)


def create(input_data, est_scheme):
    """
    Creates new Network object based on input data
    """
    # Check if sensor requires global information
    if EST_SCHEMES[est_scheme]["class"].REQUIRES_GLOBAL_INFO:
        print(f"Selected scheme {EST_SCHEMES[est_scheme]['short-name']} (It's not fully-distributed!)")
    else:
        print(f"Selected scheme {EST_SCHEMES[est_scheme]['short-name']}")

    network = sim.network.Network(est_scheme)
    network.create_sensors(input_data["network"])
    return network


def _get_neighbor_indices(self_index, adjacency_row):
    """
    Get list of sensors connected to the sensor <self_index>
    """
    return [
        index
        for index, value in enumerate(adjacency_row)
        if value and index != self_index
    ]
