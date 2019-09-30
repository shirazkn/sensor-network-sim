import sim.target
import sim.network
import sim.history


def simulate(input_data, duration=100):
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
