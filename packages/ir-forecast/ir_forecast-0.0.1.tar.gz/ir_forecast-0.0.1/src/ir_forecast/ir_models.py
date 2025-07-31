import numpy as np
import pandas as pd

class VasicekModel():

    def __init__(self, theta: float, mu: float, sigma: float, r0: float,
                 T: float = 1.0,
                 N: int = 252):
        """
        Discrete Vasicek model for forecasting interest rates.

        Parameters
        ----------
        theta: `float`
            Speed of the reversion to the mean
        mu: `float`
            Long-term mean interest rate
        sigma: `float`
            Interest rate volatility
        r0: `float`
            Initial interest rate
        T: `float` = 1.0
            Time horizon in years
        N: `int` = 252
            The number of time steps to simulate
        """

        self.__theta = theta
        self.__mu = mu
        self.__sigma = sigma
        self.__r0 = r0
        self.__T = T
        self.__N = N
        
        self.__dt = T/N # size of a single time step (dt = 1/252 is one business day)
        self.__rates = np.zeros(self.__N)

    def get_rates(self):
        """
        Returns the simulated interest rates.

        The interest rates are returned from the current point of time (t = 0) to the specified time horizon (T).
        """

        self.__rates[0] = self.__r0 # start from the initial interest rate

        # dr = theta * (mu-r[t-1]) * dt + sigma * sqrt(dt) * rand_normal
        # rate[t] = rate[t-1] + dr
        for t in range(1,self.__N):
            dr = self.__theta * (self.__mu - self.__rates[t-1]) * self.__dt + self.__sigma * np.sqrt(self.__dt) * np.random.normal()
            self.__rates[t] = self.__rates[t-1] + dr

        return self.__rates
    
    def get_params(self):
        """Returns the model parameters as a dictionary."""

        return {"theta":self.__theta,
                "mu":self.__mu,
                "sigma":self.__sigma,
                "r0":self.__r0,
                "T":self.__T,
                "N":self.__N,
                "dt":self.__dt}
    
class CIRModel():

    def __init__(self, theta: float, mu: float, sigma: float, r0: float,
                 T: float = 1.0,
                 N: int = 252):
        """
        Discrete Cox-Ingersoll-Ross model for forecasting interest rates.

        Parameters
        ----------
        theta: `float`
            Speed of the reversion to the mean
        mu: `float`
            Long-term mean interest rate
        sigma: `float`
            Interest rate volatility
        r0: `float`
            Initial interest rate
        T: `float` = 1.0
            Time horizon in years
        N: `int` = 252
            The number of time steps to simulate
        """

        self.__theta = theta
        self.__mu = mu
        self.__sigma = sigma
        self.__r0 = r0
        self.__T = T
        self.__N = N
        
        self.__dt = T/N
        self.__rates = np.zeros(self.__N)

    def get_rates(self):
        """
        Returns the simulated interest rates.

        The interest rates are returned from the current point of time (t = 0) to the specified time horizon (T).
        """

        self.__rates[0] = self.__r0 # start from the initial interest rate

        # dr = theta * (mu-r[t-1]) * dt + sigma * sqrt(dt) * rand_normal
        # rate[t] = rate[t-1] + dr
        for t in range(1,self.__N):
            dr = self.__theta * (self.__mu - self.__rates[t-1]) * self.__dt + self.__sigma * np.sqrt(self.__dt) * np.sqrt(max(0,self.__rates[t-1])) * np.random.rand()
            self.__rates[t] = self.__rates[t-1] + dr

        return self.__rates
    
    def get_params(self):
        """Returns the model parameters as a dictionary."""

        return {"theta":self.__theta,
                "mu":self.__mu,
                "sigma":self.__sigma,
                "r0":self.__r0,
                "T":self.__T,
                "N":self.__N,
                "dt":self.__dt}

if __name__ == "__main__":
    pass