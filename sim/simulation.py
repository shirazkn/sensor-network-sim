import sim.target
import sim.network
import sim.history

import numpy as np


def simulate(input_data, duration=100, est_scheme=None):
    input_data["scheme"] = est_scheme if est_scheme else input_data["scheme"]

    target = sim.target.create(input_data)
    network = sim.network.create(input_data)
    sim_history = sim.history.create(network)

    for t in range(duration):
        sim_history.add_target(target.x)

        network.make_measurements(target.x)
        network.share_info_with_neighbors()
        network.get_info_about_target(target)
        network.do_estimations()

        sim_history.add_estimates(network)
        target.update()

    return sim_history


def simulate_many(input_data, duration=100, est_schemes=None, sensor_initials=None):

    target = sim.target.create(input_data)
    networks = []
    simulations = []

    for est_scheme in est_schemes:
        input_data["scheme"] = est_scheme if est_scheme else input_data["scheme"]
        networks.append(sim.network.create(input_data))
        simulations.append(sim.history.create(networks[-1]))

        if sensor_initials:
            for sensor in networks[-1].sensors.values():
                sensor.ErrCov_prior = np.array(sensor_initials["ErrCov_prior"])
                sensor.estimate_prior = np.array(sensor_initials["estimate_prior"])
                # print(sensor.estimate_prior)

    for t in range(duration):
        for _sim in simulations:
            _sim.add_target(target.x)

        for i, network in enumerate(networks):
            network.make_measurements(target.x)
            network.share_info_with_neighbors()
            network.get_info_about_target(target)
            network.do_estimations()
            simulations[i].add_estimates(network)

        target.update()

    return simulations
