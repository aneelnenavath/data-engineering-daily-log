-- Day 53: SQL deduplication with window functions

-- Proof 0: confirm duplicates exist
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT order_id) AS distinct_orders
FROM orders_dupes;
-- 800 total rows, 500 distinct order_ids -> 300 duplicate rows present

-- Proof 1: naive DISTINCT only catches byte-identical duplicates
SELECT COUNT(*) FROM (SELECT DISTINCT * FROM orders_dupes) t;
-- 650 rows - caught the 150 exact resends, left all 150 stale-vs-updated
-- pairs untouched, since those rows genuinely differ column by column

-- Proof 2: ROW_NUMBER() partitioned by the business key, ordered by
-- recency, correctly collapses to one row per order
SELECT COUNT(*)
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
    FROM orders_dupes
) t
WHERE rn = 1;
-- 500 rows - exactly the true number of unique orders

-- Proof 3: confirm the kept row is genuinely the newer, correct version,
-- not an arbitrary pick
SELECT order_id, status, amount, updated_at,
       ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
FROM orders_dupes
WHERE order_id = 200
ORDER BY rn;
-- rn=1: completed, 246.91, 2026-10-02 (kept)
-- rn=2: pending,   241.91, 2026-10-01 (correctly discarded)
