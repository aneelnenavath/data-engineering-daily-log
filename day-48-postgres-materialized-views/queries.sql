-- Day 48: Postgres Materialized Views
-- Proof queries and results, in order run.

-- Setup: reused perf_orders (500,000 rows, from Days 45-46). Built a plain VIEW and an
-- identically-defined MATERIALIZED VIEW, both aggregating total orders and total revenue
-- per customer. Full setup in setup_materialized_view.sql.

-- Proof 1a: a filtered query against the plain view - the planner pushes the WHERE clause
-- down through the view definition and uses the existing customer_id index before
-- aggregating, so this is actually fast (1.312 ms). A plain view is not inherently slow.
EXPLAIN ANALYZE SELECT * FROM customer_revenue_summary WHERE customer_id = 12345;

-- Proof 1b: a query with no filter to push down - top 10 customers by revenue. This must
-- aggregate all 500,000 rows into all 49,999 customer groups every single time.
-- Result: GroupAggregate over the full table, Execution Time: 655.421 ms.
EXPLAIN ANALYZE SELECT * FROM customer_revenue_summary ORDER BY total_revenue DESC LIMIT 10;

-- Proof 2: the identical query against the MATERIALIZED view.
-- Result: plain Seq Scan over the already-computed 49,999 rows, no aggregation at query
-- time at all. Execution Time: 10.524 ms - roughly a 62x speedup.
EXPLAIN ANALYZE SELECT * FROM customer_revenue_summary_mat ORDER BY total_revenue DESC LIMIT 10;

-- Proof 3: the limitation - staleness. Baseline for customer 1 in both views: 2 orders,
-- $243.06 total revenue (matching).
SELECT * FROM customer_revenue_summary WHERE customer_id = 1;
SELECT * FROM customer_revenue_summary_mat WHERE customer_id = 1;

-- Simulated a new order arriving for customer 1:
INSERT INTO perf_orders (order_id, customer_id, status, amount, order_date)
VALUES (500001, 1, 'completed', 5000.00, CURRENT_DATE);

-- Rechecked both views:
-- Plain view:        3 orders, $5243.06 - picked up the new order INSTANTLY (it recomputes
--                     live on every query).
-- Materialized view:  still 2 orders, $243.06 - completely unaware the new row exists, even
--                     though it is sitting right there in perf_orders.
SELECT * FROM customer_revenue_summary WHERE customer_id = 1;
SELECT * FROM customer_revenue_summary_mat WHERE customer_id = 1;

-- Fix: explicitly refresh the materialized view.
REFRESH MATERIALIZED VIEW customer_revenue_summary_mat;
-- Rechecked: now shows 3 orders, $5243.06 - back in sync with the live data.
SELECT * FROM customer_revenue_summary_mat WHERE customer_id = 1;

-- Bonus: REFRESH MATERIALIZED VIEW CONCURRENTLY avoids taking an exclusive lock during
-- refresh (a plain REFRESH blocks all reads against the view while it rebuilds). It requires
-- a unique index on the materialized view to work at all - the reason
-- setup_materialized_view.sql created one on customer_id. Ran successfully:
REFRESH MATERIALIZED VIEW CONCURRENTLY customer_revenue_summary_mat;
