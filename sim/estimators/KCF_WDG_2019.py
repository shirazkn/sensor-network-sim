"""
------------------------
Kalman Consensus Filter with Weighted Consensus (KCF-WDG, 2019)
------------------------
Notes:
    WDG: Weighted Directed Graphs
    Requires global topology information for cross-cov. propagation
"""

import logging
from typing import List, Dict
from copy import deepcopy
import numpy as np
import numpy.linalg as la

from sim.helpers import column
import sim.sensor


class EstimatorKCF_WDG(sim.sensor.Sensor):

    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["measurement", "estimate", "noise", "Obs"]
    REQUIRES_GLOBAL_INFO: bool = True

    def __init__(self, all_sensor_ids, **kwargs):

        super().__init__(**kwargs)
        self.all_sensors = all_sensor_ids  # Global information is required

        self.estimate_prior = column(np.array([20, 0]))
        self.ErrCov_prior = 50*np.identity(2)  # For all i, i
        self.CrossCov_prior = np.zeros([2, 2])  # For all i, j pairs

        # Prior and posterior Cross-covariance matrices, where i = self.id
        self.P = {i_ind: {} for i_ind in all_sensor_ids}
        self.M = deepcopy(self.P)

    def initialize(self):
        for i_ind, row in self.P.items():
            for j_ind in self.all_sensors:
                row[j_ind] = self.CrossCov_prior
            row[i_ind] = self.ErrCov_prior

    def do_estimation(self, target_info: dict, all_sensors: Dict[str, sim.sensor.Sensor]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param all_sensors: {"sensor_ID": Sensor }, Global sensor-network information
        """

        _i = self.id
        # Consensus gains Cji are stored as C{i: {j: ..., ...}, ...} where j are neighbors of i
        C_gains = {_id: get_C_gains(_id, all_sensors) for _id in all_sensors.keys()}
        # Kalman gains Ki are stored as K{i: ...}
        K_gains = {_id: get_K_gain(_id, all_sensors, C_gains) for _id in all_sensors.keys()}

        # F := (I - KH)
        F = {_id:
                 (np.identity(2) - K_gains[_id] @ all_sensors[_id].Obs)
             for _id in all_sensors.keys()}

        self.estimate = self.estimate_prior + K_gains[self.id] @ (self.measurement - self.Obs @ self.estimate_prior) \
                        + sum([C_gains[_i][j] @ (all_sensors[j].estimate_prior - self.estimate_prior)
                               for j in self.neighbors])

        # Propagate M_ij
        for i in all_sensors.keys():
            N_i = all_sensors[i].neighbors
            for j in all_sensors.keys():
                N_j = all_sensors[j].neighbors

                self.M[i][j] = F[i] @ self.P[i][j] @ F[j].T

                self.M[i][j] += F[i] @ sum([(self.P[i][s] - self.P[i][j]) @ C_gains[j][s].T for s in N_j])
                self.M[i][j] += (F[j] @ sum([(self.P[j][s] - self.P[j][i]) @ C_gains[i][s].T for s in N_i])).T

                for r in N_i:
                    for s in N_j:
                        self.M[i][j] += C_gains[i][r] \
                                        @ (self.P[r][s] - self.P[r][j] - self.P[i][s] + self.P[i][j]) \
                                        @ C_gains[j][s].T

                if i == j:
                    self.M[i][j] += K_gains[i] @ all_sensors[i].NoiseCov @ K_gains[i].T

        # Propagate P_ij
        for i in all_sensors.keys():
            for j in all_sensors.keys():
                self.P[i][j] = (target_info["A"] @ self.M[i][j] @ target_info["A"].T
                                + target_info["B"] @ target_info["NoiseCov"] @ target_info["B"].T)

        self.ErrCov = self.M[_i][_i]
        self.estimate_prior = target_info["A"] @ self.estimate


def get_C_gains(_id, sensors):
    """
    Compute consensus gains for a sensor
    :param _id: ID of sensor with index i ( as in C_ji )
    :param sensors: All sensors
    :return: dict: {"neighbor_ID": [numpy.array]}
    """
    _i = _id
    sensor = sensors[_id]
    _C_gains = {_id: np.zeros([2, 2]) for _id in sensor.neighbors}

    # Solve matrix equality (using local information)
    A = [[np.zeros([2, 2]) for _ in sensor.neighbors] for _ in sensor.neighbors]
    B = [np.zeros([2, 2]) for _ in sensor.neighbors]
    Del_inv = la.pinv(sensor.NoiseCov + sensor.Obs @ sensor.P[_i][_i] @ sensor.Obs.T)

    for r, _r in enumerate(sensor.neighbors):
        for s, _s in enumerate(sensor.neighbors):
            A[s][r] = ((sensor.P[_s][_i] - sensor.P[_i][_i])
                       @ sensor.Obs.T @ Del_inv @ sensor.Obs
                       @ (sensor.P[_i][_r] - sensor.P[_i][_i]))
            A[s][r] -= (sensor.P[_s][_r] - sensor.P[_s][_i] - sensor.P[_i][_r] + sensor.P[_i][_i])
        B[r] = ((np.identity(2) - sensor.P[_i][_i] @ sensor.Obs.T @ Del_inv @ sensor.Obs)
                @ (sensor.P[_i][_r] - sensor.P[_i][_i]))

    A_inv = la.pinv(np.block(A))
    C = (np.block(B) @ A_inv)

    # Separate C into 2x2 matrices
    for ind, _j in enumerate(sensor.neighbors):
        _C_gains[_j] = C[0:2, ind*2:(ind+1)*2]

    return _C_gains


def get_K_gain(ID, sensors, C_gains):
    """
    Compute Kalman gain for a sensor
    :param ID: Sensor i
    :param sensors: Neighbors
    """
    _i = ID
    sensor = sensors[ID]
    sum_term = sum([C_gains[_i][_r] @ (sensor.P[_r][_i] - sensor.P[_i][_i]) for _r in sensor.neighbors])
    Del_inv = la.pinv(sensor.NoiseCov + sensor.Obs @ sensor.P[_i][_i] @ sensor.Obs.T)
    return (sensor.P[sensor.id][sensor.id] + sum_term) @ sensor.Obs.T @ Del_inv
