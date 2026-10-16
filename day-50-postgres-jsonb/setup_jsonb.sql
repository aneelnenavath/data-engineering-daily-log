DROP TABLE IF EXISTS orders_meta;

CREATE TABLE orders_meta (
    order_id integer,
    customer_id integer,
    metadata jsonb
);

INSERT INTO orders_meta
SELECT
    gs AS order_id,
    (random() * 999)::int + 1 AS customer_id,
    jsonb_build_object(
        'payment_method', (ARRAY['card','paypal','bank_transfer','gift_card'])[floor(random() * 4 + 1)],
        'shipping', jsonb_build_object(
            'country', (ARRAY['UK','US','DE','FR','IN'])[floor(random() * 5 + 1)],
            'express', (random() < 0.2)
        ),
        'vip', (random() < 0.05),
        'tags', (
            SELECT jsonb_agg(tag) FROM (
                SELECT (ARRAY['gift','fragile','bulk','sale'])[floor(random() * 4 + 1)] AS tag
                FROM generate_series(1, (floor(random() * 3) + 1)::int)
            ) t
        )
    ) AS metadata
FROM generate_series(1, 500000) AS gs;

SELECT count(*) FROM orders_meta;
