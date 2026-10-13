# Day 46 — Postgres Table Partitioning

## Topic

Yesterday (Day 45) sped up queries by adding an index on top of a single large table.
Today looks at a different technique: physically splitting one large table into smaller
pieces (partitions) so Postgres can skip reading entire pieces that can't possibly contain
the rows a query needs. This is called partition pruning, and it's a different mechanism
from indexing, with its own strengths and its own sharp limitation.

## Setup

Reused the 500,000-row `perf_orders` table built on Day 45 (same Postgres container,
still running) as a non-partitioned baseline. Built a second table, `perf_orders_partitioned`,
with identical columns and identical data, but declared with `PARTITION BY RANGE (order_date)`
and split into 13 monthly partitions covering October 2025 through October 2026. All 500,000
rows were copied in with a single INSERT, and Postgres automatically routed each row into the
correct monthly partition based on its own `order_date` value. Full setup is in
`setup_partitioning.sql`, full proof queries are in `queries.sql`.

## Proof 1 — partition pruning on the partition key

Filtering both tables down to a single month (March 2026, about 42,000 of the 500,000 rows):

    Non-partitioned table:  Seq Scan on perf_orders, full 500,000 rows scanned,
                             457,553 rows removed by filter. Execution Time: 773.183 ms

    Partitioned table:      Seq Scan on perf_orders_p2026_03 ONLY - the other 12
                             partitions were never opened. Execution Time: 69.938 ms

That's roughly an 11x speedup, achieved with zero indexes - purely from the planner being
able to prove in advance that only one partition could contain matching rows, and skipping
the rest entirely.

## Proof 2 — the limitation: pruning only works on the partition key

Filtering the partitioned table on `customer_id` instead - a column with no relationship to
how the table is physically split by date:

    Partitioned table (no index on customer_id):  Parallel Seq Scan across ALL 13
                             partitions individually. Execution Time: 262.393 ms

No pruning happened at all, because the planner has no way to know which partition a given
customer_id might fall into - that information simply isn't encoded in how the table is split.
For comparison, the plain non-partitioned table still has the `idx_perf_orders_customer_id`
index from Day 45, and running the identical filter against it:

    Non-partitioned table (WITH existing index):  Bitmap Index Scan.
                             Execution Time: 5.641 ms

The indexed non-partitioned table beat the partitioned table by about 46x on this query.
Partitioning is not a general-purpose speed-up - it only helps when a query filters on the
column the table is partitioned by.

## Closing the loop — partitioning and indexing work together, not instead of each other

Added an index on `customer_id` directly to the partitioned table:

    CREATE INDEX ON perf_orders_partitioned (customer_id);

Postgres created one real B-tree index per partition automatically (13 physical indexes
behind one logical "partitioned index"). Rerunning the same customer_id filter:

    Partitioned table (WITH its own index):  Bitmap Index Scan on each partition's
                             own small customer_id index - still no pruning across
                             partitions, but each per-partition probe is now cheap.
                             Execution Time: 6.373 ms

That matches the non-partitioned indexed table's performance almost exactly. Partitioning
and indexing solve different problems: partitioning helps the planner skip whole chunks of
a table when a query filters on the partition key, while an index helps find specific rows
within whatever is actually scanned, partition key or not. A real table that's both large and
queried on multiple different columns typically needs both, not one instead of the other.

## What to remember going forward

Partition pruning is a real, measured win (about 11x here), but it is conditional, not
automatic: it only fires when a query's filter lines up with the column the table is
partitioned by. Filtering on anything else gets no benefit from partitioning alone, and can
even be slower than a plain indexed table if the partitions themselves aren't indexed too.
The two techniques are complementary, confirmed here by adding an index to the partitioned
table and watching its performance on a non-partition-key filter catch up to the plain
indexed table.
