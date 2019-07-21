import json
import numpy as np

def read_config(filename):
    with open(filename, "r") as file:
        return json.load(file)


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
    assert "state_space" in data["target"]
    assert "ss_B" in data["target"]["state_space"]