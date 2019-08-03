import numpy as np
from numpy import pi
import logging

def pre_process_target(payload):
    """
    Populate state_space matrices
    :param payload: json_dict["target"]
    :return: Nothing
    """

    ss_B = np.array(payload["state"]["ss_B"])
    payload["state"]["ss_B"]= ss_B
    payload["state"]["dimension"] = ss_B.shape[0]

    if not payload["state"].get("ss_A"):
        if payload["state"]["motion"]["type"] == "circular":
            speed = payload["state"]["motion"]["parameter"] or 200

            ss_A = [[np.cos(pi/speed), -np.sin(pi/speed)],[np.sin(pi/speed), np.cos(pi/speed)]]
            ss_A = np.array(ss_A)
            payload["state"]["ss_A"]= np.array(ss_A)
            del payload["state"]["motion"]

    return

def pre_process_network(payload):
    network = payload["network"]
    adj_matrix = np.array(network["adjacency"])
    network["n_sensors"] = len(adj_matrix)

    obs_data = payload["observation_matrices"]
    noise_data = payload["noise_covariances"]
    network["observability"] = pre_process_matrices(network["n_sensors"], obs_data)
    network["noise"] = pre_process_matrices(network["n_sensors"], noise_data)

    del payload["observation_matrices"]
    del payload["noise_covariances"]
    return


def pre_process_matrices(length_matrices, matrix_data):
    default_matrix = matrix_data["default_matrix"]
    matrices = []
    for i in range(length_matrices):
        matrices.append(default_matrix)

    if not "other" in matrix_data:
        return matrices

    # Any non-default matrices are in 'other' key
    for key, _matrix in matrix_data["other"].items():
        matrices[int(key)] = _matrix

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
    pre_process_target(raw_data["target"])
    pre_process_network(raw_data)
    logging.debug("Data ready for simulation.")
    return raw_data