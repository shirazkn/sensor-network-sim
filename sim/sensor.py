"""
Sensor base class.
Handles measurement/sensing methods, whereas inheriting class handles estimation
"""
import numpy as np
import sim.noise
import sim.errors
import sim.estimators

from sim.helpers import column
from typing import List, Dict


class Sensor:
    """
    Base sensor (without estimation logic)
    """

    # (See inheriting sensor class for usage; should be overridden)
    INFO_NEEDED_FROM_TARGET: List[str] = None
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = None

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

    def make_measurement(self, target_x: np.array):
        """
        Makes noisy measurement of the target
        :param target_x: Present co-ordinates of the target
        """
        self.measurement = (self.Obs @ target_x) + self.noise.sample()

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        raise sim.errors.InvalidSensorClass("The method do_estimation needs to be defined in inherited class.")

    def __getitem__(self, key):
        return self.__dict__[key]


def get_estimator(estimation_scheme):
    sensor_params = {}

    if estimation_scheme == "KCF":
        SensorClass = sim.estimators.KCF_2007.EstimatorKCF
        sensor_params = {"epsilon": 0.25}

    elif estimation_scheme == "OMVF":
        SensorClass = sim.estimators.OptimalMVF.EstimatorOMVF

    elif estimation_scheme == "ICF":
        SensorClass = sim.estimators.ICF_2013.EstimatorICF
        sensor_params = {"epsilon": 0.25}
    else:
        SensorClass = sim.estimators.template.EstimatorTemp
        print("Wrong estimation scheme ; No estimator selected!")

    return SensorClass, sensor_params
