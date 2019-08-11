from typing import Dict


class Messages:
    def __init__(self, network):
        """
        List of message_dicts. Message_dict structure varies based on estimation algorithm
        """
        sensor_ids = network.get_sensors().keys()
        # TODO fill message_dict into this dict. Build dict based on some footprint stored in Sensor Class.
        # message_dict = Network.MESSAGE_DICT
        self.stream: Dict[dict] = {sensor_id: message_dict for sensor_id in sensor_ids}

    def add(self, sender_id, payload):
        for key, value in payload.items():
            self.stream[sender_id][key] = value

    def get_from_sensor(self, sender_id):
        return self.stream[sender_id]

