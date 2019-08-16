import numpy as np
from numpy import pi
import logging
import sim.network


def pre_process_target(raw_data):
    """
    Populate state_space matrices
    :param raw_data: json_dict["target"]
    :return: Nothing
    """
    target_data = raw_data["target"]
    ss_B = np.array(target_data["state"]["ss_B"])
    target_data["state"]["ss_B"] = ss_B
    target_data["state"]["dimension"] = ss_B.shape[0]

    if not target_data["state"].get("ss_A"):
        if target_data["state"]["motion"]["type"] == "circular":
            speed = target_data["state"]["motion"]["parameter"] or 200

            ss_A = [
                [np.cos(pi / speed), -np.sin(pi / speed)],
                [np.sin(pi / speed), np.cos(pi / speed)],
            ]
            ss_A = np.array(ss_A)
            target_data["state"]["ss_A"] = np.array(ss_A)
            del target_data["state"]["motion"]

    return


def pre_process_network(raw_data):
    network = raw_data["network"]
    adj_matrix = np.array(network["adjacency"])
    network["n_sensors"] = len(adj_matrix)

    obs_data = raw_data["observation_matrices"]
    noise_data = raw_data["noise_covariances"]

    network["observability"] = pre_process_matrices(network, obs_data)
    network["noise"] = pre_process_matrices(network, noise_data)

    del raw_data["observation_matrices"]
    del raw_data["noise_covariances"]
    return


def pre_process_matrices(network_data, matrix_data):
    default_matrix = matrix_data["default_matrix"]
    matrices = {}
    sensor_ids = sim.network.get_sensor_ids(network_data)
    for id in sensor_ids:
        matrices[id] = default_matrix

    if "other" not in matrix_data:
        return matrices

    # Any non-default matrices are in 'other' key
    for key, _matrix in matrix_data["other"].items():
        matrices[key] = _matrix

    return matrices


def sanity_check(data):
    assert "network" in data
    assert "adjacency" in data["network"]

    adj_matrix = np.array(data["network"]["adjacency"])
    adj_matrix_dim = adj_matrix.shape
    assert adj_matrix_dim[0] == adj_matrix_dim[1]
    assert np.all(adj_matrix == adj_matrix.transpose())

    assert "simulation" in data
    assert data["simulation"]["total_steps"] > 0

    assert "target" in data
    assert "state" in data["target"]
    assert "motion" in data["target"]["state"]
    assert "type" in data["target"]["state"]["motion"]

    assert "noise" in data["target"]
    assert "ss_B" in data["target"]["state"]


def do_everything(raw_data):
    sanity_check(raw_data)
    pre_process_target(raw_data)
    pre_process_network(raw_data)
    logging.debug("Data ready for simulation.")
    return raw_data
