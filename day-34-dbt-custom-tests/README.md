# Day 34 — Writing a Custom Generic dbt Test

## Goal
Every test used in this project so far has been one of dbt's four built-in generic tests - unique,
not_null, accepted_values, and relationships. Real projects constantly need business-rule checks
that don't exist out of the box, like "revenue can never be negative." This exercise writes a
custom, reusable generic test macro from scratch and proves it genuinely catches a violation.

## The custom test
A new macro, non_negative, defined in tests/generic/test_non_negative.sql:

    {% test non_negative(model, column_name) %}
    select *
    from {{ model }}
    where {{ column_name }} < 0
    {% endtest %}

Like every dbt test, it's just a query that should return zero rows - the same mechanism behind
the built-in tests, just written by hand. It's applied to mart_customer_revenue.total_revenue in
models/marts/schema.yml the exact same way a built-in test would be:

    - name: total_revenue
      tests:
        - not_null
        - non_negative

## Proof

| Step                              | Result                                                        |
|-------------------------------------|------------------------------------------------------------------|
| Clean build, legitimate data         | PASS non_negative_mart_customer_revenue_total_revenue (20/20)      |
| Planted a completed order with amount -50.00 | FAIL 1 non_negative... - "Got 1 result, configured to fail if != 0" |
| Bad row removed, rebuilt             | Back to PASS, 20/20                                               |

## Key takeaway
A custom dbt test is not a different kind of object from a built-in one - dbt's own error message
("Got 1 result, configured to fail if != 0") makes the mechanism explicit: every test, built-in or
custom, is just a SQL query that is expected to return no rows. Once that clicks, writing a test
for any business rule a real project needs - a discount that can't exceed 100%, a date that can't
be in the future, a status that must follow a valid state machine - is just writing the right
select ... where <violation> query and wrapping it in {% test %}.
