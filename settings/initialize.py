import numpy as np
from numpy import pi
import sim.network


def pre_process_target(raw_data):
    """
    Populate state_space matrices
    :param raw_data: json_dict["target"]
    :return: Nothing
    """
    target_data = raw_data["target"]
    ss_B = np.array(target_data["state_space"]["ss_B"])
    target_data["state_space"]["ss_B"] = ss_B
    target_data["state_space"]["dimension"] = ss_B.shape[0]

    if not target_data["state_space"].get("ss_A"):
        if target_data["state_space"]["motion"]["type"] == "circular":
            speed = target_data["state_space"]["motion"]["parameter"] or 200

            ss_A = [
                [np.cos(pi / speed), -np.sin(pi / speed)],
                [np.sin(pi / speed), np.cos(pi / speed)],
            ]

            ss_A = np.array(ss_A)
            target_data["state_space"]["ss_A"] = np.array(ss_A)
            del target_data["state_space"]["motion"]

    return


def pre_process_network(raw_data):
    network = raw_data["network"]
    adj_matrix = np.array(network["adjacency"])
    network["n_sensors"] = len(adj_matrix)
    network["observation_matrices"] = pre_process_matrices(network, network["observation_matrices"]["default"])
    network["noise_covariances"] = pre_process_matrices(network, network["noise_covariances"]["default"])

    return


def pre_process_matrices(network_data, default_matrix):
    default_matrix = default_matrix
    matrices = {}
    sensor_ids = sim.network.get_sensor_ids(network_data)
    for id in sensor_ids:
        matrices[id] = default_matrix
    return matrices


def do_everything(raw_data):
    adj_matrix = np.array(raw_data["network"]["adjacency"])
    assert np.all(adj_matrix == adj_matrix.transpose()), "Adjacency matrix must be symmetric."
    pre_process_target(raw_data)
    pre_process_network(raw_data)
    return raw_data
