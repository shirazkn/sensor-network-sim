"""
Scratchpad for dumping tests. You might be looking for the jupyter notebook
Please don't read this file, Not going to update this after every refactor
"""

# Import modules
import os
import settings.input
import settings.initialize

import sim.target
import sim.network

# Get settings files
simulation_file = os.path.join("settings","json_files", "simulation",  "ICF-sim.json")
sensor_network_file = os.path.join("settings","json_files", "sensor_network",  "ICF-sensor-network.json")

# Read settings files
raw_data = settings.input.read_configs([simulation_file, sensor_network_file])
input_data  = settings.initialize.do_everything(raw_data)

target = sim.target.create(input_data)
network = sim.network.create(input_data)

# NETWORK CREATION
for i in range(0,7):
    try:
        s = network.get_sensor(i)
        print(str(s.id))
        print(str(s.H))
        print(str(s.R))
    except:
        print("Oops")

