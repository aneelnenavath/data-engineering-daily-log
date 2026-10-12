# Day 45 — SQL Performance Tuning with EXPLAIN ANALYZE

## What this is

A genuine before/after proof of indexing, run against a synthetic 500,000-row Postgres
table (perf_orders) generated specifically to be large enough that indexing effects
actually show up - the project's existing datasets are far too small for EXPLAIN plans
to show anything meaningful. Three different filter conditions were tested, chosen
deliberately to span highly selective, moderately selective, and barely selective at
all - the full range of how an index actually behaves, not just the one case where it
obviously helps.

## Proof 1 - a highly selective lookup: dramatic improvement

Filtering on customer_id = 12345 (one of 50,000 possible values, matching only a
handful of rows) started as a Seq Scan at 47.058 ms execution time. After creating an
index on customer_id, the same query used a Bitmap Index Scan and dropped to 0.608 ms -
roughly a 77x improvement.

## Proof 2 - a moderately selective filter: a real surprise worth correcting

Filtering on status = 'completed' (roughly a third of all 500,000 rows, since status
has three evenly split values) started as a Seq Scan at 90.830 ms. The initial
prediction here was that an index would not help at all at this selectivity - but after
creating an index on status, the planner actually used it anyway, as a Bitmap Index
Scan, and execution time dropped to 54.011 ms. The reason the prediction was wrong: a
bitmap scan is a different strategy from a plain index scan. It collects every matching
row's location first, sorts those locations by physical table page, and then reads the
table in that more sequential-friendly order - which lets it still provide real benefit
even at moderate selectivity, instead of being limited to the "a handful of rows" case a
plain index scan is best at.

## Proof 3 - a low selectivity filter: the real crossover point

Filtering on status IN ('completed', 'pending') (roughly two thirds of all rows) came
back as a plain Seq Scan at 116.732 ms, even with the status index still in place from
Proof 2. At this selectivity, the planner correctly determined that reading almost the
whole table directly was cheaper than the overhead of using the index at all, and
skipped it entirely.

## Key takeaway


There is no fixed selectivity percentage above which an index stops helping - Postgres's
planner makes this decision based on actual estimated cost, not a simple rule of thumb,
and a bitmap index scan specifically changes the economics at moderate selectivity
compared to what a plain index scan could do. Having an initial prediction turn out wrong
here, and digging into the real reason rather than just re-asserting the simple version,
produced a more accurate and more useful understanding than if the first guess had
simply been correct.
