"""
Target of the classes (the noisy dynamical system being sensed)
"""
import numpy as np
from sim.helpers import column
import classes.noise


class Target:
    def __init__(self, target_data):
        self.A = np.array(target_data["state"]["ss_A"])
        self.B = np.array(target_data["state"]["ss_B"])
        self.Q = np.array(target_data["noise"])

        self.x = column(np.array(target_data["constraints"]["x_initial"]))
        self.w = classes.noise.Noise(self.Q)

    def update(self):
        self.x = (self.A @ self.x) + (self.B @ self.w.sample())
