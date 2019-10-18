"""
Function to deal with sensor creation, update etc
"""
import sim.sensor
import sim.estimator
import sim.mailbox
import sim.errors
import sim.helpers
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

        self.sensor_params = {}
        self.SensorClass, self.sensor_params = sim.estimator.get_estimator(estimation_scheme)

        # Messages shared between sensors in the network are put in the 'mailbox'
        self.mailbox: sim.mailbox.Mailbox

        # Info needed about the target at every time-step
        self.target_info = {key: None for key in self.SensorClass.INFO_NEEDED_FROM_TARGET}

    def create_sensors(self, data: dict):
        """
        Make all sensors in the network
        """
        adjacency_matrix = data["adjacency"]

        # Using uniquely 'named' sensor objects
        sensor_ids = sim.helpers.get_unique_ids(data["n_sensors"])

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

    def make_measurements(self, target_x):
        """
        All sensors make noisy measurements
        """
        for sensor in self.sensors.values():
            sensor.make_measurement(target_x)

    def share_info_with_neighbors(self):
        """
        All sensors share information and prepare for estimation
        """
        for sensor_ID, sensor in self.sensors.items():
            payload = {key: sensor[key] for key in sensor.INFO_NEEDED_FROM_NEIGHBORS}
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
        for sensor in self.sensors.values():
            neighbor_info = {}
            for neighbor_ID in sensor.neighbors:
                neighbor_info[neighbor_ID] = self.mailbox.receive_from_sensor(neighbor_ID)
            sensor.do_estimation(self.target_info, neighbor_info)


def create(input_data):
    """
    Creates new Network object based on input data
    """
    _data = deepcopy(input_data)
    estimation_scheme = _data["scheme"]
    network = sim.network.Network(estimation_scheme)
    network.create_sensors(_data["network"])
    network.mailbox = sim.mailbox.Mailbox(network)
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
