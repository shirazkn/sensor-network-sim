import json
import logging
from json_minify import json_minify


def read_configs(filenames):
    data = {}
    for filename in filenames:
        logging.debug("Reading the file %s...", filename)
        with open(filename, "r") as file:
            raw_data = file.read()
            data.update(json.loads(raw_data))
    return data
