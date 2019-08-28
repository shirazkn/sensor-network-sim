"""
------------------------------------------------
Optimal Measurement Vector Fusion with Consensus
Shiraz Khan (Research work from Summer '19)
------------------------------------------------
Notes:
    Does not account for cross-covariances

Base Sensor class has Obs, ErrCov, NoiseCov, measurement, estimate..
Prior quantities need to be described here
"""

import logging
from typing import List, Dict
from sim.helpers import column
import sim.sensor
import numpy as np
import numpy.linalg as la


class EstimatorOMVF(sim.sensor.Sensor):
    """
    An example of how an implemented sensor-estimator class could look
    """

    # What information does a sensor need about the target?
    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]

    # What information does the sensor need from its neighbors?
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["estimate_prior", "measurement", "Obs", "ErrCov_prior", "NoiseCov"]

    # If you need an init function, you must also call super().__init__ like this
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.estimate_prior = column(np.array([20, 0]))
        self.ErrCov_prior = np.array(
            [[1.0, 0.0],
             [0.0, 1.0]]
        )
        self.K_gain = {_id: None for _id in (self.neighbors + [self.id])}
        self.C_gain = {_id: None for _id in (self.neighbors + [self.id])}

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param neighbor_info: {"sensor_ID": _dict }, for sensor_ID in cls.neighbors
               _dict = {key: value} for key in INFO_NEEDED_FROM_NEIGHBORS
        """
        # See KCF Raj (2017) for equation numbers.
        _neighbor_info = self.add_self_to_neighbor_info(neighbor_info)

        # Find K and Cs
        self.calc_C_gains(_neighbor_info)
        self.calc_K_gains(_neighbor_info)

        # Calculate Estimate, then propagate prior quantities
        mvf_term = self.mvf_term(_neighbor_info)
        cons_term = self.cons_term(_neighbor_info)
        self.estimate = self.estimate_prior + mvf_term + cons_term
        self.do_propagation(target_info, _neighbor_info)

    def do_propagation(self, target_info, _neighbor_info):

        _, sum_W_inv = get_W_matrices(_neighbor_info)

        self.ErrCov = sum_W_inv
        self.ErrCov_prior = (
            (target_info["A"] @ self.ErrCov @ target_info["A"].T)
            + (target_info["B"] @ target_info["NoiseCov"] @ target_info["B"].T)
        )

        self.estimate_prior = target_info["A"] @ self.estimate

    def calc_C_gains(self, _neighbor_info):
        # Introducing a new matrix, W
        W, sum_W_inv = get_W_matrices(_neighbor_info)

        for j, neighbor in _neighbor_info.items():
            self.C_gain[j] = sum_W_inv @ W[j]

    def calc_K_gains(self, _neighbor_info):
        for j, neighbor in _neighbor_info.items():
            P_j = neighbor["ErrCov_prior"]
            H_j = neighbor["Obs"]
            R_j = neighbor["NoiseCov"]
            del_j_inv = la.inv(R_j + (H_j @ P_j @ H_j.T))

            self.K_gain[j] = self.C_gain[j] @ P_j @ H_j.T @ del_j_inv

            # Applying the Matrix inversion rule, we can also use...
            # R_j_inv = la.inv(neighbor["NoiseCov"])
            # self.K_gain[j] = self.C_gain[j] @ la.inv(la.inv(P_j) + H_j.T @ R_j_inv @ H_j) @ H_j.T @ R_j_inv

    def mvf_term(self, neighbor_info):
        _sum = column(np.array([0.0, 0.0]))
        for j, neighbor in neighbor_info.items():
            _sum += self.K_gain[j] @ (neighbor["measurement"] - (neighbor["Obs"] @ neighbor["estimate_prior"]))
        return _sum

    def cons_term(self, neighbor_info):
        _sum = column(np.array([0.0, 0.0]))
        for j, neighbor in neighbor_info.items():
            _sum += self.C_gain[j] @ (neighbor["estimate_prior"] - self.estimate_prior)
        return _sum


def get_W_matrices(_neighbor_info):
    W = {}
    sum_W = np.zeros([2, 2])
    for j, neighbor in _neighbor_info.items():
        P_j = neighbor["ErrCov_prior"]
        H_j = neighbor["Obs"]
        R_j = neighbor["NoiseCov"]
        Del_j_inv = la.inv(R_j + H_j @ P_j @ H_j.T)

        W[j] = la.inv(P_j - P_j @ H_j @ Del_j_inv @ H_j.T @ P_j)
        sum_W += W[j]

    return W, la.inv(sum_W)
