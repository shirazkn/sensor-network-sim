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


class EstimatorOIVF(sim.sensor.Sensor):
    """
    An example of how an implemented sensor-estimator.py class could look
    """

    # What information does a sensor need about the target?
    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]

    # What information does the sensor need from its neighbors?
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["estimate_prior", "w", "W"]

    # If you need an init function, you must also call super().__init__ like this
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.estimate_prior = column(np.array([100.0, 0.0]))
        self.ErrCov_prior = np.array(
            [[1000.0, 0.0],
             [0.0, 1000.0]]
        )
        self.C_gain = {_id: None for _id in (self.neighbors + [self.id])}

        self.w = None
        self.W = None

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param neighbor_info: {"sensor_ID": _dict }, for sensor_ID in cls.neighbors
               _dict = {key: value} for key in INFO_NEEDED_FROM_NEIGHBORS
        """
        # _neighbor_info = self.add_self_to_neighbor_info(neighbor_info)

        sum_W = self.W
        for sensor in neighbor_info.values():
            sum_W += sensor["W"]
        self.ErrCov = la.inv(sum_W)

        # Find K and Cs
        self.calc_C_gains(neighbor_info)

        # Calculate Estimate, then propagate prior quantities
        self.estimate = self.estimate_prior + self.ivf_term(neighbor_info) + self.cons_term(neighbor_info)
        self.do_propagation(target_info)

    def do_propagation(self, target_info):
        self.ErrCov_prior = (
            (target_info["A"] @ self.ErrCov @ target_info["A"].T)
            + (target_info["B"] @ target_info["NoiseCov"] @ target_info["B"].T)
        )
        self.estimate_prior = target_info["A"] @ self.estimate

    def calc_C_gains(self, _neighbor_info):
        for j, sensor in _neighbor_info.items():
            self.C_gain[j] = self.ErrCov @ sensor["W"]

    def ivf_term(self, neighbor_info):
        _sum = self.ErrCov @ self.w
        for j, sensor in neighbor_info.items():
            _sum += self.ErrCov @ sensor["w"]
        return _sum

    def cons_term(self, neighbor_info):
        _sum = column(np.array([0.0, 0.0]))
        for j, sensor in neighbor_info.items():
            _sum += self.C_gain[j] @ (sensor["estimate_prior"] - self.estimate_prior)
        return _sum

    def make_measurement(self, target_x: np.array):
        """
        Overrides make_measurement function of base class
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()
        self.W = la.inv(self.ErrCov_prior) + self.Obs.T @ la.inv(self.NoiseCov) @ self.Obs
        self.w = (self.Obs.T @ la.inv(self.NoiseCov)) @ (self.measurement - self.Obs @ self.estimate_prior)

    # def add_self_to_neighbor_info(self, _neighbor_info):
    #     """
    #     Add own info to _neighbor_info dict (to simplify code & notation)
    #     """
    #     _neighbor_info[self.id] = {
    #         _attr: self[_attr]
    #         for _attr in self.INFO_NEEDED_FROM_NEIGHBORS
    #     }
    #     return _neighbor_info

