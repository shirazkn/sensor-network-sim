import numpy as np
from sim.helpers import column
import sim.noise
from copy import deepcopy


class Target:
    """
    Handles target dynamics
    'Target' = System to be estimated
    """
    def __init__(self, target_data):
        self.A = np.array(target_data["state_space"]["ss_A"])
        self.B = np.array(target_data["state_space"]["ss_B"])
        self.NoiseCov = np.array(target_data["noise_covariance"])

        self.x = column(np.array(target_data["constraints"]["x_initial"]))
        self.noise = sim.noise.Noise(self.NoiseCov)

    def update(self):
        self.x = (self.A @ self.x) + (self.B @ self.noise.sample())

    def __getitem__(self, key):
        return self.__dict__[key]


def create(input_data):
    """
    :param input_data: result of settings.initialize.do_everything()
    :return: Target class object
    """
    _data = deepcopy(input_data["target"])
    return Target(_data)