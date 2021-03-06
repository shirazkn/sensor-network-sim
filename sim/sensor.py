"""
Sensor base class.
Handles measurement/sensing methods, whereas inheriting (Estimator) class handles estimation
"""
import numpy as np
import sim.noise
import sim.errors

from sim.helpers import column, nones, nones_matrix
from typing import List, Dict


class Sensor:
    """
    Base sensor (without estimation logic)
    """

    # (See inheriting sensor class for usage; should be overridden)
    INFO_NEEDED_FROM_TARGET: List[str] = None
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = None
    REQUIRES_GLOBAL_INFO: bool = False

    def __init__(self, sensor_id, neighbors, obs_matrix, noise_cov_matrix):
        target_dim = len(obs_matrix[0])
        measurement_dim = len(obs_matrix)

        # (Local) topology information
        self.id: str = sensor_id
        self.neighbors: List[str] = neighbors

        # Matrices & Vectors corresponding to measurement
        self.Obs: np.array = np.array(obs_matrix)
        self.NoiseCov: np.array = np.array(noise_cov_matrix)

        self.measurement: np.array = column(nones(measurement_dim))
        self.noise = sim.noise.Noise(self.NoiseCov)

        # Matrices and Vectors corresponding to estimation
        self.estimate: np.array = column(nones(target_dim))
        self.ErrCov: np.array = nones_matrix(target_dim, target_dim)

    def initialize(self):
        """
        Inheriting class may use this for pre-processing
        """
        pass

    def make_measurement(self, target_x: np.array):
        """
        Makes noisy measurement of the target
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        raise sim.errors.InvalidSensorClass("The method do_estimation needs to be defined in inherited class.")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
