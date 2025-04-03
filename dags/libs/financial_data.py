"""
Financial Data Fetcher Module

This module provides functions to retrieve financial data from Yahoo Finance and
the Brazilian Central Bank's SGS system (Sistema Gerenciador de Séries Temporais).

"""

from datetime import date, datetime, timedelta

import pandas as pd
import requests
import yfinance as yf
from dateutil.relativedelta import relativedelta

# Constants
MAX_SGS_YEARS_RANGE = 10


def get_yahoo_finance_data(code: str, date_init: date, date_end: date) -> str:
    """
    Fetch financial data from Yahoo Finance for a given stock code and date range.

    Args:
        code (str): The ticker symbol (e.g., '^BVSP').
        date_init (date): Start date for data retrieval.
        date_end (date): End date for data retrieval.

    Returns:
        str: JSON-compatible containing the requested financial data.

    Raises:
        ValueError: If date_init is after date_end
        RuntimeError: If data cannot be fetched from Yahoo Finance.
    """
    print(f"Fetching Yahoo Finance data for {code} from {date_init} to {date_end}")

    # Validate date range
    if date_init > date_end:
        raise ValueError("Start date cannot be after end date")

    try:
        # Download data using yfinance
        ticker = yf.Ticker(code)
        df = ticker.history(start=date_init, end=date_end)

        # Reset index to make date a column and format for JSON output
        df.reset_index(inplace=True)

        # Process and standardize the data
        df["date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df["ticker"] = code
        df["source"] = "Yahoo Finance"
        df["extracted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate daily returns
        df["close"] = df["Close"].pct_change()

        # Remove NA rows in close column
        df.dropna(subset=["close"], inplace=True)

        # Select only the required columns
        result_df = df[["date", "close", "ticker", "source", "extracted_date"]].copy()

        # Convert DataFrame to JSON-compatible dictionary
        return result_df.to_json(orient="records", date_format="iso")

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from Yahoo Finance: {str(e)}")


def get_sgs_data(code: str, date_init: date, date_end: date) -> str:
    """
    Fetch time series data from Brazilian Central Bank's SGS system.

    The SGS API only allows requests for up to 10 years of data at once.
    This function handles longer date ranges by making multiple requests if needed.

    Args:
        code (str): The SGS series code (e.g., 12 for CDI).
        date_init (date): Start date for data retrieval.
        date_end (date): End date for data retrieval.

    Returns:
        str: JSON-compatible containing the requested time series data.

    Raises:
        ValueError: If invalid dates are provided.
        RuntimeError: If data cannot be fetched from the SGS API.
    """
    print(f"Fetching SGS data for series {code} from {date_init} to {date_end}")

    # Input validation
    if date_init > date_end:
        raise ValueError("Start date must be before end date")

    # Format dates for the API
    date_format = "%d/%m/%Y"

    # Initialize an empty DataFrame to store all results
    full_df = pd.DataFrame()

    # Calculate the number of 10-year periods needed
    current_start = date_init

    try:
        while current_start <= date_end:
            # Calculate the end date for this chunk (either 10 years from start or the overall end date)
            current_end = min(
                date_end, current_start + relativedelta(years=10) - relativedelta(days=1)
            )

            print(f"Fetching chunk from {current_start} to {current_end}")

            # Format dates for API request
            start_str = current_start.strftime(date_format)
            end_str = current_end.strftime(date_format)

            # Construct URL
            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={start_str}&dataFinal={end_str}"

            # Make the request
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors

            # Parse JSON response
            chunk_data = response.json()

            # Convert to DataFrame
            if chunk_data:  # Check if data was returned
                chunk_df = pd.DataFrame(chunk_data)

                # Append to the full dataset
                full_df = pd.concat([full_df, chunk_df], ignore_index=True)

            # Update start date for next iteration
            current_start = current_end + timedelta(days=1)

        # Check if we got any data
        if full_df.empty:
            return {"error": f"No data available for SGS code {code} in the specified date range"}

        # Data cleaning and transformation
        # Convert 'data' column to datetime format
        full_df["date"] = pd.to_datetime(full_df["data"], format="%d/%m/%Y")

        # Convert 'valor' column to numeric and divide by 100 as it's a percentage
        full_df["close"] = pd.to_numeric(full_df["valor"], errors="coerce") / 100

        # Process and standardize the data
        full_df["ticker"] = code
        full_df["source"] = "SGS"
        full_df["extracted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Convert to dictionary/JSON format
        result = full_df[["date", "close", "ticker", "source", "extracted_date"]].to_json(
            orient="records", date_format="iso"
        )

        return result

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request error: {str(e)}")
    except ValueError as e:
        raise RuntimeError(f"Data parsing error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while fetching SGS data: {str(e)}")


def get_sgs_last_data(code: str) -> str:
    """
    Fetch the most recent data point for a given SGS series code.

    Args:
        code (str): The SGS series code (e.g., '12' for CDI).

    Returns:
        str: JSON-compatible containing the most recent data point.

    Raises:
        RuntimeError: If data cannot be fetched from the SGS API.
    """
    print(f"Fetching last data point for SGS series {code}")

    try:
        # Construct URL for last data point
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/1?formato=json"

        # Make the request
        response = requests.get(url)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        if not data:
            return {"error": f"No data available for SGS code {code}"}

        # Convert to DataFrame for consistent processing
        df = pd.DataFrame(data)

        # Convert 'valor' column to numeric and divide by 100 as it's a percentage
        df["close"] = pd.to_numeric(df["valor"], errors="coerce") / 100

        # Data processing
        df["date"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["ticker"] = code
        df["source"] = "SGS"
        df["extracted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return df[["date", "close", "ticker", "source", "extracted_date"]].to_json(
            orient="records", date_format="iso"
        )

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while fetching last SGS data: {str(e)}")


def get_yahoo_finance_historical_data(code: str) -> str:
    """
    Fetch complete historical data for a given ticker from Yahoo Finance.

    Args:
        code (str): The ticker symbol.

    Returns:
        str: JSON-compatible containing all available historical data.

    Raises:
        RuntimeError: If data cannot be fetched from Yahoo Finance.
    """
    print(f"Fetching complete historical data for {code} from Yahoo Finance")

    try:
        # Download all available historical data
        ticker = yf.Ticker(code)
        df = ticker.history(period="max")

        # Reset index to make date a column
        df.reset_index(inplace=True)

        # Process and standardize the data
        df["date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df["ticker"] = code
        df["source"] = "Yahoo Finance"
        df["extracted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate daily returns
        df["close"] = df["Close"].pct_change()

        # Remove NA rows in close column
        df.dropna(subset=["close"], inplace=True)

        # Select only the required columns
        result_df = df[["date", "close", "ticker", "source", "extracted_date"]].copy()

        # Convert DataFrame to JSON-compatible dictionary
        return result_df.to_json(orient="records", date_format="iso")

    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data from Yahoo Finance: {str(e)}")
