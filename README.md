## Sensor Network Simulation (WIP)
#### for testing distributed estimation algorithms

The program is written within the context of consensus-based distributed estimation algorithms. 

The intent is to write modular OOP-based code, so that one can keep track of the flow of information.
For eg. Each sensor ‘transmits’ and ‘receives’ information to/from its neighbors (I would love to make this async, but that’s outside my scope and requirements as of now). The information is processed ‘locally’ via classmethods, mimicking many of the realistic limitations on such sensor networks. 

Also allows for easy extension into real sensor network limitations such as packet drops, asynchronous update, bandwidth considerations...
