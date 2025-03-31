WITH source_data AS (
    SELECT
        ticker,
        date,
        close,
        source,
        extracted_date
    FROM {{ source('raw', 'raw_market_data') }}
),

cleaned_data AS (
    SELECT DISTINCT ON (ticker, date)
        ticker AS ticker_type_nm,
        date AS ticker_date,
        close AS profitability,
        CASE
            WHEN source = 'Yahoo Finance' THEN False
            ELSE True
        END AS is_src
    FROM source_data
    WHERE ticker IS NOT NULL
      AND date IS NOT NULL
    ORDER BY ticker, date, extracted_date DESC
)

SELECT
    ticker_type_nm,
    ticker_date,
    profitability,
    is_src
FROM cleaned_data