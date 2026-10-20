DROP TABLE IF EXISTS orders_dupes;

CREATE TABLE orders_dupes (
    order_id INT,
    customer_id INT,
    status TEXT,
    amount NUMERIC(10,2),
    updated_at TIMESTAMP
);

-- 500 unique orders, original version, all pending, timestamp T0
INSERT INTO orders_dupes (order_id, customer_id, status, amount, updated_at)
SELECT
    gs,
    (random() * 1000)::int,
    'pending',
    round((random() * 500 + 10)::numeric, 2),
    TIMESTAMP '2026-10-01 09:00:00'
FROM generate_series(1, 500) AS gs;

-- Exact resends for order_id 1-150: identical row, same timestamp
-- (simulates a message delivered twice - DISTINCT can catch this)
INSERT INTO orders_dupes (order_id, customer_id, status, amount, updated_at)
SELECT order_id, customer_id, status, amount, updated_at
FROM orders_dupes
WHERE order_id BETWEEN 1 AND 150;

-- Stale-vs-updated duplicates for order_id 151-300: same order_id,
-- but status/amount changed and a later timestamp
-- (simulates a status update arriving as a new row instead of an UPDATE -
--  DISTINCT cannot catch this, the rows are genuinely different)
INSERT INTO orders_dupes (order_id, customer_id, status, amount, updated_at)
SELECT
    order_id,
    customer_id,
    'completed',
    amount + 5.00,
    TIMESTAMP '2026-10-02 14:30:00'
FROM orders_dupes
WHERE order_id BETWEEN 151 AND 300 AND updated_at = TIMESTAMP '2026-10-01 09:00:00';
