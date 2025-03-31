{% macro build_partitioned_table_if_missing(relation, partition_column, months_ahead) %}
  {% set table_exists_query %}
    SELECT 1 FROM pg_tables
    WHERE schemaname = '{{ relation.schema }}'
      AND tablename = '{{ relation.identifier }}'
  {% endset %}

  {% set table_exists = run_query(table_exists_query).columns[0].values() | length > 0 %}
  {% set hooks = [] %}

  {% if not table_exists %}
    {% do hooks.append(
      "DO $$ BEGIN
        EXECUTE 'ALTER TABLE " ~ relation.schema ~ "." ~ relation.identifier ~ " RENAME TO " ~ relation.identifier ~ "_temp';
        EXECUTE \'
          CREATE TABLE " ~ relation.schema ~ "." ~ relation.identifier ~ " (
            serie_id TEXT,
            ticker_date DATE REFERENCES " ~ relation.schema ~ ".dim_date_tb(ticker_date),
            ticker_type_id TEXT REFERENCES " ~ relation.schema ~ ".dim_ticker_type_tb(ticker_type_id),
            profitability NUMERIC,
            PRIMARY KEY (serie_id, ticker_date)
          ) PARTITION BY RANGE (ticker_date);
        \';
      END$$;"
    ) %}

    {% do post_hooks.append(
    "{{ create_year_month_partitions(this, 'ticker_date', 12) }}"
  ) %}

    {% do hooks.append(
      "DO $$ BEGIN
        EXECUTE 'INSERT INTO " ~ relation.schema ~ "." ~ relation.identifier ~ " SELECT * FROM " ~ relation.schema ~ "." ~ relation.identifier ~ "_temp';
        EXECUTE 'DROP TABLE " ~ relation.schema ~ "." ~ relation.identifier ~ "_temp CASCADE';
      END$$;"
    ) %}
  {% else %}
    {% do post_hooks.append(
    "{{ create_year_month_partitions(this, 'ticker_date', 12) }}"
  ) %}
  {% endif %}

  {{ return(hooks) }}
{% endmacro %}
