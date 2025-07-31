import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ir_models import *

class MonteCarlo():

    def __init__(self, model: VasicekModel | CIRModel, number_of_simulations: int):
        """
        Monte Carlo simulation for Vasicek and Cox-Ingersoll-Ross models.
        
        Parameters
        ----------
        model: `VasicekModel` | `CIRModel`
            The interest rate model to simulate
        number_of_simulations: `int`
            The number of Monte Carlo simulations to run
        """

        self.__model = model
        self.__nsims = number_of_simulations
        self.__params = model.get_params()

        # N rows, number_of_simulation columns
        self.__all_sims = np.zeros((self.__params["N"],number_of_simulations))
        self.__run(number_of_simulations)


    # Methods for showing the results, summary statistics and visualization

    def results(self):
        """
        Returns the Monte Carlo simulation results as a DataFrame.
        
        The results for each simulation run are in their respective columns.
        """

        df = pd.DataFrame(self.__all_sims)
        df.index.name = "Time step"
        df.columns = [f"Simulation {i}" for i in range(1,len(df.columns) + 1)]
        return df
    
    def stats(self):
        """Returns summary statistics of the simulation results."""

        qs = self.__quantiles()
        q1 = qs["q1"].iloc[-1]
        q5 = qs["q5"].iloc[-1]
        q9 = qs["q9"].iloc[-1]

        labels = ["Initial Interest Rate (r0)",
                  "Long-Term Mean (mu)",
                  "90% quantile",
                  "50% quantile",
                  "10% quantile"]
        
        data = [self.__params["r0"],
                self.__params["mu"],
                q9,
                q5,
                q1]

        df = pd.DataFrame(data=data,
                          index=labels,
                          columns=[f"Results for {self.__nsims} simulations"])

        return df
        
    def visualize(self):
        """Visualizes the simulated interest rate paths."""

        df = self.results()
        q = self.__quantiles()

        fig,ax = plt.subplots()
        ax.set_xlim([0,self.__params["N"]])

        for c in df.columns:
            plt.plot(df[c],linewidth=0.5)

        plt.plot(q["q9"],"--",color="0.3",label=".9 quantile")
        plt.plot(q["q5"],"k--",label=".5 quantile")
        plt.plot(q["q1"],"--",color="0.3",label=".1 quantile")

        plt.legend()
        plt.show()

    
    # Hidden methods for calculations

    def __run(self, n: int):
        """Run the Monte Carlo simulation."""

        for i in range(n):
            self.__all_sims[:,i] = self.__model.get_rates()

    def __quantiles(self):
        """Returns the .1, .5 and .9 quantiles of the simulation"""

        df = self.results()

        q1 = df.quantile(q=0.1,axis=1)
        q5 = df.quantile(axis=1) #default 0.5
        q9 = df.quantile(q=0.9,axis=1)

        quantiles = pd.DataFrame({"q1":q1,"q5":q5,"q9":q9})

        return quantiles

if __name__ == "__main__":
    pass