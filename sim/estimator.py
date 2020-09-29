import sim.estimators.template
import sim.estimators.KCF_2007
import sim.estimators.ICF_2013
import sim.estimators.OKCF_2017
import sim.estimators.KCF_WDG_2019

EST_SCHEMES = {
    "KCF": {
        "name": "Kalman Consensus Filter",
        "short-name": "KCF",
        "class": sim.estimators.KCF_2007.EstimatorKCF,
        "params": {"epsilon": 0.25},
    },
    "ICF": {
        "name": "Information Consensus Filter",
        "short-name": "ICF",
        "class": sim.estimators.ICF_2013.EstimatorICF,
        "params": {"epsilon": 0.25},
    },
    "OKCF": {
        "name": "Optimal Kalman Consensus Filter",
        "short-name": "Optimal KCF",
        "class": sim.estimators.OKCF_2017.EstimatorOKCF,
    },
    "KCF-WDG": {
        "name": "Kalman Consensus Filter with Weighted Consensus",
        "short-name": "OKCF-WDG",
        "class": sim.estimators.KCF_WDG_2019.EstimatorKCF_WDG,
    },
    "No_Scheme": {
        "name": "-N/A-",
        "short-name": "-N/A-",
        "class": sim.estimators.template.EstimatorTemp
    }
}


def get_estimator(estimation_scheme):
    Est_Scheme_Dict = EST_SCHEMES.get(estimation_scheme, EST_SCHEMES["No_Scheme"])
    return Est_Scheme_Dict["class"], Est_Scheme_Dict.get("params", {})
