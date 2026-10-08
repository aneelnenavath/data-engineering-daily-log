# Day 43 — Great Expectations

## Why this day is different

Every data quality safeguard in this project so far has been built with dbt's own
tooling (tests, unit tests, snapshots, contracts). This day deliberately steps outside
dbt entirely: Great Expectations is a standalone Python data validation library, used
here to validate the same `raw_orders.csv` seed completely independently of dbt - a
common real-world pattern is validating raw data with a tool like this *before* it ever
enters a dbt project.

## What this is

A Python script (`ge_validate_orders.py`) that loads the orders seed with pandas, wraps
it as a Great Expectations "batch," and runs five expectations against it:

```python
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="amount"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(column="status", value_set=["completed", "pending", "cancelled"]))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="amount", min_value=0))

results = batch.validate(suite)
```

## Proof 1 — a clean baseline passes all five expectations

Running the script against the real seed data produced `SUCCESS: True`, with all five
expectations individually reporting `success=True`.

## Proof 2 — two different planted problems, each caught precisely

Two bad rows were added: one with a negative amount (-75.00), one with a status value
outside the accepted set (`refunded`). Rerunning the script produced `SUCCESS: False`,
with exactly the two relevant expectations failing - `expect_column_values_to_be_between`
and `expect_column_values_to_be_in_set` - while the other three (not-null checks,
uniqueness) correctly stayed `True`, since nothing about those columns had actually
broken.

## Proof 3 — not just pass/fail, the exact failing values

The script was extended to surface each failed expectation's `partial_unexpected_list`
and `unexpected_count`. Output showed `FAILING VALUES: [-75.0] (unexpected_count=1)` for
the amount check and `FAILING VALUES: ['refunded'] (unexpected_count=1)` for the status
check - precise, not just "this expectation failed."

## Final state

Both bad rows were removed and the script rerun, confirming a clean `SUCCESS: True`
again.

## Key takeaway

Great Expectations and dbt's built-in tests solve a very similar problem - asserting
facts about data and failing loudly when they're violated - but from different layers
and in different ecosystems. dbt tests live inside the transformation layer and run as
part of a `dbt build`; Great Expectations is standalone and dataframe/table-agnostic,
commonly used to validate data *before* it's trusted enough to feed into a pipeline at
all, or in non-dbt Python pipelines entirely. Knowing both - and knowing which kind of
project reaches for which - is a genuinely useful thing to be able to speak to, rather
than treating "data testing" as a single tool.
