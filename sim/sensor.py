"""
Sensor / drone class.
Handles information receiving/sending/processing and estimate propagation.
"""
import numpy as np
import sim.noise
import sim.errors

from sim.helpers import column
from typing import List


class Sensor:
    """
    Base sensor (without estimation logic)
    """
    def __init__(self, sensor_id, neighbors, obs_matrix, noise_cov_matrix):

        # Topology information
        self.id: int = sensor_id
        self.neighbors: List[str] = neighbors

        # Matrices & Vectors corresponding to measurement
        self.Obs: np.ndarray = obs_matrix
        self.NoiseCov: np.ndarray = noise_cov_matrix

        self.measurement: np.ndarray = column(np.ndarray([0, 0]))
        self.noise = sim.noise.Noise(self.Cov)

        # Matrices and Vectors corresponding to estimation
        self.estimate: np.ndarray = column(np.ndarray([0, 0]))
        self.ErrCov: np.ndarray = np.ndarray([
            [0, 0],
            [0, 0]]
        )

    def make_measurement(self, target_x: np.ndarray):
        """
        Measures the target
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()

    def do_estimation(self, kwargs):
        raise sim.errors.InvalidSensorClass("The method do_estimation needs to be defined in inherited class.")


class Sensor_Template(Sensor):
    """
    An example of how an implemented sensor-estimator class could look
    """
    INFO_NEEDED_FROM_TARGET: List[str] = {}

    # The keys that should be in a 'message'. i.e. All the quantities that a sensor needs to share with neighbor.
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = {}

    def calculate_gains(self, kwargs):
        pass
