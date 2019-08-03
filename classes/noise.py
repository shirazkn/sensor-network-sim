"""
Random variables to describe additive white gaussian system and measurement noises
"""
from scipy import stats

class Noise:
    """
    Class to handle sensor and measurement noises
    """

    def __init__(self, _cov):
        """
        Creating Noise object creates persistent random variable
        """
        self.r_var = stats.multivariate_normal(mean=None, cov=_cov)
        self.dim = len(_cov)

    def sample(self):
        """
        Calling Noise object fetches a random sample
        """
        return self.r_var.rvs().reshape(self.dim, 1)

    def update_cov(self, _cov):
        """
        Update co-variance (for eg. sensors with changing noise characteristics)
        """
        if len(_cov) == self.dim:
            self.r_var.cov = _cov
        else:
            raise ValueError("Invalid co-variance")