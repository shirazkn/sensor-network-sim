import json
import logging

def read_configs(filenames):
    data = {}
    for filename in filenames:
        logging.debug("Reading the file %s...", filename)
        with open(filename, "r") as file:
            data.update(json.load(file))
    return data