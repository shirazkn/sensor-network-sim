import json
import logging
import settings.initialize


def read(filenames):
    data = {}
    for filename in filenames:
        logging.debug("Reading the file %s...", filename)
        with open(filename, "r") as file:
            raw_data = file.read()
            data.update(json.loads(raw_data))

    return settings.initialize.do_everything(data)

