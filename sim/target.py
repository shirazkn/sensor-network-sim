"""
Target (the noisy dynamical system being sensed)
"""
import numpy as np
from sim.helpers import column
import sim.noise


def create(input_data):
    """
    Abstracts the __init__ method. Please don't import this directly into namespace!
    :param input_data: result of settings.initialize.do_everything()
    :return: Target class object
    """
    return Target(input_data["target"])


class Target:
    def __init__(self, target_data):
        self.A = np.array(target_data["state"]["ss_A"])
        self.B = np.array(target_data["state"]["ss_B"])
        self.Q = np.array(target_data["noise"])

        self.x = column(np.array(target_data["constraints"]["x_initial"]))
        self.w = sim.noise.Noise(self.Q)

    def update(self):
        self.x = (self.A @ self.x) + (self.B @ self.w.sample())
