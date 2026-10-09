{% macro log_run_summary(results) %}
    {% set success_count = results | selectattr("status", "equalto", "success") | list | length %}
    {% set pass_count = results | selectattr("status", "equalto", "pass") | list | length %}
    {% set fail_count = results | selectattr("status", "equalto", "fail") | list | length %}
    {% set error_count = results | selectattr("status", "equalto", "error") | list | length %}
    {% set skip_count = results | selectattr("status", "equalto", "skipped") | list | length %}
    insert into main.dbt_run_log (invocation_id, run_started_at, total_nodes, pass_count, fail_count, skip_count)
    values (
        '{{ invocation_id }}',
        '{{ run_started_at }}',
        {{ results | length }},
        {{ success_count + pass_count }},
        {{ fail_count + error_count }},
        {{ skip_count }}
    )
{% endmacro %}
