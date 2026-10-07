# Day 41 — dbt Hooks

## Note on today's topic

This project already had a Day 29 covering dbt + GitHub Actions CI, a Day 30 covering
incremental models, and a Day 31 covering snapshots - which only came to light partway
into today's session when the original plan (CI/CD) turned out to duplicate Day 29.
Today's actual topic was changed to dbt hooks instead, which hadn't been covered yet.

## What this is

Two kinds of dbt hook, both demonstrated with a real, queryable audit trail:

- **Project-level hooks** (`on-run-start` / `on-run-end` in `dbt_project.yml`) fire once
  around an entire dbt invocation. `on-run-start` creates two audit tables if they don't
  already exist; `on-run-end` calls a macro that inserts one summary row per invocation
  into `dbt_run_log`, using dbt's `results` variable (a list of every node's outcome).
- **Model-level hooks** (`post_hook` in a model's `config()`) fire immediately after that
  one specific model builds. `mart_customer_revenue` has a `post_hook` that inserts a row
  into `model_build_log` recording its own row count every time it builds.

```sql
-- macros/log_run_summary.sql (called from on-run-end)
{% macro log_run_summary(results) %}
    {% set success_count = results | selectattr("status", "equalto", "success") | list | length %}
    {% set pass_count = results | selectattr("status", "equalto", "pass") | list | length %}
    {% set fail_count = results | selectattr("status", "equalto", "fail") | list | length %}
    {% set error_count = results | selectattr("status", "equalto", "error") | list | length %}
    {% set skip_count = results | selectattr("status", "equalto", "skipped") | list | length %}
    insert into main.dbt_run_log (invocation_id, run_started_at, total_nodes, pass_count, fail_count, skip_count)
    values ('{{ invocation_id }}', '{{ run_started_at }}', {{ results | length }},
            {{ success_count + pass_count }}, {{ fail_count + error_count }}, {{ skip_count }})
{% endmacro %}
```

## Proof 1 — a clean build logs an accurate summary

A full `dbt build` finished with `Done. PASS=46 WARN=0 ERROR=0`. Querying `dbt_run_log`
immediately after showed a row with `total_nodes=46, pass_count=46, fail_count=0,
skip_count=0` - matching exactly. `model_build_log` showed `mart_customer_revenue`
logged with `row_count=12`, matching an independent count of distinct customers with at
least one completed order.

## Proof 2 — the audit trail stays honest when something actually fails

A negative-amount order was planted (customer 119, -75.00), which fails the
`non_negative` test on `mart_customer_revenue.total_revenue`. Rerunning `dbt build`
produced `Completed with 1 error` and correctly skipped the entire downstream
`mart_customer_revenue_ranked` branch (6 nodes) rather than building on top of a known-bad
result. Querying the audit tables afterwards confirmed:

- `dbt_run_log` logged a new row with `fail_count=1, skip_count=6` - the `on-run-end`
  hook fired and recorded the real failure, not a fabricated success.
- `model_build_log` logged a new row for `mart_customer_revenue` with `row_count=13` -
  proving its `post_hook` ran even though a test *downstream of it* failed, because the
  model itself still built successfully before the test ever ran.

## An unplanned but genuine discovery

A third, unexpected row appeared in `dbt_run_log` with `total_nodes=1, pass_count=1`.
Tracing it back: `dbt seed --select raw_orders`, a completely separate command run before
the second `dbt build`, is its own full dbt invocation with exactly one node - and it
turns out `on-run-start`/`on-run-end` fire on it too. By contrast, four separate
`dbt show --inline` queries run over the course of the day never added any rows at all.
The conclusion, confirmed empirically rather than assumed: dbt's project-level hooks fire
on real build-style commands (`run`, `build`, `seed`, `test`, `snapshot`) but not on
lightweight preview commands like `dbt show`. A production version of this audit table
would need to account for that - logging every `dbt seed` alongside every `dbt build`
might not be the intended behaviour, depending on what the audit trail is actually for.

## Final state

The bad row was removed and a final `dbt build` confirmed clean: 49/49 (46 real nodes +
3 hook executions).

## Key takeaway

A hook that only gets exercised on the happy path hasn't actually been proven - it's
just been configured. The real test was deliberately causing a failure and checking that
the audit trail reflected the failure accurately rather than silently logging a false
"success," and separately, that a model-level hook's behaviour is tied to its own node's
outcome, not to whatever happens downstream of it afterward.
