-- models/marts/financial/dimensions/dim_date_tb.sql
{{
  config(
    materialized='incremental',
    unique_key='ticker_date',
    post_hook=[
      """
      DO $$
      BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'dim_date_pk'
          ) THEN
              ALTER TABLE {{ this }} ADD CONSTRAINT dim_date_pk PRIMARY KEY (ticker_date);
          END IF;
      END$$;
      """
    ]
  )
}}

WITH distinct_dates AS (
    SELECT DISTINCT
        ticker_date
    FROM {{ ref('vw_stg_raw_market_data') }}
    WHERE ticker_date IS NOT NULL
    {% if is_incremental() %}
      AND ticker_date > (SELECT MAX(ticker_date) FROM {{ this }})
    {% endif %}
)

SELECT
    ticker_date,
    EXTRACT(MONTH FROM ticker_date)::integer AS month,
    EXTRACT(YEAR FROM ticker_date)::integer AS year,
    EXTRACT(QUARTER FROM ticker_date)::integer AS quarter
FROM distinct_dates
