"""
------------------------------------------------
Optimal Kalman Consensus Filter
R. Deshmukh, C. Kwon, I. Hwang (2017)
------------------------------------------------
Notes:
    Uses cross-covariance matrices
    Requires global topology information
"""

from typing import List, Dict
from sim.helpers import column
import sim.sensor
import numpy as np
import numpy.linalg as la
from copy import deepcopy


class EstimatorOKCF(sim.sensor.Sensor):

    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["measurement", "estimate", "noise", "Obs"]
    REQUIRES_GLOBAL_INFO: bool = True

    def __init__(self, all_sensor_ids, **kwargs):

        super().__init__(**kwargs)
        self.all_sensors = all_sensor_ids  # Global information is required
        self.x_dim = len(self.estimate)
        self.estimate_prior = deepcopy(self.estimate)
        self.ErrCov_prior = deepcopy(self.ErrCov)
        self.CrossCov_prior = np.zeros([self.x_dim, self.x_dim])  # For all i, j pairs

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
        C_gains = {_id: self.get_C_gain(_id, sensor) for _id, sensor in all_sensors.items()}
        K_gains = {_id: self.get_K_gain(_id, all_sensors, C_gains[_id]) for _id in all_sensors.keys()}

        # F := (I - KH)
        F = {_id: (np.identity(self.x_dim) - K_gains[_id] @ all_sensors[_id].Obs) for _id in all_sensors.keys()}

        self.estimate = self.estimate_prior \
                        + K_gains[self.id] @ (self.measurement - self.Obs @ self.estimate_prior) \
                        + C_gains[_i] @ sum([all_sensors[j].estimate_prior - self.estimate_prior
                                             for j in self.neighbors])

        # Propagate M_ij
        for i in all_sensors.keys():
            N_i = all_sensors[i].neighbors
            for j in all_sensors.keys():
                N_j = all_sensors[j].neighbors

                self.M[i][j] = F[i] @ self.P[i][j] @ F[j].T

                self.M[i][j] += F[i] @ sum([(self.P[i][s] - self.P[i][j]) for s in N_j]) @ C_gains[j].T
                self.M[i][j] += (F[j] @ sum([(self.P[j][s] - self.P[j][i]) for s in N_i]) @ C_gains[i].T).T

                for r in N_i:
                    for s in N_j:
                        self.M[i][j] += C_gains[i] \
                                        @ (self.P[r][s] - self.P[r][j] - self.P[i][s] + self.P[i][j]) \
                                        @ C_gains[j].T

                if i == j:
                    self.M[i][j] += K_gains[i] @ all_sensors[i].NoiseCov @ K_gains[i].T

        # Propagate P_ij
        for i in all_sensors.keys():
            for j in all_sensors.keys():
                self.P[i][j] = (target_info["A"] @ self.M[i][j] @ target_info["A"].T
                                + target_info["B"] @ target_info["NoiseCov"] @ target_info["B"].T)

        self.ErrCov = self.M[_i][_i]
        self.estimate_prior = target_info["A"] @ self.estimate

    def get_C_gain(self, _i, sensor):
        """
        Compute consensus gain for a sensor
        :param _i: ID of sensor
        :param sensor: Sensor object
        :return: numpy.array
        """
        Del_inv = la.pinv(sensor.NoiseCov + sensor.Obs @ sensor.P[_i][_i] @ sensor.Obs.T)
        D = np.zeros([self.x_dim, self.x_dim])
        L = np.zeros([self.x_dim, self.x_dim])
        for _r in sensor.neighbors:
            for _s in sensor.neighbors:
                D += sensor.P[_r][_s] - sensor.P[_r][_i] - sensor.P[_i][_s] + sensor.P[_i][_i]
            L += sensor.P[_r][_i] - sensor.P[_i][_i]

        G = D - L @ sensor.Obs.T @ Del_inv @ sensor.Obs @ L.T
        return (sensor.P[_i][_i] @ sensor.Obs.T @ Del_inv @ sensor.Obs - np.identity(self.x_dim)) @ L.T @ la.pinv(G)

    def get_K_gain(self, _i, sensors, C_gain):
        """
        Compute Kalman gain for a sensor
        :param _i: Sensor i
        :param sensors: Neighbors
        :param C_gain: Consensus gain of sensor i
        """
        sensor = sensors[_i]
        Del_inv = la.pinv(sensor.NoiseCov + sensor.Obs @ sensor.P[_i][_i] @ sensor.Obs.T)
        L = np.zeros([self.x_dim, self.x_dim])
        for _r in sensor.neighbors:
            L += sensor.P[_r][_i] - sensor.P[_i][_i]

        return (sensor.P[sensor.id][sensor.id] + C_gain @ L) @ sensor.Obs.T @ Del_inv
