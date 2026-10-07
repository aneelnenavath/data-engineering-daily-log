# Day 42 — dbt Model Contracts

## What this is

An enforced contract on `mart_customer_revenue`, declaring its exact column names and
data types up front (`customer_id: integer`, `num_orders: bigint`, `total_revenue:
double` - confirmed against the model's real DuckDB types via `information_schema.columns`
before writing the contract). Unlike a data test, which checks a table's contents after
it's already been built, a contract is checked at compile/build time - dbt refuses to
create the table at all if its actual output doesn't match what was declared.

```yaml
- name: mart_customer_revenue
  config:
    contract:
      enforced: true
  columns:
    - name: customer_id
      data_type: integer
    - name: num_orders
      data_type: bigint
    - name: total_revenue
      data_type: double
```

## Proof 1 — a missing column is caught before the table is ever created

Removed `num_orders` from the model's `select`. Running just the model (`dbt run
--select mart_customer_revenue`, bypassing tests) produced a compilation error, not a
runtime one: `This model has an enforced contract that failed`, with a table showing
`num_orders | (blank) | BIGINT | missing in definition`. No table was created at all.

## Proof 2 — a type mismatch is caught the same way

Restored the column, then changed `total_revenue` to `cast(round(sum(amount)) as
integer)`. Same result: `total_revenue | INTEGER | DOUBLE | data type mismatch`,
caught before any DDL ran.

## An interesting interaction worth noting

The very first attempt to prove the missing-column case didn't surface the contract
error at all - it surfaced a *different* error first. This project's Day 38 unit test
on this same model expects `num_orders` in its output rows, and dbt validates a unit
test's expected columns against the model's real compiled output before ever reaching
the contract check. With `num_orders` removed, the unit test failed with "Invalid
column name: 'num_orders'... Accepted columns are: ['customer_id', 'total_revenue']",
and `dbt build`'s DAG-aware ordering skipped the model entirely as a result - so the
contract check was never even reached under `dbt build`. Only bypassing tests entirely
with `dbt run --select mart_customer_revenue` revealed the contract's own error
message directly. Two independent safety nets caught the same break from two different
layers; which one you see first just depends on build order.

## Final state

Model restored to its correct shape, contract still enforced. Full `dbt build` passed
cleanly: 50/50 (2 incremental models, 3 project hooks, 4 seeds, 1 snapshot, 3 table
models, 34 data tests, 1 unit test, 2 view models).

## Key takeaway

A test catches a schema-breaking change only after a bad table already exists and only
if a test happens to be watching the right column. A contract catches it structurally,
for every declared column, before the table is ever built - a stronger guarantee,
though only as strong as the "every column, every time" declaration behind it. Worth
remembering too: dbt's own layers of defense (tests, unit tests, contracts) don't
always fire in the order you'd expect, and only running them in isolation revealed
which one was actually responsible for which error.
