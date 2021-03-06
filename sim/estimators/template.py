"""
An example of how to implement your own sensor-estimator.py.
This is the only extra file you should have to create.
"""

from typing import List, Dict
import sim.sensor


class EstimatorTemp(sim.sensor.Sensor):
    """
    An example of how an implemented sensor-estimator.py class could look
    """

    # What information does a sensor need about the target?
    INFO_NEEDED_FROM_TARGET: List[str] = ["A"]

    # What information does the sensor need from its neighbors?
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = ["measurement"]

    def do_estimation(self, target_info: dict, neighbor_info: Dict[str, dict]):
        """
        :param target_info: {key: value} for key in INFO_NEEDED_FROM_TARGET
        :param neighbor_info: {"sensor_ID": _dict }, for sensor_ID in cls.neighbors
               _dict = {key: value} for key in INFO_NEEDED_FROM_NEIGHBORS
        """
        self.estimate = self.measurement
