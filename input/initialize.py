import numpy as np
from numpy import pi

def pre_process_target(payload):
    """
    Populate state_space matrices
    :param payload: json_dict["target"]
    :return: Nothing
    """

    ss_B = np.array(payload["state_space"]["ss_B"])
    payload["state_space"]["ss_B"]= ss_B

    payload["state"]["dimension"] = ss_B.shape[0]
    payload["noise"]["dimension"] = ss_B.shape[1]

    if not payload["state_space"].get("ss_A"):
        if payload["state"]["motion"]["type"] == "circular":
            speed = payload["state"]["motion"]["parameter"] or 200

            ss_A = [[np.cos(pi/speed), -np.sin(pi/speed)],[np.sin(pi/speed), np.cos(pi/speed)]]
            ss_A = np.array(ss_A)
            payload["state_space"]["ss_A"]= np.array(ss_A)

    return

def pre_process_network(payload):
    adj_matrix = np.array(payload["adjacency"])
    payload["n_sensors"] = len(adj_matrix)

    return