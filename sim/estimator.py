import sim.estimators.template
import sim.estimators.KCF_2007
import sim.estimators.ICF_2013
import sim.estimators.SubIVF


def get_estimator(estimation_scheme):
    sensor_params = {}

    if estimation_scheme == "KCF":
        SensorClass = sim.estimators.KCF_2007.EstimatorKCF
        sensor_params = {"epsilon": 0.25}

    elif estimation_scheme == "SIVF":
        SensorClass = sim.estimators.SubIVF.EstimatorSIVF

    elif estimation_scheme == "ICF":
        SensorClass = sim.estimators.ICF_2013.EstimatorICF
        sensor_params = {"epsilon": 0.25}
    else:
        SensorClass = sim.estimators.template.EstimatorTemp
        print("Wrong estimation scheme ; No estimator.py selected!")

    return SensorClass, sensor_params
