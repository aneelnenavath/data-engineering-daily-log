# Day 26 — Intro to dbt with DuckDB

## Objective
Introduce dbt (data build tool) - genuinely one of the most commonly
referenced tools in current data engineering job postings, and untouched
by anything earlier in this project. Build a small staging-to-mart pipeline
with real dbt tests, and prove the tests actually catch bad data rather
than just being configured to look like they would.

## Setup
Used `dbt-duckdb` rather than a warehouse-hosted adapter, since DuckDB
needs no server, account, or credentials - just a local file - keeping the
whole exercise self-contained. The project structure (`dbt_project.yml`,
`profiles.yml`, seeds, models) was written directly rather than through the
interactive `dbt init` wizard, since this workflow runs one command at a
time rather than answering interactive prompts.

## Pipeline design
- `seeds/raw_orders.csv`: 15 synthetic orders loaded via `dbt seed`.
- `models/staging/stg_orders.sql`: a view over the seed, referenced with
  `{{ ref('raw_orders') }}`.
- `models/marts/mart_customer_revenue.sql`: a table aggregating completed-
  order revenue per customer, referenced from staging with
  `{{ ref('stg_orders') }}` - the `ref()` calls are what let dbt build the
  dependency graph (lineage) automatically, confirmed via `dbt docs
  generate`.
- Tests declared in each model's `schema.yml`: `unique` and `not_null` on
  `order_id`, `not_null` on `customer_id`, `accepted_values` on `status`,
  plus `unique`/`not_null` checks on the mart's output.

## Proving the tests actually catch bad data
The seed data was deliberately written with three problems: a null
`customer_id`, a `status` value outside the accepted set, and a duplicate
`order_id`. Running `dbt build` against this data produced exactly three
test failures - `accepted_values_stg_orders_status`,
`not_null_stg_orders_customer_id`, and `unique_stg_orders_order_id` - each
reporting "Got 1 result, configured to fail if != 0", matching precisely
the three planted problems. The seed was then corrected and reloaded with
`dbt build --full-refresh`, and every one of the 10 checks (1 seed, 1 view
model, 1 table model, 7 tests) passed.

## Verification
Rather than trust the green build, `dbt show --select mart_customer_revenue`
was used to inspect the actual output: nine customers, each with exactly
one completed order, and each `total_revenue` value matched that order's
amount exactly on manual cross-check.

## Key takeaway
A dbt test only earns trust once you've watched it fail on data it should
reject - the same principle applied throughout this project to Airflow
retries, branches, and dynamic mapping, now applied to a tool whose entire
purpose is data quality assurance. `ref()` is also what makes dbt's
lineage graph meaningful rather than cosmetic: it is the literal dependency
that determines both execution order and the diagram `dbt docs` renders.
