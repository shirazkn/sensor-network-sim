"""
KCF estimation Scheme as presented by Olfati-Saber
"""

import logging
from typing import List, Dict
from sim.helpers import column
import sim.sensor
import numpy as np
import numpy.linalg as la


class EstimatorKCF(sim.sensor.Sensor):
    """
    An example of how an implemented sensor-estimator class could look
    """

    # What information does a sensor need about the target?
    INFO_NEEDED_FROM_TARGET: List[str] = ["A", "B", "NoiseCov"]

    # What information does the sensor need from its neighbors?
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["estimate_prior"]

    # If you need an init function, you must also call super().__init__ like this
    def __init__(self, epsilon, **kwargs):

        self.estimate_prior = column(np.array([0, 0]))
        self.ErrCov_prior = column(np.array(
            [[0, 0],
             [0, 0]]
        ))
        self.K_gain = None
        self.C_gain = {_id: None for _id in self.neighbors}

        # Epsilon
        self.eps = epsilon
        super().__init__(**kwargs)

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param neighbor_info: {"sensor_ID": _dict }, for sensor_ID in cls.neighbors
               _dict = {key: value} for key in INFO_NEEDED_FROM_NEIGHBORS
        """

        # See KCF Raj (2017) for equation numbers.

        # Find K and Cs
        self.calc_K_gain()
        self.calc_C_gain()

        # Calculate Estimate, then propagate prior quantities
        eq_7term_2 = self.K_gain @ (self.measurement - (self.Obs @ self.estimate_prior))
        eq_7term_3 = column(np.array([0, 0]))
        for i in self.neighbors:
            eq_7term_3 += self.C_gain[i] @ (neighbor_info[i]["estimate_prior"] - self.estimate_prior)

        self.estimate = self.estimate_prior + eq_7term_2 + eq_7term_3
        self.do_propagation(target_info)

    def calc_K_gain(self):
        eq_24_brackets = self.NoiseCov + (self.Obs @ self.ErrCov_prior @ self.Obs.T)
        eq_24_brackets_inv = eq_24_brackets.inverse()

        self.K_gain = self.ErrCov_prior @ self.Obs.T @ eq_24_brackets_inv

    def calc_C_gain(self):
        for i in self.neighbors:
            self.C_gain[i] = self.eps * (self.ErrCov_prior / 1 + la.norm(self.ErrCov_prior, 'fro'))

    def do_propagation(self, target_info):
        _F = np.identity(2) - self.K_gain @ self.Obs

        self.ErrCov = (_F @ self.ErrCov_prior @ _F.T) + (self.K_gain @ self.NoiseCov @ self.K_gain.T)
        self.ErrCov_prior = ((target_info["A"] @ self.ErrCov @ target_info["A"].T)
                             + (target_info["B"] @ target_info["NoiseCov"] @ target_info["B"]))

        self.estimate_prior = target_info["A"] @ self.estimate