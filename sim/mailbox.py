from typing import Dict


class Mailbox:
    """
    Stores and handles messages (to simulate wireless communication between sensors)
    """
    def __init__(self, network):
        """
        :param network: sim.network.Network() object
        """
        sensor_ids = network.sensors.keys()
        self.message_dict = {key: None for key in network.SensorClass.INFO_NEEDED_FROM_NEIGHBORS}
        self.messages: Dict[str, dict] = {sensor_id: self.message_dict for sensor_id in sensor_ids}

    def send(self, sender_id, payload):
        for key, value in payload.items():
            self.messages[sender_id][key] = value

    def receive_from_sensor(self, sender_id):
        return self.messages[sender_id]

    def erase_all(self):
        for key in self.messages.keys():
            self.messages[key] = self.message_dict
