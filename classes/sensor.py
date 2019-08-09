"""
Sensor / drone class.
Handles information receiving/sending/processing and estimate propagation.
"""
import numpy as np
import classes.noise
from sim.helpers import column


class Sensor:
    def __init__(self, sensor_id, neighbors, obs_matrix, cov_matrix):

        # Topology information
        self.id: int = sensor_id
        self.neighbors = neighbors

        self.H: np.ndarray = obs_matrix
        self.R: np.ndarray = cov_matrix

        self.z: np.ndarray = column(np.ndarray([0, 0]))
        self.x_hat: np.ndarray = column(np.array([0, 0]))
        self.x_bar: np.ndarray = column(np.array([0, 0]))
        self.v = classes.noise.Noise(self.R)

    def make_measurement(self, target_x: np.ndarray):
        """
        Measures the target
        :param target_x: Present co-ordinates of the target
        """
        self.z = (self.H @ target_x) + self.v.sample()


class Sensor_KCF(Sensor):
    def calculate_gains(self):
        raise NotImplementedError
