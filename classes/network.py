"""
Function to deal with sensor creation, update etc
"""
import classes.sensor
from typing import Dict


class Network:
    """
    To make the sensor network indexing easier (without having to deal with the mutability of a list)
    """

    def __init__(self):
        """
        Makes a dict where key is the sensor ID and value is the sensor dict
        """
        self.sensors: Dict[str, classes.sensor.Sensor] = {}

    def get_sensor(self, index: int) -> classes.sensor.Sensor:
        """
        Not sure if this method is needed. I intend to do bulk operations on sensors via the network object
        :param index: int or str
        """
        return self.sensors[str(index)]

    def get_sensors(self) -> Dict[str, classes.sensor.Sensor]:
        """
        Not sure if this method is needed. I intend to do bulk operations on sensors via the network object
        :param index: int or str
        """
        return self.sensors

    def get_estimates(self):
        raise NotImplementedError

    def create_sensors(self, data: dict):
        """
        Make all sensors in the network
        :param data: input_data["network"]
        """
        adjacency_matrix = data["adjacency"]
        obs_matrices = data["observability"]
        cov_matrices = data["noise"]

        # Using uniquely 'named' sensor objects instead of relying in list indices
        sensor_IDs = range(1, data["n_sensors"] + 1)
        # assert len(sensor_IDs) == len(set(sensor_IDs))

        for index in range(data["n_sensors"]):
            obs_matrix = obs_matrices[index]
            cov_matrix = cov_matrices[index]

            neighbor_indices = _get_neighbor_indices(index, adjacency_matrix[index][:])
            neighbors = [sensor_IDs[_i] for _i in neighbor_indices]

            self.add_sensor(id, neighbors, obs_matrix, cov_matrix)

    def add_sensor(self, id, neighbors, obs_matrix, cov_matrix):
        """
        :param id: Sensor ID (unique)
        :param H_matrix: numpy nd array, Observability matrix
        :param R_matrix: numpy nd array, Noise co-variance
        """
        assert str(id) not in self.sensors, "Duplicate sensor ID!"
        sensor_object = classes.sensor.Sensor(id, obs_matrix, cov_matrix)
        self.sensors[str(id)] = sensor_object

    def make_measurements(self, target_x):
        """
        All sensors make noisy measurements
        """
        for sensor in self.sensors.values():
            sensor.make_measurement(target_x)


def _get_neighbor_indices(self_index, adjacency_row):
    return [
        index
        for index, value in enumerate(adjacency_row)
        if value and index != self_index
    ]
