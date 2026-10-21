-- Day 54: Change Data Capture (CDC) basics with Postgres triggers

-- The sequence of operations run against orders_cdc:
INSERT INTO orders_cdc (order_id, customer_id, status, amount) VALUES (1, 501, 'pending', 99.50);
UPDATE orders_cdc SET status = 'completed', amount = 150.00, updated_at = now() WHERE order_id = 1;
DELETE FROM orders_cdc WHERE order_id = 1;

-- Proof: the main table has zero trace of order 1 after the delete
SELECT * FROM orders_cdc WHERE order_id = 1;
-- (0 rows)

-- Proof: the log table has the complete history regardless
SELECT log_id, operation, order_id, old_data, new_data, changed_at
FROM orders_cdc_log
ORDER BY log_id;
-- log_id 1  INSERT  old_data=NULL                 new_data={pending, 99.50}
-- log_id 2  UPDATE  old_data={pending, 99.50}      new_data={completed, 150.00}
-- log_id 3  DELETE  old_data={completed, 150.00}   new_data=NULL
