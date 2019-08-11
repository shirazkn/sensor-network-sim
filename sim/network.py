"""
Function to deal with sensor creation, update etc
"""
import sim.sensor
import sim.messages
import sim.estimators.template

from typing import Dict


def create(input_data):
    """
    Creates network object and adds sensors.
    :param input_data: result of setting.initialize.do_everything()
    :return: network object with sensors
    """
    estimation_scheme = input_data["scheme"]
    network = sim.network.Network(estimation_scheme)
    network.create_sensors(input_data["network"])
    network.messages = sim.messages.Messages(network)
    return network


class Network:
    """
    To make the sensor network indexing easier (without having to deal with the mutability of a list)
    """

    def __init__(self, estimation_scheme=None):
        """
        Makes a dict where key is the sensor ID and value is the sensor dict
        """

        self.SensorClass = sim.estimators.template.EstimatorTemp

        # if estimation_scheme == "ICF":
        #     self.SensorClass = sim.estimators.ICF.EstimatorICF
        #
        # elif estimation_scheme == "KCF":
        #     self.SensorClass = sim.estimators.KCF.EstimatorKCF

        self.sensors: Dict[str, sim.sensor.Sensor] = {}

        # Messages shared between sensors in the network
        self.messages: sim.messages.Messages

        # Info needed about the target
        self.target_info = {key: None for key in self.SensorClass.INFO_NEEDED_FROM_TARGET}

    def get_sensor(self, index: int) -> sim.sensor.Sensor:
        """
        Not sure if this method is needed. I intend to do bulk operations on sensors via the network object
        :param index: int or str
        """
        return self.sensors[str(index)]

    def get_sensors(self) -> Dict[str, sim.sensor.Sensor]:
        """
        Not sure if this method is needed. I intend to do bulk operations on sensors via the network object
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
        sensor_ids = [str(_id) for _id in range(1, data["n_sensors"] + 1)]

        # assert len(sensor_IDs) == len(set(sensor_IDs))

        for index in range(data["n_sensors"]):
            id = sensor_ids[index]
            neighbor_indices = _get_neighbor_indices(index, adjacency_matrix[index][:])
            neighbors = [sensor_ids[_i] for _i in neighbor_indices]
            obs_matrix = obs_matrices[index]
            cov_matrix = cov_matrices[index]
            self.add_sensor(id, neighbors, obs_matrix, cov_matrix)

    def add_sensor(self, id, neighbors, obs_matrix, cov_matrix):
        """
        :param id: Sensor ID (unique)
        :param neighbors: IDs of neighboring sensors
        :param obs_matrix: numpy nd array, Observability matrix
        :param cov_matrix: numpy nd array, Noise co-variance
        """
        assert str(id) not in self.sensors, "Duplicate sensor ID!"
        sensor_object = self.SensorClass(id, neighbors, obs_matrix, cov_matrix)
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
            self.messages.send(sensor_ID, payload.copy())

    def get_info_about_target(self, target):
        for key in self.target_info:
            self.target_info[key] = target[key]

    def do_estimations(self):
        for sensor in self.sensors.values():
            neighbor_info = {}
            for neighbor_ID in sensor.neighbors:
                neighbor_info[neighbor_ID] = self.messages.receive_from_sensor(neighbor_ID)
            sensor.do_estimation(self.target_info, neighbor_info)


def _get_neighbor_indices(self_index, adjacency_row):
    return [
        index
        for index, value in enumerate(adjacency_row)
        if value and index != self_index
    ]
