{% macro create_year_month_partitions(table_relation, partition_column, months_ahead=12) %}
  {%- set create_partitions %}
  do $$
  declare
    start_date date := '1990-01-01'::date;
    end_date date := date_trunc('month', current_date) + interval '{{ months_ahead }} month';
    interval_step interval := interval '1 month';
    current_date_mod date := start_date;
    partition_name text;
    start_partition text;
    end_partition text;
    year_month text;
  begin
    while current_date_mod < end_date loop
      year_month := to_char(current_date_mod, 'YYYY_MM');
      partition_name := '{{ table_relation.identifier }}_' || year_month;
      start_partition := to_char(current_date_mod, 'YYYY-MM-DD');
      current_date_mod := current_date_mod + interval_step;
      end_partition := to_char(current_date_mod, 'YYYY-MM-DD');
      
      execute format('
        create table if not exists {{ table_relation.schema }}.%I 
        partition of {{ table_relation.schema }}.{{ table_relation.identifier }} 
        for values from (''%s'') to (''%s'')', 
        partition_name, start_partition, end_partition
      );
    end loop;
  end $$;
  {% endset %}

  {% do run_query(create_partitions) %}
  {% do log("Created partitions for " ~ table_relation ~ " from 1990-01-01 to " ~ months_ahead ~ " months ahead", info=true) %}
{% endmacro %}
