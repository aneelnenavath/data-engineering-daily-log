DROP TABLE IF EXISTS perf_orders;

CREATE TABLE perf_orders AS
SELECT
    gs AS order_id,
    (random() * 49999)::int + 1 AS customer_id,
    (ARRAY['completed','pending','cancelled'])[floor(random() * 3 + 1)] AS status,
    round((random() * 500)::numeric, 2) AS amount,
    (CURRENT_DATE - (random() * 365)::int) AS order_date
FROM generate_series(1, 500000) AS gs;

SELECT count(*) FROM perf_orders;
