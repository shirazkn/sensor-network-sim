from typing import Dict


class Messages:
    def __init__(self, network):
        """
        List of message_dicts. Message_dict structure varies based on estimation algorithm
        """
        sensor_ids = network.sensors.keys()

        message_dict = {key: None for key in network.SensorClass.INFO_NEEDED_FROM_NEIGHBORS}
        self.all: Dict[str, dict] = {sensor_id: message_dict for sensor_id in sensor_ids}

    def send(self, sender_id, payload):
        for key, value in payload.items():
            self.all[sender_id][key] = value

    def receive_from_sensor(self, sender_id):
        return self.all[sender_id]

