# Financial Data Warehouse

This dbt project implements a multidimensional data warehouse for financial time series data.

## Project Overview

This project transforms raw financial data into a dimensional model with:
- Dimension tables for tickers, ticker types, and dates
- A fact table for financial series data with rentabilidade metrics
- Support for incremental loading
- Time-based partitioning by year and month

## Getting Started

### Prerequisites

- dbt 1.3.0 or higher
- PostgreSQL database
- dbt-utils package

### Installation

1. Clone this repository
2. Update the `profiles.yml` file with your database connection details
3. Run `dbt deps` to install package dependencies
4. Run `dbt run` to build the models

## Project Structure

This project follows the [dbt best practices](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) for project structure:

- **staging**: Raw data cleaning and standardization
- **marts/dimensions**: Dimension tables (ticker, ticker type, date)
- **marts/facts**: Fact tables (financial series data)
- **macros**: Custom functionality for partitioning

## Usage

### Full Rebuild

To run a full rebuild of all models:
```bash
dbt run --full-refresh
```

### Incremental Loading

To run an incremental load (only processing new data):
```bash
dbt run
```

## Testing

Run the test suite with:
```bash
dbt test
```

## Documentation

Generate and view documentation with:
```bash
dbt docs generate
dbt docs serve --port 8081
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request