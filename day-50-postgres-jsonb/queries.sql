-- Day 50: Postgres JSONB
-- Proof queries and results, in order run.

-- Setup: orders_meta (500,000 rows) with a jsonb metadata column holding payment_method,
-- a nested shipping object (country, express), a vip boolean, and a tags array - a realistic
-- example of semi-structured data sitting inside an otherwise relational table. Full setup
-- in setup_jsonb.sql.

-- Operator demo: -> returns a jsonb value, ->> returns text, and they chain for nested paths.
SELECT metadata -> 'payment_method' AS as_json,
       metadata ->> 'payment_method' AS as_text,
       metadata -> 'shipping' ->> 'country' AS nested_country
FROM orders_meta WHERE order_id = 1;
-- Result: as_json = "gift_card" (quoted, still jsonb), as_text = gift_card (plain text),
-- nested_country = IN (reached through the nested shipping object).

-- Proof 1: a containment query on a single, moderately selective condition (~25% of rows
-- match payment_method = paypal), with NO index on the jsonb column yet.
EXPLAIN ANALYZE SELECT count(*) FROM orders_meta
WHERE metadata @> '{"payment_method": "paypal"}';
-- Result: Parallel Seq Scan across all 500,000 rows. Execution Time: 142.532 ms.

-- Fix: add a GIN index, built specifically for indexing inside composite/jsonb values.
CREATE INDEX idx_orders_meta_gin ON orders_meta USING GIN (metadata);

-- Proof 2: the identical single-condition query, now with the GIN index available.
EXPLAIN ANALYZE SELECT count(*) FROM orders_meta
WHERE metadata @> '{"payment_method": "paypal"}';
-- Result: Bitmap Heap Scan using idx_orders_meta_gin. Execution Time: 108.546 ms - only a
-- modest ~24% improvement, because the filter still matches ~25% of the table (124,864 rows),
-- and a Bitmap Heap Scan still has to visit a large fraction of the table's actual heap blocks
-- no matter how it found them.

-- Proof 3: a MORE selective query - two jsonb conditions combined (vip = true AND
-- payment_method = paypal), matching only ~1.26% of rows (6,295 of 500,000), WITH the index.
EXPLAIN ANALYZE SELECT count(*) FROM orders_meta
WHERE metadata @> '{"vip": true, "payment_method": "paypal"}';
-- Result: Bitmap Index Scan on idx_orders_meta_gin. Execution Time: 62.559 ms.
-- Plan also shows "Rows Removed by Index Recheck: 23679" and "Heap Blocks: exact=10196" -
-- a GIN index on jsonb returns a lossy bitmap of candidate rows, which Postgres must then
-- recheck against the actual heap to confirm a real match, unlike a B-tree index on a plain
-- scalar column.

-- Proof 4: the SAME selective combined-condition query, with the planner forced away from
-- using the index, for a fair apples-to-apples comparison against Proof 3.
SET enable_bitmapscan = off;
SET enable_indexscan = off;
EXPLAIN ANALYZE SELECT count(*) FROM orders_meta
WHERE metadata @> '{"vip": true, "payment_method": "paypal"}';
-- Result: Parallel Seq Scan across all 500,000 rows. Execution Time: 90.366 ms.
-- The GIN index gave a real but modest ~1.44x speedup (90.366 ms -> 62.559 ms) on this more
-- selective query - genuinely useful, but nowhere near the 10-60x+ speedups B-tree indexes
-- gave on plain scalar columns across Days 45-48.
