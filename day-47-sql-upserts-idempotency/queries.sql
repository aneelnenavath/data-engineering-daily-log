-- Day 47: SQL Upserts and Idempotent Loads
-- Proof queries and results, in order run.

-- Setup: orders_feed (5,000-row staging table simulating a daily extract) and orders_current
-- (the target table a pipeline loads into), initially created WITHOUT a primary key - that
-- missing constraint is the root of today's bug. Full setup in setup_upsert_demo.sql.

-- Proof 1: the naive, append-only load, run as if a pipeline retried after a transient failure.
-- First run (normal daily load):
INSERT INTO orders_current SELECT * FROM orders_feed;
-- Result: INSERT 0 5000, count(*) = 5000 - looks correct.

-- Second run (simulated retry of the exact same job):
INSERT INTO orders_current SELECT * FROM orders_feed;
-- Result: INSERT 0 5000 again - NO ERROR RAISED - count(*) jumped to 10000.
-- Confirmed concretely: SELECT * FROM orders_current WHERE order_id = 1 returned TWO
-- byte-for-byte identical rows. Every downstream aggregate on this table is now silently
-- doubled, with nothing in the logs indicating anything went wrong.

-- Fix: rebuild the target table with a real primary key, which a naive design had skipped.
DROP TABLE orders_current;
CREATE TABLE orders_current (
    order_id integer PRIMARY KEY,
    customer_id integer,
    status text,
    amount numeric,
    updated_at timestamp
);

-- Proof 2: the upsert load (see upsert_load.sql), run twice.
-- First run: INSERT 0 5000, count(*) = 5000 (all fresh inserts, no conflicts yet).
-- Second run (identical rerun): INSERT 0 5000 again, but count(*) stayed at 5000.
-- Note: "INSERT 0 5000" on the second run does NOT mean 5000 new rows were added - it's the
-- total number of rows the statement PROCESSED, including every row that hit ON CONFLICT
-- and became an update instead of a fresh insert. The idempotency proof is the unchanged
-- row count, not the message itself.
INSERT INTO orders_current (order_id, customer_id, status, amount, updated_at)
SELECT order_id, customer_id, status, amount, updated_at
FROM orders_feed
ON CONFLICT (order_id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    status = EXCLUDED.status,
    amount = EXCLUDED.amount,
    updated_at = EXCLUDED.updated_at;

-- Proof 3: upserts aren't just deduplication - they genuinely reflect real source changes.
-- Mutated order 1 in the SOURCE feed:
UPDATE orders_feed SET status = 'completed', amount = 999.99 WHERE order_id = 1;

-- Reran the exact same upsert_load.sql script (no code change at all), then checked order 1:
-- Result: order_id 1 now shows status = 'completed', amount = 999.99 - the real change
-- propagated correctly - still exactly ONE row, and count(*) is still 5000.
