DROP TABLE IF EXISTS orders_feed;
DROP TABLE IF EXISTS orders_current;

CREATE TABLE orders_feed (
    order_id integer,
    customer_id integer,
    status text,
    amount numeric,
    updated_at timestamp
);

INSERT INTO orders_feed
SELECT
    gs AS order_id,
    (random() * 999)::int + 1 AS customer_id,
    (ARRAY['pending','completed','cancelled'])[floor(random() * 3 + 1)] AS status,
    round((random() * 500)::numeric, 2) AS amount,
    now() AS updated_at
FROM generate_series(1, 5000) AS gs;

-- Deliberately NO primary key or unique constraint here yet - this is the mistake.
CREATE TABLE orders_current (
    order_id integer,
    customer_id integer,
    status text,
    amount numeric,
    updated_at timestamp
);

SELECT count(*) FROM orders_feed;
