-- models/marts/financial/facts/fct_serie_tb.sql
{{
  config(
    materialized='incremental',
    unique_key=['ticker_date', 'ticker_type_id'],
    post_hook=[
      """
      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'fct_serie_pk'
        ) THEN
          ALTER TABLE {{ this }} ADD CONSTRAINT fct_serie_pk PRIMARY KEY (serie_id);
        END IF;

        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'fct_serie_fk_ticker_type'
        ) THEN
          ALTER TABLE {{ this }} ADD CONSTRAINT fct_serie_fk_ticker_type
          FOREIGN KEY (ticker_type_id)
          REFERENCES {{ ref('dim_ticker_type_tb') }} (ticker_type_id);
        END IF;

        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'fct_serie_fk_date'
        ) THEN
          ALTER TABLE {{ this }} ADD CONSTRAINT fct_serie_fk_date
          FOREIGN KEY (ticker_date)
          REFERENCES {{ ref('dim_date_tb') }} (ticker_date);
        END IF;

        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'fct_serie_unique_ticker_date_type'
        ) THEN
          ALTER TABLE {{ this }} ADD CONSTRAINT fct_serie_unique_ticker_date_type
          UNIQUE (ticker_date, ticker_type_id);
        END IF;
      END$$;
      """
    ]
  )
}}

WITH ticker_mapping AS (
    SELECT
        t.ticker_type_id,
        t.ticker_type_nm
    FROM {{ ref('dim_ticker_type_tb') }} t
),

series_data AS (
    SELECT
        s.ticker_date,
        tm.ticker_type_id,
        s.profitability
    FROM {{ ref('vw_stg_raw_market_data') }} s
    INNER JOIN ticker_mapping tm
        ON s.ticker_type_nm = tm.ticker_type_nm

    {% if is_incremental() %}
    WHERE NOT EXISTS (
        SELECT 1 FROM {{ this }}
        WHERE {{ this }}.ticker_date = s.ticker_date
          AND {{ this }}.ticker_type_id = tm.ticker_type_id
    )
    {% endif %}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['ticker_date', 'ticker_type_id']) }} AS serie_id,
    ticker_date,
    ticker_type_id,
    profitability::numeric AS profitability
FROM series_data