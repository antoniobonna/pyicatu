-- models/marts/financial/dimensions/dim_ticker_type.sql
{{ config(
    materialized='incremental',
    unique_key='ticker_type_id',
    post_hook=[
      """
      DO $$
      BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'dim_ticker_type_pk'
          ) THEN
              ALTER TABLE {{ this }} ADD CONSTRAINT dim_ticker_type_pk PRIMARY KEY (ticker_type_id);
              CREATE INDEX ON {{ this }} (ticker_type_nm);
          END IF;
      END$$;
      """
    ]
) }}


WITH distinct_ticker_types AS (
    SELECT DISTINCT
        ticker_type_nm,
        is_src
    FROM {{ ref('vw_stg_raw_market_data') }}
    WHERE ticker_type_nm IS NOT NULL
    
    {% if is_incremental() %}
    -- Only process ticker types not already in our table
    AND ticker_type_nm NOT IN (SELECT ticker_type_nm FROM {{ this }})
    {% endif %}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['ticker_type_nm']) }} AS ticker_type_id,
    ticker_type_nm,
    is_src
FROM distinct_ticker_types