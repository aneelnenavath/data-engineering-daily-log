INSERT INTO orders_current (order_id, customer_id, status, amount, updated_at)
SELECT order_id, customer_id, status, amount, updated_at
FROM orders_feed
ON CONFLICT (order_id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    status = EXCLUDED.status,
    amount = EXCLUDED.amount,
    updated_at = EXCLUDED.updated_at;
