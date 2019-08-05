"""
Make network class object, etc
"""
import classes.network


def create(input_data):
    network = classes.network.Network()
    network.create_sensors(input_data["network"])
    return network
