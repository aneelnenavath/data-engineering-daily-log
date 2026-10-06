# Day 38 — dbt Unit Tests

## Goal
Every test built so far in this project - unique, not_null, the custom non_negative test, source
freshness - checks data that has already been built into a real table. dbt's unit testing feature
(available since dbt 1.8) works differently: it tests the SQL transformation logic itself against
small, fixed, mocked input rows defined directly in YAML, completely independent of whatever
actually sits in the seeds - the same idea as a unit test in regular software, applied to a
transformation query.

## The test
A unit test was written for mart_customer_revenue, which sums order amounts per customer but only
for orders with status = 'completed'. The mocked input rows use customer_ids (201, 202) that don't
exist anywhere in the real seed data on purpose - the whole point is the test shouldn't depend on
it. The mock includes a pending order and a cancelled order deliberately, specifically to exercise
the filter logic:

    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: 1, customer_id: 201, amount: 10.00, status: 'completed'}
          - {order_id: 2, customer_id: 201, amount: 20.00, status: 'completed'}
          - {order_id: 3, customer_id: 201, amount: 999.00, status: 'pending'}
          - {order_id: 4, customer_id: 202, amount: 50.00, status: 'completed'}
          - {order_id: 5, customer_id: 202, amount: 999.00, status: 'cancelled'}
    expect:
      rows:
        - {customer_id: 201, num_orders: 2, total_revenue: 30.00}
        - {customer_id: 202, num_orders: 1, total_revenue: 50.00}

## Proof

| Step | Result |
|---|---|
| Correct model, unit test run | PASS - 0.27s, entirely against mocked data |
| status = 'completed' filter deliberately removed from the model | FAIL - dbt's diff showed customer_id 201: total_revenue 30.0->1029.0, customer_id 202: total_revenue 50.0->1049.0, tracing exactly back to the pending and cancelled orders getting incorrectly counted |
| Filter restored, full dbt build re-run | PASS - 36/36, unit test included |

## Key takeaway
A data test (unique, not_null, source freshness) proves something about data that's already been
loaded - it can only catch a problem after the fact, and only if the real data happens to contain
a case that exposes it. A unit test proves something about the transformation logic itself, using
input you deliberately construct to exercise exactly the edge cases you care about - here, a
pending and a cancelled order specifically chosen to catch a broken status filter - regardless of
whether today's real data happens to contain that edge case at all. Both matter, but they catch
different classes of bugs, and dbt's own diff output on a unit test failure (showing the exact
before/after per row) is as precise as any assertion failure from a regular software test suite.
