## Sensor Network Simulation (WIP)
#### For testing distributed estimation algorithms

The program is written within the context of consensus-based distributed estimation algorithms. 

The intent is to write modular OOP-based code, so that one can keep track of the flow of information.
For eg. Each sensor ‘transmits’ and ‘receives’ information to/from its neighbors. The information is processed ‘locally’ via classmethods, mimicking many of the realistic limitations on such sensor networks. 

Also allows for easy extension into real sensor network limitations such as packet drops, asynchronous update and bandwidth considerations.

#### Here are the instructions to...
### Install :
Requires Python 3.5+

Install requirements using,
```
pip3 install -r requirements.txt
```
### Run :
Open Jupyter Notebook using,
```
jupyter notebook main.ipynb
```
Press `shift+enter` to execute cells sequentially.
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
See `template.EstimatorTemp` for the exact details.
