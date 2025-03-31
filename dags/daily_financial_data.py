"""
DAG: Daily Financial Data Update

This DAG runs every day at 8:00 PM to update the financial database with the most recent
market data from:
- Yahoo Finance (e.g., Bovespa and other stock indices/prices)
- Brazilian Central Bank's SGS system (e.g., CDI and other interest rates)

Steps:
1. Query the database for all active ticker types
2. Fetch financial data based on the source (SGS or Yahoo)
3. Load the raw data into PostgreSQL
4. Run DBT transformations and tests
"""

from datetime import date, timedelta

import pandas as pd
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Constants for database and file paths
RAW_TABLE_NAME = "raw_market_data"
DBT_PROJECT_DIR = "/usr/local/airflow/datawarehouse"

# DAG configuration parameters
default_args = {
    "owner": "Astro",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "email_on_failure": True,
    "email_on_retry": False,
}


@dag(
    default_args=default_args,
    schedule_interval="0 20 * * *",
    dag_id="daily_financial_data_update",
    start_date=days_ago(1),
    tags=["financial_data", "daily_update"],
    catchup=False,
)
def daily_financial_data_update():
    """
    Main DAG function for daily financial data update.
    """

    @task()
    def get_ticker_list() -> list:
        """
        Fetches list of tickers from dim_ticker_type_tb, including source info.

        Returns:
            list: Records with 'ticker_type_nm' and 'is_src'

        Raises:
            ValueError: If no tickers are found in the dimension table
        """
        from libs.database import create_postgres_engine, read_from_table

        print("Retrieving ticker list from financial_s.dim_ticker_type_tb...")

        engine = create_postgres_engine()

        query = """
            SELECT 
                ticker_type_nm, 
                is_src 
            FROM 
                financial_s.dim_ticker_type_tb
            WHERE 
                is_active = true
        """

        df = read_from_table(
            table_name="dim_ticker_type_tb", engine=engine, schema="financial_s", query=query
        )

        if df is None or df.empty:
            raise ValueError("No active tickers found in dim_ticker_type_tb")

        print(f"Found {len(df)} active tickers to process")

        return df.to_dict(orient="records")

    @task()
    def get_yahoo_data(tickers: list) -> list:
        """
        Fetch data for tickers from Yahoo Finance.

        Args:
            tickers (list): List of dictionaries with ticker_type_nm and is_src

        Returns:
            list: List of JSON strings containing Yahoo Finance data
        """
        from libs.financial_data import get_yahoo_finance_data

        today = date.today()
        date_init = today - timedelta(days=3)

        yahoo_tickers = [row for row in tickers if not row["is_src"]]

        print(f"Processing {len(yahoo_tickers)} Yahoo Finance tickers...")

        if not yahoo_tickers:
            print("No Yahoo Finance tickers to process")
            return []

        result = []

        for idx, row in enumerate(yahoo_tickers):
            ticker = row["ticker_type_nm"]
            try:
                print(
                    f"[{idx + 1}/{len(yahoo_tickers)}] Fetching data for {ticker} from {date_init} to {today}"
                )
                data = get_yahoo_finance_data(ticker, date_init, today)
                result.append(data)
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")

        return result

    @task()
    def get_sgs_data(tickers: list) -> list:
        """
        Fetch latest data from SGS for CDI and similar series.

        Args:
            tickers (list): List of dictionaries with ticker_type_nm and is_src

        Returns:
            list: List of JSON strings containing SGS data
        """
        from libs.financial_data import get_sgs_last_data

        sgs_tickers = [row for row in tickers if row["is_src"]]

        print(f"Processing {len(sgs_tickers)} Brazilian Central Bank SGS tickers...")

        if not sgs_tickers:
            print("No SGS tickers to process")
            return []

        result = []

        for idx, row in enumerate(sgs_tickers):
            ticker = row["ticker_type_nm"]
            try:
                print(
                    f"[{idx + 1}/{len(sgs_tickers)}] Fetching latest data for SGS series {ticker}"
                )
                data = get_sgs_last_data(ticker)
                result.append(data)
            except Exception as e:
                print(f"Error fetching data for SGS series {ticker}: {e}")

        return result

    @task()
    def load_financial_data(yahoo_data: list, sgs_data: list) -> bool:
        """
        Loads all financial data into the raw table in PostgreSQL.

        This task combines data from both sources into a single DataFrame,
        performs necessary data type conversions, and loads it into the
        database in a single operation for efficiency.

        Args:
            yahoo_data (list): List of Yahoo Finance data in JSON
            sgs_data (list): List of SGS data in JSON

        Returns:
            bool: True if data loaded successfully

        Raises:
            ValueError: If data loading fails
        """
        from libs.database import create_postgres_engine, write_dataframe_to_table

        engine = create_postgres_engine()
        try:
            all_data = yahoo_data + sgs_data
            dfs = [pd.read_json(batch) for batch in all_data]
            combined_df = pd.concat(dfs, ignore_index=True)

            combined_df["date"] = pd.to_datetime(combined_df["date"]).dt.date
            combined_df["extracted_date"] = pd.to_datetime(combined_df["extracted_date"])

            return write_dataframe_to_table(
                df=combined_df, table_name=RAW_TABLE_NAME, engine=engine, if_exists="append"
            )
        except Exception as e:
            print(f"Error writing combined data: {e}")
            return False

    @task()
    def completion_notification(success: bool) -> None:
        """
        Final confirmation or failure message.

        Args:
            success (bool): True if all data was loaded successfully

        Raises:
            ValueError: If data loading was not successful
        """
        if success:
            print("Daily financial data pipeline completed successfully.")
            return True
        else:
            raise ValueError("One or more loading steps failed.")

    # DBT commands for data transformation and testing
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"""
        echo "Running DBT transformations..."
        dbt run --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        echo "Running DBT tests..."
        dbt test --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}
        """,
    )

    # DAG flow definition
    tickers = get_ticker_list()
    yahoo_data = get_yahoo_data(tickers)
    sgs_data = get_sgs_data(tickers)
    loading_success = load_financial_data(yahoo_data, sgs_data)
    notify = completion_notification(loading_success)

    # Execute DBT pipeline after data is loaded
    notify >> dbt_run >> dbt_test


# Instantiate the DAG
daily_financial_data_update_dag = daily_financial_data_update()
