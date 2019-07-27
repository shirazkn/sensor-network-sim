import json

def read_configs(filenames):
    data = {}
    for filename in filenames:
        with open(filename, "r") as file:
            data.update(json.load(file))
    return data