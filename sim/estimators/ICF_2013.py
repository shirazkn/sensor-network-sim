"""
------------------------
Information Consensus Filter (2013)
Implemented with a single consensus iteration per estimation iteration
------------------------
Notes:
    Sub-optimal gains

"""

import logging
from typing import List, Dict
from sim.helpers import column
import sim.sensor
import numpy as np
import numpy.linalg as la


class EstimatorICF(sim.sensor.Sensor):

    # What information does a sensor need about the target?
    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]

    # What information does the sensor need from its neighbors?
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["v", "V"]

    # If you need an init function, you must also call super().__init__ like this
    def __init__(self, epsilon, **kwargs):

        super().__init__(**kwargs)
        self.estimate_prior = column(np.array([20, 0]))
        self.ErrCov_prior = np.array(
            [[1.0, 0.0],
             [0.0, 1.0]]
        )
        self.v = None
        self.V = None

        # Epsilon
        self.eps = epsilon

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param neighbor_info: {"sensor_ID": _dict }, for sensor_ID in cls.neighbors
               _dict = {key: value} for key in INFO_NEEDED_FROM_NEIGHBORS
        """
        N = len(self.neighbors)
        cons_V = self.V
        cons_v = self.v
        for neighbor in neighbor_info.values():
            cons_V += self.eps*(neighbor["V"] - self.V)
            cons_v += self.eps*(neighbor["v"] - self.v)

        self.estimate = la.inv(cons_V) @ cons_v
        self.ErrCov = la.inv(N*cons_V)
        self.do_propagation(target_info)

    def do_propagation(self, target_info):
        self.ErrCov_prior = ((target_info["A"] @ self.ErrCov @ target_info["A"].T)
                             + (target_info["B"] @ target_info["NoiseCov"] @ target_info["B"]))

        self.estimate_prior = target_info["A"] @ self.estimate

    def make_measurement(self, target_x: np.array):
        """
        Overrides make_measurement function of base class
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()

        N = len(self.neighbors)
        self.V = (la.inv(self.ErrCov_prior) / N) + self.Obs.T @ la.inv(self.NoiseCov) @ self.Obs
        self.v = ((la.inv(self.ErrCov_prior)/N) @ self.estimate_prior
                  + self.Obs.T @ la.inv(self.NoiseCov) @ self.measurement)
