# Day 36 — Window Functions for Analytics

## Goal
A change of pace from dbt plumbing - this is pure SQL skill. "Rank customers by revenue" and
"calculate a running total" are two of the most commonly asked data engineering interview
questions. This exercise builds a proper analytical mart using window functions on top of
mart_customer_revenue, and proves the output is mathematically correct by hand-calculating the
expected values first and checking dbt's actual output against them.

## The model
mart_customer_revenue_ranked.sql adds three window function columns over mart_customer_revenue:
- revenue_rank: RANK() OVER (ORDER BY total_revenue DESC)
- revenue_dense_rank: DENSE_RANK() OVER (ORDER BY total_revenue DESC)
- running_total_revenue: SUM(total_revenue) OVER (ORDER BY total_revenue DESC, customer_id ASC
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

## A real bug caught by checking actual values, not trusting the compile
The first version of this model ordered RANK() and DENSE_RANK() by
`total_revenue DESC, customer_id ASC` - the same secondary sort key used for the running total.
After planting a genuine tie (two customers both at exactly 50.00 revenue), the output showed no
tie at all: ranks 2 and 3, not 2 and 2. The bug: once customer_id is part of a RANK()/DENSE_RANK()
window's own ORDER BY, every row's full sort key becomes unique, so the function never sees a tie
to begin with - silently defeating the entire point of ranking by revenue. The fix was to order
RANK() and DENSE_RANK() by total_revenue alone, while keeping the secondary customer_id sort only
on the running total, which genuinely needs a stable row order to be deterministic.

## Proof

Baseline (no ties) - all 9 original customers, order matches hand-calculation exactly:

| customer_id | total_revenue | revenue_rank | revenue_dense_rank | running_total |
|---|---|---|---|---|
| 106 | 60.00 | 1 | 1 | 60.00 |
| 112 | 50.00 | 2 | 2 | 110.00 |
| 109 | 45.00 | 3 | 3 | 155.00 |
| 102 | 40.00 | 4 | 4 | 195.00 |
| 114 | 37.20 | 5 | 5 | 232.20 |
| 104 | 33.75 | 6 | 6 | 265.95 |
| 101 | 25.50 | 7 | 7 | 291.45 |
| 108 | 22.00 | 8 | 8 | 313.45 |
| 111 | 19.99 | 9 | 9 | 333.44 |

With a genuine planted tie (customer 116 added at 50.00, tying customer 112) - RANK and
DENSE_RANK now genuinely diverge, matching the hand-calculation exactly:

| customer_id | total_revenue | revenue_rank | revenue_dense_rank | running_total |
|---|---|---|---|---|
| 106 | 60.00 | 1 | 1 | 60.00 |
| 112 | 50.00 | 2 | 2 | 110.00 |
| 116 | 50.00 | 2 | 2 | 160.00 |
| 109 | 45.00 | 4 | 3 | 205.00 |
| 102 | 40.00 | 5 | 4 | 245.00 |
| 114 | 37.20 | 6 | 5 | 282.20 |
| 104 | 33.75 | 7 | 6 | 315.95 |
| 101 | 25.50 | 8 | 7 | 341.45 |
| 108 | 22.00 | 9 | 8 | 363.45 |
| 111 | 19.99 | 10 | 9 | 383.44 |

RANK skips straight from 2 to 4 after the tie; DENSE_RANK continues at 3. The tie was left in the
committed data deliberately, so this proof is reproducible by anyone who clones the repo.

## Key takeaway
RANK() and DENSE_RANK() only recognize a tie when the tied rows have genuinely identical sort
keys in that window's own ORDER BY - adding any extra tiebreaker column directly into a ranking
function's ORDER BY silently eliminates every tie it could ever detect, which is an easy mistake
to make and an easy one to miss without checking real output against real ties.
