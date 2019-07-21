import os
import input.input_output
import input.initialize

def test_read_config():
    filename = os.path.join("input", "ICF-sim.json")
    data = input.input_output.read_config(filename)
    assert "simulation" in data

def test_initialize():
    filename = os.path.join("input", "ICF-sim.json")
    data = input.input_output.read_config(filename)

    input.input_output.sanity_check(data)
    input.initialize.pre_process_target(data["target"])
    input.initialize.pre_process_network(data["network"])
