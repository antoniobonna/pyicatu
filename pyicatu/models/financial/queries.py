"""
Financial data query operations.

This module provides functions to retrieve financial data from the database,
including profitability metrics for various financial instruments.
"""

from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from pyicatu.utils.database import create_postgres_engine


def get_profitability_df(
    ticker: str, init_date: date, end_date: date, engine: Optional[Engine] = None
) -> pd.DataFrame:
    """
    Get raw profitability data for a financial ticker between dates.

    Args:
        ticker: Financial instrument identifier (e.g., 'CDI', 'Ibovespa')
        init_date: Start date (datetime.date)
        end_date: End date (datetime.date)
        engine: Optional SQLAlchemy engine; creates a new one if not provided

    Returns:
        pd.DataFrame: Raw query results with columns:
            - ticker_nm: Asset name
            - ticker_date: Date of record
            - month: Month of record
            - year: Year of record
            - rentabilidade_diaria: Daily return
            - annual_tax: Annual tax rate

    Raises:
        SQLAlchemyError: For database connection or query issues
    """
    query = f"""
        SELECT
            t.ticker_nm,
            d.ticker_date,
            d.month,
            d.year,
            s.profitability,
            t.annual_tax
        FROM financial_s.fct_serie_tb s
        JOIN financial_s.dim_ticker_type_tb tt ON s.ticker_type_id = tt.ticker_type_id
        JOIN financial_s.dim_date_tb d ON d.ticker_date = s.ticker_date
        JOIN financial_s.dim_ticker_tb t ON t.ticker_type_id = tt.ticker_type_id
        WHERE t.ticker_nm = '{ticker}'
          AND d.ticker_date BETWEEN '{str(init_date)}' AND '{str(end_date)}'
        ORDER BY d.ticker_date
    """
    # Use provided engine or create a new one
    db_engine = engine or create_postgres_engine()

    try:
        # Execute query with parameters and convert to DataFrame
        with db_engine.connect() as connection:
            raw_conn = connection.connection
            return pd.read_sql(
                query,
                raw_conn,
                parse_dates=["ticker_date"],
                params={"ticker": ticker, "init_date": init_date, "end_date": end_date},
            )
    except SQLAlchemyError as e:
        raise ValueError(f"Query execution failed: {e}") from e
