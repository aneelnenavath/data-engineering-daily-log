# Day 18 — Partitioned Parquet Table

Writes a Parquet table partitioned by `order_date` and confirms partition
pruning actually happens, rather than just trusting that partitioning
"should" make date-filtered queries faster.

## Data

3,515 synthetic orders spanning 30 distinct days (Jan 1-30, 2026),
generated with a fixed random seed for reproducibility.

## Writing the partitioned table

```python
df.write.mode("overwrite").partitionBy("order_date").parquet("sales_partitioned")
```

This produces one physical subdirectory per distinct date -
`order_date=2026-01-01/`, `order_date=2026-01-02/`, etc. - each holding
only that day's rows, confirmed directly with `ls sales_partitioned/`.

## Proving pruning, not just describing it

Two `explain()` calls, read side by side:

- **No filter (baseline)**: `PartitionFilters: []` - Spark has no reason
  to skip any partition directory, so a query like this would have to
  open all 30.
- **Filtered on `order_date = '2026-01-15'`**:
  `PartitionFilters: [isnotnull(order_date#43), (order_date#43 = 2026-01-15)]`
  - the filter was pushed down into the scan itself. Spark now knows,
  before reading a single row, that only the `order_date=2026-01-15/`
  directory can possibly match, and skips the other 29 entirely.

That's the actual mechanism partition pruning relies on: because the
partition value is encoded in the directory name rather than inside the
Parquet files themselves, Spark can decide which directories to open
using the query's filter alone, with zero file I/O spent on the
partitions it excludes.

## Correctness cross-check

The filtered query returned 120 rows for `2026-01-15`. Counting that
same date directly from the raw CSV - with no Spark, no partitioning,
no query planner involved at all - also gives 120. Confirms the
partitioned table isn't just fast, it's still correct.
