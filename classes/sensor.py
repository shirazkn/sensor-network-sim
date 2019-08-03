"""
Sensor / drone class.
Handles information receiving/sending/processing and estimate propagation.
"""
import numpy as np
from sim.helpers import column

class Sensor:
    def __init__(self, sensor_id, obs_matrix, cov_matrix):
        self.id: int = sensor_id
        self.H: np.ndarray = obs_matrix
        self.R: np.ndarray = cov_matrix

        self.x_hat: np.ndarray = column(np.array([0, 0]))
        self.x_bar: np.ndarray = column(np.array([0, 0]))

    def make_measurement(self, target_x: np.ndarray):
        """
        Measures the target
        :param target_x: Present co-ordinates of the target
        """
        raise NotImplementedError
