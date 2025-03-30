"""
Financial Data Initialization DAG

This DAG initializes the financial database and loads historical market data from:
1. Yahoo Finance (Bovespa Index)
2. Brazilian Central Bank SGS system (CDI rates)

Flow:
1. Creates the database if not exists
2. Fetches historical Bovespa data from Yahoo Finance
3. Fetches historical CDI rates from SGS
4. Stores both datasets in PostgreSQL
"""

from datetime import date, timedelta

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

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
    def create_database_task():
        """Create the financial database if it doesn't exist"""
        from libs.database import create_database

        print("Creating database if not exists...")
        success = create_database()
        if not success:
            raise ValueError("Failed to create database")
        return "database_created"

    @task()
    def get_bovespa_data():
        """Fetch historical Bovespa index data from Yahoo Finance"""
        from libs.financial_data import get_yahoo_finance_historical_data

        print("Fetching Bovespa historical data...")
        return get_yahoo_finance_historical_data(code="^BVSP")

    @task()
    def get_cdi_data():
        """Fetch historical CDI rates from Brazilian Central Bank"""
        from libs.financial_data import get_sgs_data

        print("Fetching CDI historical data...")
        return get_sgs_data("12", date(2000, 1, 1), date.today())

    @task()
    def load_bovespa_data(bovespa_data: list):
        """Load Bovespa data into PostgreSQL"""
        import pandas as pd
        from libs.database import create_postgres_engine, write_dataframe_to_table

        print("Loading Bovespa data to database...")

        df = pd.DataFrame(bovespa_data)
        engine = create_postgres_engine()
        success = write_dataframe_to_table(
            df=df, table_name="bovespa_index", engine=engine, if_exists="replace"
        )
        if not success:
            raise ValueError("Failed to load Bovespa data")

    @task()
    def load_cdi_data(cdi_data: list):
        """Load CDI data into PostgreSQL"""
        import pandas as pd
        from libs.database import create_postgres_engine, write_dataframe_to_table

        print("Loading CDI data to database...")

        df = pd.DataFrame(cdi_data)
        engine = create_postgres_engine()
        success = write_dataframe_to_table(
            df=df, table_name="cdi_rates", engine=engine, if_exists="replace"
        )
        if not success:
            raise ValueError("Failed to load CDI data")

    @task()
    def completion_notification():
        """Notify that the initialization is complete"""
        print("Financial data initialization completed successfully!")

    # Define task dependencies
    db_created = create_database_task()

    # Parallel data fetching and loading
    bovespa_data = get_bovespa_data()
    cdi_data = get_cdi_data()

    # Data loading
    bovespa_loaded = load_bovespa_data(bovespa_data)
    cdi_loaded = load_cdi_data(cdi_data)

    # Final notification after both loads complete
    [bovespa_loaded, cdi_loaded] >> completion_notification()


# Instantiate the DAG
financial_data_initialization_dag = financial_data_initialization()
