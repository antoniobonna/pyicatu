"""
Module for calculating financial metrics and performance indicators.

This module provides functionality to calculate various financial metrics
including daily returns, cumulative returns, and monthly performance
for different financial instruments.
"""

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from pyicatu.models.financial.queries import get_profitability_df

# Constants
BUSINESS_DAYS_PER_YEAR = 252  # Standard number of business days in a financial year


@dataclass
class FinancialMetrics:
    """
    A class for calculating various financial metrics from database records.

    This class provides methods to retrieve financial data and calculate
    performance metrics such as daily returns, cumulative returns, and
    monthly performance indicators.
    """

    def fetch_profitability(self, ticker: str, init_date: date, end_date: date) -> pd.DataFrame:
        """
        Fetch and calculate adjusted daily returns for a ticker.

        This method retrieves raw profitability data and calculates the
        tax-adjusted daily returns. It handles the conversion from annual
        to daily tax rates and applies necessary adjustments.

        Args:
            ticker: Financial instrument identifier
            init_date: Start date (datetime.date)
            end_date: End date (datetime.date)

        Returns:
            pd.DataFrame: With calculated columns:
                - All original columns from get_profitability_df()
                - taxa_diaria: Daily equivalent of annual tax
                - rentabilidade_ajustada: Tax-adjusted daily return
        """
        # Retrieve raw profitability data from database
        df = get_profitability_df(ticker, init_date, end_date)

        # Return early if no data is found
        if df.empty:
            return df

        # Calculate daily tax from annual rate (business days per year)
        df["daily_tax"] = np.where(
            df["annual_tax"].notnull(),
            100 * ((1 + df["annual_tax"]) ** (1 / BUSINESS_DAYS_PER_YEAR) - 1),
            0.0
        )

        # Calculate tax-adjusted profitability
        df["adjusted_profitability"] = df["profitability"] + df["daily_tax"]

        # Set the first day's adjusted profitability to 0 as the base value
        df.loc[df.index[0], "adjusted_profitability"] = 0

        return df

    def get_cumulative_profitability(self, ticker: str, init_date: date, end_date: date) -> float:
        """
        Calculate cumulative profitability between dates.

        Args:
            ticker: Financial instrument identifier
            init_date: Start date (datetime.date)
            end_date: End date (datetime.date)

        Returns:
            float: Cumulative return as a decimal (e.g., 0.0525 for 5.25%)
        """
        # Get adjusted profitability data
        df = self.fetch_profitability(ticker, init_date, end_date)

        # Return 0.0 if no data is available
        if df.empty:
            return 0.0

        # Calculate cumulative return
        cumulative_return = (1 + df["adjusted_profitability"] / 100).cumprod()

        return float(cumulative_return.iloc[-1] - 1)

    def get_monthly_cumulative_profitability(
        self, ticker: str, init_date: date, end_date: date
    ) -> list[dict[str, float]]:
        """
        Calculate cumulative monthly returns between two dates.

        Args:
            ticker: Financial instrument identifier
            init_date: Start date (datetime.date)
            end_date: End date (datetime.date)

        Returns:
            List[Dict[str, float]]: DataFrame with monthly returns:
                - year: Year of the return
                - month: Month of the return (1-12)
                - adjusted_profitability: Monthly compounded return as decimal
        """
        # Get adjusted profitability data
        df = self.fetch_profitability(ticker, init_date, end_date)

        # Return empty DataFrame if no data is available
        if df.empty:
            return []

        # Calculate daily cumulative returns
        df["cumulative_return"] = (1 + df["adjusted_profitability"] / 100).cumprod() - 1

        # Get last value of each month
        monthly_cumulative = (
            df.groupby(["year", "month"])
            .apply(lambda group: group[["cumulative_return"]].iloc[-1])
            .reset_index()
        )

        return monthly_cumulative.to_dict(orient="records")
