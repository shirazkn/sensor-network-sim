## Sensor Network Simulation (WIP)
#### For implementing/analyzing consensus-based distributed estimation algorithms

- Models target dynamics, sensor measurement & estimation
- Uses OOP concepts to keep track of flow of information between sensors
For eg. Each sensor ‘transmits’ and ‘receives’ information to/from its neighbors. The information is processed ‘locally’ via classmethods, mimicking many of the realistic limitations on such sensor networks.

- Allows for easy extension into realistic sensor network limitations such as packet drops, asynchronous update and bandwidth considerations.

- Allows for easy implementation of new estimation algorithms and numerical comparison amongst them

#### Here are the instructions to...
### Install :
Install Python 3.5+

Install requirements using,
```
pip3 install -r requirements.txt
```
### Run :
Open Jupyter Notebook using,
```
jupyter notebook main.ipynb
```

### Other :
To edit the simulation parameters and target/sensor characteristics, edit the json files in `settings/json-files`.

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
