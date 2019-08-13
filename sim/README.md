### Code Design

#### Sensors
Sensor class handles functions that are common to all sensors.
Inherited classes need to provide methods for doing the estimation and propagating required quantities.
Most (possibly all) Sensor methods are called by the Network class methods.

Inherited Sensors must also take charge of tracking what information is transmitted and received. As a rule of hand, the structure of the message transmitted should be the same as that of the message expected to be received.
Not sure if there should be a Network method that checks this.

#### Messages
Sensor 22 broadcasts message.
Message.stream becomes `["22": {message_dict}]`

Total bandwidth usage for a single unidirectional communication link between sensors is size(`Message.stream["22"]`)

So adjacent sensors 23 & 24 can ask for `Message.stream["22"]`.

When 22 has an updated message for everyone, it patches the new information into the message stream_list.

-------

#### To Do (Maybe):
Instead of sticking to 2D estimation, create template objects for dimensions and reuse them. For eg. store column([0,0]) object and invoke that wherever you need a 2D vector.
Add helper functions such as make_nxm_matrix(n, m, type="identity") (type can be zeros or none)
type=none is to enforce that we aren't unknowingly initializing anything

Make message update asynchronus using async coroutines

Iterations could probably be made into a class that stores current iteration_count, passed_simulation_time, passed_clock_time, total_iterations (along with `__iter__` and `__next__` methods.
