"""
Sensor base class.
Handles measurement/sensing methods, whereas inheriting (Estimator) class handles estimation
"""
import numpy as np
import sim.noise
import sim.errors

from sim.helpers import column
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

        # (Local) topology information
        self.id: str = sensor_id
        self.neighbors: List[str] = neighbors

        # Matrices & Vectors corresponding to measurement
        self.Obs: np.array = np.array(obs_matrix)
        self.NoiseCov: np.array = np.array(noise_cov_matrix)

        self.measurement: np.array = column(np.array([None, None]))
        self.noise = sim.noise.Noise(self.NoiseCov)

        # Matrices and Vectors corresponding to estimation
        self.estimate: np.array = column(np.array([None, None]))
        self.ErrCov: np.array = np.array([
            [None, None],
            [None, None]]
        )
        self.network = None

    def make_measurement(self, target_x: np.array):
        """
        Makes noisy measurement of the target
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()

    def get_target_info(self):
        # TODO
        pass

    def send_messages(self):
        # TODO
        for sensor_ID, sensor in self.sensors.items():
            payload = {key: sensor[key] for key in self.SensorClass.INFO_NEEDED_FROM_NEIGHBORS}
            self.mailbox.send(sensor_ID, payload.copy())

    def receive_messages(self):
        # TODO
        pass

    def __getitem__(self, key):
        return self.__dict__[key]


