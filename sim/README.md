### Code Design

#### Sensors
Sensor class handles functions that are common to all sensors.
Inherited (estimator) classes need to provide methods for doing the estimation and propagating required quantities.
Sensor methods are called by the Network class methods.

#### Messages
Sensor 22 broadcasts message.
Mailbox.messages becomes `["22": {message_dict}]`, and connected sensors can read this.

So total bandwidth usage for communication link between sensors is size(`Message.stream["22"]`)


-------

#### To Do (Maybe):
Generalize to p, q  & r dimensions, instead of 2, 2, 2.
Add helper functions such as make_nxm_matrix(n, m, type="identity") (type can be zeros or none)
type=none is to enforce that we aren't unknowingly initializing anything

Make message update asynchronus using async coroutines

Iterations could probably be made into a class that stores current iteration_count, passed_simulation_time, passed_clock_time, total_iterations (along with `__iter__` and `__next__` methods.
