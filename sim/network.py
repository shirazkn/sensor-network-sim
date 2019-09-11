"""
Function to deal with sensor creation, update etc
"""
import sim.sensor
import sim.messages
import sim.errors

# Add your new estimation scheme here
import sim.estimators.template
import sim.estimators.KCF_2007
import sim.estimators.OptimalMVF
import sim.estimators.ICF_2013

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


def get_sensor_ids(data):
    data["indexing_style"] = data.get("indexing_style", "python")

    if data["indexing_style"] == "matlab":
        return [str(_id) for _id in range(1, data["n_sensors"] + 1)]
    elif data["indexing_style"] == "python":
        return [str(_id) for _id in range(data["n_sensors"])]


class Network:
    """
    To make the sensor network indexing easier (without having to deal with the mutability of a list)
    """

    def __init__(self, estimation_scheme=None):
        """
        Makes a dict where key is the sensor ID and value is the sensor dict
        """

        self.SensorClass = sim.estimators.template.EstimatorTemp
        self.sensor_params = {}

        # Add your new estimation scheme here

        if estimation_scheme == "KCF":
            self.SensorClass = sim.estimators.KCF_2007.EstimatorKCF
            self.sensor_params = {"epsilon": 0.25}

        elif estimation_scheme == "OMVF":
            self.SensorClass = sim.estimators.OptimalMVF.EstimatorOMVF

        elif estimation_scheme == "ICF":
            self.SensorClass = sim.estimators.ICF_2013.EstimatorICF
            self.sensor_params = {"epsilon": 0.25}
        else:
            print("Wrong estimation scheme ; No estimator selected!")

        self.sensors: Dict[str, sim.sensor.Sensor] = {}

        # Messages shared between sensors in the network
        self.messages: sim.messages.Messages

        # Info needed about the target
        self.target_info = {key: None for key in self.SensorClass.INFO_NEEDED_FROM_TARGET}

    def create_sensors(self, data: dict):
        """
        Make all sensors in the network
        :param data: input_data["network"]
        """
        adjacency_matrix = data["adjacency"]
        obs_matrices = data["observation_matrices"]
        cov_matrices = data["noise_covariances"]

        # Using uniquely 'named' sensor objects instead of relying on list indices
        sensor_ids = get_sensor_ids(data)

        for index in range(data["n_sensors"]):
            _id = sensor_ids[index]
            neighbor_indices = _get_neighbor_indices(index, adjacency_matrix[index][:])
            neighbors = [sensor_ids[_i] for _i in neighbor_indices]
            obs_matrix = obs_matrices[_id]
            cov_matrix = cov_matrices[_id]
            self.add_sensor(_id, neighbors, obs_matrix, cov_matrix, **self.sensor_params)

    def add_sensor(self, id, neighbors, obs_matrix, noise_cov_matrix, **kwargs):
        """
        :param id: Sensor ID (unique)
        :param neighbors: IDs of neighboring sensors
        :param obs_matrix: numpy nd array, Observability matrix
        :param noise_cov_matrix: numpy nd array, Noise co-variance
        """
        assert str(id) not in self.sensors, "Duplicate sensor ID!"

        # (Note : Must use keyword args here...)
        sensor_object = self.SensorClass(sensor_id=id, neighbors=neighbors, obs_matrix=obs_matrix, noise_cov_matrix=noise_cov_matrix, **kwargs)
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
