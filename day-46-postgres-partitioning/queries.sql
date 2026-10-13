-- Day 46: Postgres Table Partitioning
-- Proof queries and results, in order run.

-- Proof 1a: date-range filter on the NON-partitioned baseline table (perf_orders, 500,000 rows)
-- Result: Seq Scan on perf_orders, full table scanned, Rows Removed by Filter: 457553
-- Execution Time: 773.183 ms
EXPLAIN ANALYZE SELECT * FROM perf_orders
WHERE order_date >= '2026-03-01' AND order_date < '2026-04-01';

-- Proof 1b: identical date-range filter on the PARTITIONED table
-- Result: Seq Scan on perf_orders_p2026_03 ONLY (partition pruning) - the other 12 partitions
-- were never touched. Execution Time: 69.938 ms (~11x faster, no index involved at all)
EXPLAIN ANALYZE SELECT * FROM perf_orders_partitioned
WHERE order_date >= '2026-03-01' AND order_date < '2026-04-01';

-- Proof 2a: filtering on a column that is NOT the partition key (customer_id), on the
-- partitioned table, BEFORE adding any index on customer_id.
-- Result: Parallel Seq Scan across ALL 13 partitions individually - no pruning was possible
-- because customer_id has no relationship to how the table is physically split.
-- Execution Time: 262.393 ms
EXPLAIN ANALYZE SELECT * FROM perf_orders_partitioned WHERE customer_id = 12345;

-- Proof 2b: the SAME customer_id filter on the NON-partitioned table, which still has the
-- idx_perf_orders_customer_id index created back on Day 45.
-- Result: Bitmap Index Scan, Execution Time: 5.641 ms - far faster than the partitioned
-- table's 262 ms for the same filter, because an index helps regardless of table layout
-- while partitioning only helps when the partition key is filtered on.
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE customer_id = 12345;

-- Fix: add a matching index on the partitioned table. Postgres creates one real index per
-- partition automatically (a single "partitioned index" backed by 13 physical indexes).
CREATE INDEX ON perf_orders_partitioned (customer_id);

-- Proof 3: rerun the customer_id filter on the partitioned table now that it has its own index.
-- Result: Bitmap Index Scan on each partition's own small customer_id index, still no pruning
-- (all 13 partitions still probed), but each probe is now cheap.
-- Execution Time: 6.373 ms - matches the non-partitioned indexed table, proving partitioning
-- and indexing solve different problems and work together rather than substituting each other.
EXPLAIN ANALYZE SELECT * FROM perf_orders_partitioned WHERE customer_id = 12345;
