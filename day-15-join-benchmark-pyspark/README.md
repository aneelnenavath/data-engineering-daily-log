# Day 15 — Join Strategy Benchmark (PySpark)

The PySpark counterpart to Day 8's MySQL `EXPLAIN`-based join comparison:
instead of reading query plans in isolation, this actually times two join
strategies against the same data and confirms the chosen physical plan
for each.

## Data

- `customers_dim.csv` — 10 rows, a genuinely small dimension table.
- `orders_large.csv` — 50,000 rows, a fact table referencing those 10
  customers, generated with a fixed random seed for reproducibility.

## The two strategies (`join_benchmark.py`)

1. **No hint** — `spark.sql.autoBroadcastJoinThreshold` set to `-1` to
   force Spark away from its own automatic broadcast heuristic, so the
   join has to shuffle both sides across the cluster and sort-merge them.
2. **Broadcast hint** — the small `customers` table wrapped in
   `broadcast()`, telling Spark explicitly to ship the whole table to
   every executor instead of shuffling anything.

Each was run 3 times and averaged, and `explain()` was called on both to
confirm the physical plan Spark actually chose, rather than assuming the
hint did what it was supposed to.

## Results

| Strategy | Physical plan operator | Avg. time (3 trials) |
|---|---|---|
| No hint | `SortMergeJoin` | 1.183s |
| Broadcast hint | `BroadcastHashJoin` | 0.343s |

Broadcast was **3.45x faster**. Both joins correctly returned all 50,000
rows — confirmed identical, so the speed difference is purely about
execution strategy, not a difference in correctness or a dropped row.

## Why this matters

A `SortMergeJoin` has to shuffle every row of the large `orders` table
across the network so matching keys land on the same executor -
expensive, and its cost scales with the size of *both* tables. A
`BroadcastHashJoin` instead sends the small `customers` table (a few KB)
to every executor once, so each executor can complete the join entirely
from its local partition of `orders` with no shuffle of the large table
at all. Spark already does this automatically for tables under its
default 10MB threshold, but the explicit `broadcast()` hint matters when
a table is small in row count but Spark's size estimate is wrong (e.g.
after several transformations), or when being explicit is simply more
reliable than trusting an automatic heuristic in a query that has to run
predictably in production.
