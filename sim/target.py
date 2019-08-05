"""
Target functions
"""
import classes.target


def create(input_data):
    return classes.target.Target(input_data["target"])
