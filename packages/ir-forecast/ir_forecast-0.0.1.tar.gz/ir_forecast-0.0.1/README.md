# Interest Rate Forecasting

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Work with historical Euribor data and forecast interest rates utilizing stochastic models and Monte Carlo simulations.

## Features

- Fetch historical Euribor data from 1999 onwards by maturity in standardized format
- Initialize discrete Vasicek and Cox-Ingersoll-Ross models 
- Simulate and visualize interest rate paths with Monte Carlo simulations
## Requirements

NumPy, pandas and Matplotlib are required:

```
pip install numpy
pip install pandas
pip install matplotlib
```

The Anaconda distribution for Python is recommended, which includes all the requirements:

https://www.anaconda.com/download
## Installation

Install with pip:

```
pip install ir_forecast
```
## Example

This example shows how to fetch historical Euribor data, initialize the interest rate models and simulate them with Monte Carlo.
### Fetching Euribor Data

Historical Euribor data is available for the following maturities:
- 1 week
- 1 month
- 3 months
- 6 months
- 12 months

```
from interest_rates import Euribor

r = Euribor(maturity="3 months")
```

There are four methods for fetching the data:

- `get_current()`
- `get_daily(start: str, end: str)`
- `get_monthly(start: str, end: str)`
- `get_yearly(start: str, end: str)`

The `get_current()` method returns the most recent rate of the previous business day as a float, whereas the others return date indexed DataFrames for the user specified date ranges:

```
monthly = r.get_monthly(start="2024/01", end="2025/07")
print(monthly)
```

| Date       | Euribor (3 months) |
| :--------- | -----------------: |
| 2024-01-01 |            0.03905 |
| 2024-02-01 |            0.03884 |
| 2024-03-01 |            0.03938 |
| 2024-04-01 |            0.03883 |
| 2024-05-01 |            0.03853 |
| 2024-06-03 |            0.03782 |
| 2024-07-01 |            0.03709 |
| 2024-08-01 |            0.03638 |
| 2024-09-02 |            0.03469 |
| 2024-10-01 |            0.03252 |
| 2024-11-01 |            0.03085 |
| 2024-12-02 |            0.02924 |
| 2025-01-01 |            0.02736 |
| 2025-02-03 |            0.02562 |
| 2025-03-03 |            0.02464 |
| 2025-04-01 |            0.02324 |
| 2025-05-01 |            0.02142 |
| 2025-06-02 |            0.01979 |
| 2025-07-01 |            0.01961 |
### Initializing Interest Rate Models

The package contains two stochastic models for forecasting interest rates:
- Vasicek Model
- Cox-Ingersoll-Ross Model

For theoretical background on the models, see:<br>
https://en.wikipedia.org/wiki/Vasicek_model<br>
https://en.wikipedia.org/wiki/Cox%E2%80%93Ingersoll%E2%80%93Ross_model

Both models are initialized with the following parameters:
- theta: the mean reversion speed
- mu: the long-term mean interest rate
- sigma: interest rate volatility
- r0: the initial/current interest rate
- T: time horizon in years (default 1)
- N: the number of time steps to simulate (default 252, the amount of business days in a year)

Let's assume an arbitrary example with a mean reversion speed of 0.5, long-term mean interest rate of 2%, 0.2 volatility and an initial interest rate of 4%:

```
from ir_models import VasicekModel, CIRModel

theta_val = 0.5
mu_val = 0.02
vol = 0.2
initial = 0.04

# Use default T = 1 and N = 252 for both models
vasicek = VasicekModel(theta=theta_val,
                       mu=mu_val,
                       sigma=volatility,
                       r0=initial)

cir = CIRModel(theta=theta_val,
               mu=mu_val,
               sigma=volatility,
               r0=initial)
```
### Simulating Interest Rate Paths with Monte Carlo

> [!IMPORTANT]
> The example below is a result of a random process.

Simulate the Vasicek Model with 100 Monte Carlo simulation runs:

```
from monte_carlo import MonteCarlo

vasicek_mc = MonteCarlo(model=vasicek,
                        number_of_simulations=100)
```

The `results()` method returns a DataFrame with each column representing a single simulation run. The `visualize()` method shows the simulated interest rate paths alongside with 0.9, 0.5 and 0.1 quantiles:

```
vasicek_mc.visualize()
```

![Image of the simulated interest rate paths.](mc_example.png)

The `stats()` method shows summary statistic of the simulation:

```
print(vasicek_mc.stats())
```

|                            |   Results for 100 simulations |
|:---------------------------|------------------------------:|
| Initial Interest Rate (r0) |                     0.04      |
| Long-Term Mean (mu)        |                     0.02      |
| 90% quantile               |                     0.197756  |
| 50% quantile               |                     0.0150644 |
| 10% quantile               |                    -0.15431   |