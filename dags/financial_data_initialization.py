"""
Financial Data Initialization DAG

This DAG initializes the financial database and loads historical market data from:
1. Yahoo Finance (Bovespa Index) - Brazil's primary stock market index
2. Brazilian Central Bank SGS system (CDI rates) - Brazil's interbank lending rate

Flow:
1. Creates the database if not exists
2. Fetches historical Bovespa data from Yahoo Finance
3. Fetches historical CDI rates from SGS
4. Stores both datasets in PostgreSQL

Dependencies:
- libs.database: Custom module for database operations
- libs.financial_data: Custom module with financial data fetching functions
- Pandas: For data manipulation before database insertion
"""

from datetime import date, timedelta

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

# Constants
BOVESPA_CODE = "^BVSP"  # Yahoo Finance ticker symbol for Bovespa index
CDI_CODE = "12"  # SGS code for CDI (Certificado de Depósito Interbancário) rate
INITIAL_DATE = date(2000, 1, 1)  # Start date for historical data
RAW_TABLE_NAME = "raw_market_data"  # Target table for storing both datasets

default_args = {
    "owner": "Astro",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    default_args=default_args,
    schedule=None,
    dag_id="financial_data_initialization",
    start_date=days_ago(1),
    tags=["financial_data", "initial_load"],
    catchup=False,
)
def financial_data_initialization():
    """
    DAG to initialize financial database and load historical data.

    Workflow:
    1. Create database if not exists
    2. Fetch Bovespa historical data from Yahoo Finance
    3. Fetch CDI historical data from Brazilian Central Bank
    4. Store both datasets in PostgreSQL
    """

    @task()
    def create_database_task() -> bool:
        """
        Create the financial database if it doesn't exist

        This task checks if the target database exists and creates it if needed.
        The actual implementation is in the libs.database module.

        Returns:
            bool: True if database exists or was created successfully

        Raises:
            ValueError: If database creation fails
        """
        from libs.database import create_database

        print("Creating database if not exists...")
        success = create_database()
        if not success:
            raise ValueError("Failed to create database")
        return success

    @task()
    def get_bovespa_data(db_created: bool) -> list:
        """
        Fetch historical Bovespa index data from Yahoo Finance

        Gets historical price data for Brazil's main stock index (Bovespa/^BVSP)
        using the Yahoo Finance API via our custom wrapper function.

        Args:
            db_created (bool): Flag indicating if database was successfully created

        Returns:
            list: JSON-serializable list containing historical Bovespa data
        """

        from libs.financial_data import get_yahoo_finance_historical_data

        print("Fetching Bovespa historical data...")
        return get_yahoo_finance_historical_data(code=BOVESPA_CODE)

    @task()
    def get_cdi_data(db_created: bool) -> list:
        """
        Fetch historical CDI rates from Brazilian Central Bank

        Gets CDI (Interbank Deposit Certificate) rate data from the Brazilian
        Central Bank's SGS (Sistema Gerenciador de Séries Temporais) API.
        CDI is Brazil's main interest rate benchmark.

        Args:
            db_created (bool): Flag indicating if database was successfully created

        Returns:
            list: JSON-serializable list containing historical CDI data
        """
        if not db_created:
            raise ValueError("Database not created - cannot fetch data")

        from libs.financial_data import get_sgs_data

        print("Fetching CDI historical data...")
        return get_sgs_data(CDI_CODE, INITIAL_DATE, date.today())

    @task()
    def load_bovespa_data(bovespa_data: list) -> bool:
        """
        Load Bovespa data into PostgreSQL

        Converts the JSON data to a pandas DataFrame, performs necessary
        date formatting, and inserts it into the database table.

        Args:
            bovespa_data (list): The Bovespa data returned by get_bovespa_data

        Returns:
            bool: True if data was successfully loaded

        Raises:
            ValueError: If data loading fails
        """
        import pandas as pd
        from libs.database import create_postgres_engine, write_dataframe_to_table

        print("Loading Bovespa data to database...")
        # Convert JSON to DataFrame
        df = pd.read_json(bovespa_data)

        # Format dates for PostgreSQL compatibility
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["extracted_date"] = pd.to_datetime(df["extracted_date"])

        # Get database engine and write data
        engine = create_postgres_engine()
        success = write_dataframe_to_table(
            df=df,
            table_name=RAW_TABLE_NAME,
            engine=engine,
            if_exists="append"
        )

        if not success:
            raise ValueError("Failed to load Bovespa data")
        return success

    @task()
    def load_cdi_data(cdi_data: list) -> bool:
        """
        Load CDI data into PostgreSQL

        Converts the JSON data to a pandas DataFrame, performs necessary
        type conversions and date formatting, and inserts it into the database table.

        Args:
            cdi_data (list): The CDI data returned by get_cdi_data

        Returns:
            bool: True if data was successfully loaded

        Raises:
            ValueError: If data loading fails
        """
        import pandas as pd
        from libs.database import create_postgres_engine, write_dataframe_to_table

        print("Loading CDI data to database...")
        # Convert JSON to DataFrame
        df = pd.read_json(cdi_data)

        # Ensure proper data types for database compatibility
        df["ticker"] = df["ticker"].astype(str)

        # Format dates for PostgreSQL compatibility
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["extracted_date"] = pd.to_datetime(df["extracted_date"])

        # Get database engine and write data
        engine = create_postgres_engine()
        success = write_dataframe_to_table(
            df=df,
            table_name=RAW_TABLE_NAME,
            engine=engine,
            if_exists="append"
        )

        if not success:
            raise ValueError("Failed to load CDI data")
        return success

    @task()
    def completion_notification(bovespa_success: bool, cdi_success: bool) -> None:
        """
        Notify that the initialization is complete

        Final task that confirms successful completion of the data loading
        process or raises an error if any step failed.

        Args:
            bovespa_success (bool): Result of Bovespa data loading
            cdi_success (bool): Result of CDI data loading

        Raises:
            ValueError: If either data loading step failed
        """
        if bovespa_success and cdi_success:
            print("Financial data initialization completed successfully!")
        else:
            raise ValueError("Data loading completed with errors")

    # Define task dependencies
    # Step 1: Create database
    db_created = create_database_task()

    # Step 2: Fetch data after database is created (parallel tasks)
    bovespa_data = get_bovespa_data(db_created)
    cdi_data = get_cdi_data(db_created)

    # Step 3: Load data after fetching (parallel tasks)
    bovespa_loaded = load_bovespa_data(bovespa_data)
    cdi_loaded = load_cdi_data(cdi_data)

    # Step 4: Final notification after all data is loaded
    completion_notification(bovespa_loaded, cdi_loaded)


# Instantiate the DAG
financial_data_initialization_dag = financial_data_initialization()
