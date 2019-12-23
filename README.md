## Sensor Network Simulation (WIP)
#### For implementing consensus-based distributed estimation algorithms

Click
[here](https://github.com/shirazkn/sensor-network-sim/blob/master/Simulation.ipynb)
to see a Jupyter Notebook.

### Overview :
This code
- Models target dynamics and sensor measurement models
- Uses OOP to keep track of flow of information between sensors. For eg.
  Each sensor ‘transmits’ and ‘receives’ information to/from its
  neighbors. The information is processed ‘locally’ via classmethods,
  mimicking many of the realistic limitations on such sensor networks.

- Allows for easy extension into realistic sensor network limitations 
  such as packet drops, asynchronous update and bandwidth
  considerations.

- Allows for easy implementation of new estimation algorithms and
  numerical comparison amongst them by running them concurrently

### Installation :
To install requirements, run (using Python 3.5+) :
```
pip3 install -r requirements.txt
```

### Other :
To edit the simulation parameters and target/network characteristics,
edit the json files in `settings/json-files`.

To develop your own estimation algorithm, add a class such as,
```
class My_New_Estimator(sim.sensor.Sensor):
    INFO_NEEDED_FROM_TARGET: List[str] = [...]
    INFO_NEEDED_FROM_NEIGHBORS: List[str] = [...]
    
    @classmethod
    def do_estimation():
        ...

```
See `template.EstimatorTemp.py` for an example.
