import numpy as np
import sim.network
import sim.helpers


def pre_process_target(raw_data):
    """
    Get state_space matrices for target (from json information)
    """
    target_data = raw_data["target"]

    ss_A = np.array(target_data["state_space"]["ss_A"])
    target_data["state_space"]["ss_A"] = ss_A
    ss_B = np.array(target_data["state_space"]["ss_B"])
    target_data["state_space"]["ss_B"] = ss_B

    target_data["dimensions"] = {"state": ss_A.shape[0]}
    # target_data["dimensions"]["noise"] = ss_B.shape[0]

    return


def pre_process_network(raw_data):
    """
    Get observation models for network (from json information)
    """
    network = raw_data["network"]
    adj_matrix = np.array(network["adjacency"])
    network["n_sensors"] = len(adj_matrix)
    network["observation_matrices"] = get_matrices_for_all_sensors(network, network["observation_matrices"]["default"])
    network["noise_covariances"] = get_matrices_for_all_sensors(network, network["noise_covariances"]["default"])

    return


def get_matrices_for_all_sensors(network_data, default_matrix):
    """
    Returns {"ID": <Matrix>} dict for all sensors in network
    """
    sensor_ids = sim.helpers.get_unique_ids(network_data["n_sensors"])

    matrices = {}
    for _id in sensor_ids:
        matrices[_id] = default_matrix

    return matrices


def do_everything(raw_data):
    adj_matrix = np.array(raw_data["network"]["adjacency"])
    assert np.all(adj_matrix == adj_matrix.transpose()), "Adjacency matrix must be symmetric."
    pre_process_target(raw_data)
    pre_process_network(raw_data)

    return raw_data
