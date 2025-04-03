-- models/marts/financial/dimensions/dim_ticker.sql
{{
  config(
    materialized='incremental',
    unique_key='ticker_id',
    post_hook=[
      """
      DO $$
      BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'dim_ticker_pk'
          ) THEN
              ALTER TABLE {{ this }}
              ADD CONSTRAINT dim_ticker_pk PRIMARY KEY (ticker_id);
          END IF;

          IF NOT EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'dim_ticker_fk_type'
          ) THEN
              ALTER TABLE {{ this }}
              ADD CONSTRAINT dim_ticker_fk_type
              FOREIGN KEY (ticker_type_id)
              REFERENCES {{ ref('dim_ticker_type_tb') }} (ticker_type_id);
              CREATE INDEX ON {{ this }} (ticker_nm);
          END IF;
      END$$;
      """
    ]
  )
}}

WITH ticker_with_type AS (
    SELECT DISTINCT
        CASE
            WHEN t.ticker_type_nm = '^BVSP' THEN 'Ibovespa'
            WHEN t.ticker_type_nm = '12' THEN 'CDI'
        END AS ticker_nm,
        t.ticker_type_id
    FROM {{ ref('vw_stg_raw_market_data') }} s
    INNER JOIN {{ ref('dim_ticker_type_tb') }} t
        ON s.ticker_type_nm = t.ticker_type_nm
    WHERE s.ticker_type_nm IS NOT NULL
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['ticker_nm']) }} AS ticker_id,
    ticker_nm,
    ticker_type_id,
    NULL::numeric AS annual_tax
FROM ticker_with_type
{% if is_incremental() %}
WHERE ticker_nm NOT IN (SELECT ticker_nm FROM {{ this }})
{% endif %}
