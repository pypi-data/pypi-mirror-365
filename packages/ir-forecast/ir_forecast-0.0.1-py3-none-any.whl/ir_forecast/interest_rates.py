import pandas as pd
import numpy as np
from typing import Literal

class Euribor():

    def __init__(self, maturity: Literal["1 week",
                                         "1 month",
                                         "3 months",
                                         "6 months",
                                         "12 months"]):
        """
        Fetch Euribor rates of a given maturity.

        Parameters
        ----------
        maturity: `str`
            The Euribor's maturity
        """

        self.__maturity = maturity


    # Getters for current, daily, monthly and yearly Euribor rates

    def get_current(self):
        """Returns the Euribor rate of the previous business day."""

        return self.get_daily().iloc[0,0]

    def get_daily(self):
        """Returns the daily Euribor rates from the last 10 business days."""

        df = self.__fetch_by_day()
        df.rename(columns={1: f"Euribor ({self.__maturity})"},
                  inplace=True)

        return df
    
    def get_monthly(self, start: str, end: str):
        """
        Returns monthly rates from the first day of the month in the given date range.
        
        Parameters
        ----------
        start: `str`
            The start date in "YYYY/mm" format
        end: `str`
            The end date in "YYYY/mm" format
        """

        # For slicing the df without days if the user provides them nevertheless
        s = pd.to_datetime(start).strftime("%Y/%m")
        e = pd.to_datetime(end).strftime("%Y/%m")

        df = self.__concat(s,e)
        df.rename(columns={0:f"Euribor ({self.__maturity})"},inplace=True)

        return df[s:e]
    
    def get_yearly(self, start: str, end: str):
        """
        Returns the yearly rates from the first day of the year in the given date range.
        
        Parameters
        ----------
        start: `str`
            The start date in "YYYY" format
        end: `str`
            The end date in "YYYY" format
        """

        # For slicing the df without months and days if the user provides them nevertheless
        s = pd.to_datetime(start).strftime("%Y")
        e = pd.to_datetime(end).strftime("%Y")

        df = self.__concat(s,e)
        mask = df.index.month == 1
        df.rename(columns={0:f"Euribor ({self.__maturity})"},inplace=True)

        return df[mask]
    

    # Aggregate methods

    def mean(self, start: str = "1999", end: str = str(pd.Timestamp.today().year)):
        """
        Returns the mean of the Euribor rate for the specified date range.
        
        By default the mean is calculated from January 1999 to the current date with monthly precision.

        Parameters
        ----------
        start: `str` = "1999"
            The start date for calculating the mean
        end: `str` = str(pd.Timestamp.today().year)
            The end date for calculating the mean
        """

        df = self.__concat(start,end)

        return round(df[0].mean(),5)
    
    def variance(self, start: str = "1999", end: str = str(pd.Timestamp.today().year)):
        """
        Returns the variance of the Euribor rate for the specified date range.
        
        By default the variance is calculated from January 1999 to the current date with monthly precision.

        Parameters
        ----------
        start: `str` = "1999"
            The start date for calculating the variance
        end: `str` = str(pd.Timestamp.today().year)
            The end date for calculating the variance
        """
        
        df = self.__concat(start,end)

        values_a = np.array(df[0])
        mean_a = np.full(len(values_a),values_a.mean())
        deviation_a = values_a - mean_a
        d_squared_a = deviation_a ** 2
        variance = d_squared_a.sum() / len(values_a)

        return variance
    
    def std(self, start: str = "1999", end: str = str(pd.Timestamp.today().year)):
        """
        Returns the standard deviation of the Euribor rate for the specified date range.
        
        By default the standard deviation is calculated from January 1999 to the current date with monthly precision.

        Parameters
        ----------
        start: `str` = "1999"
            The start date for calculating the standard deviation
        end: `str` = str(pd.Timestamp.today().year)
            The end date for calculating the standard deviation
        """
        
        return np.sqrt(self.variance(start,end))


    # Hidden methods for web scraping and calculations
    
    def __concat(self, s: str, e: str):
        """Returns the monthly rates for several years in a single DataFrame."""

        s_year = pd.to_datetime(s).year
        e_year = pd.to_datetime(e).year
        y_range = range(s_year,e_year + 1)

        df_list = [self.__fetch_by_year(year) for year in y_range]

        return pd.concat(df_list)
    
    def __fetch_by_day(self):
        """Returns the cleaned daily rates from the last 10 days for the given maturity."""

        # Construct the url
        d = {"1 month": 1,
             "3 months": 2,
             "6 months": 3,
             "12 months": 4,
             "1 week": 5}
        m_id = d[self.__maturity]
        m_label = self.__maturity.split()

        url = f"https://www.euribor-rates.eu/en/current-euribor-rates/{m_id}/euribor-rate-{m_label[0]}-{m_label[1]}/"

        # Daily Euribors are in the first table
        df = pd.read_html(url)[0]

        # Assign date index and drop the old date column
        df.index = df[0].astype("datetime64[ns]")
        df.index.name = "Date"
        df.drop(columns=0,inplace=True)

        # Convert the string rates ("X.xxx %") to float (0.0Xxxx)
        r_column = (np.char.replace(list(df[1])," %","").astype(float)) / 100
        df[1] = r_column.round(5) # round to avoid long decimals due to python miscalculations

        return df 
    
    def __fetch_by_year(self, y: int):
        """Returns the cleaned monthly rates of a given year for the given maturity."""

        # Check validity of the year:
        current_year = pd.Timestamp.today().year
        if y > current_year or y < 1999:
            raise ValueError(f"{y} is an invalid year (valid range: 1999 - {current_year}).")

        # Construct the url:
        d = {"1 month": 1,
             "3 months": 2,
             "6 months": 3,
             "12 months": 4,
             "1 week": 5}
        m_id = d[self.__maturity]
        url = f"https://www.global-rates.com/en/interest-rates/euribor/historical/{y}/?id={m_id}#bmrk-maturity"

        # Monthly rates are in the second table
        df = pd.read_html(url)[1]

        # Use the first day of the month, drop everything else
        df.drop(columns=["Unnamed: 0","Last","Highest","Lowest","Average"],
                inplace=True)
        
        #Rename the remaining column to 0 for simplicity
        df.rename(columns={"First": 0},
                  inplace=True)
        
        # Monthly date index, first business day of the month
        idx = pd.date_range(f"{y}/1/1",f"{y}/12/31",freq="BMS")
        df.index = idx
        df.index.name = "Date"

        # Check for empty values (months of current year yet to come) and drop them
        mask = df[0] == "-"
        df[mask] = np.nan
        df.dropna(inplace=True)

        # Convert the string rates ("X.xxx %") to float (0.0Xxxx)
        r_column = (np.char.replace(list(df[0])," %","").astype(float)) / 100
        df[0] = r_column.round(5) # round to avoid long decimals due to python miscalculations

        return df

if __name__ == "__main__":
    pass