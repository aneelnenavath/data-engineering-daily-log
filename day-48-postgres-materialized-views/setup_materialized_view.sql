DROP MATERIALIZED VIEW IF EXISTS customer_revenue_summary_mat;
DROP VIEW IF EXISTS customer_revenue_summary;

CREATE VIEW customer_revenue_summary AS
SELECT
    customer_id,
    count(*) AS total_orders,
    sum(amount) AS total_revenue
FROM perf_orders
GROUP BY customer_id;

CREATE MATERIALIZED VIEW customer_revenue_summary_mat AS
SELECT
    customer_id,
    count(*) AS total_orders,
    sum(amount) AS total_revenue
FROM perf_orders
GROUP BY customer_id;

CREATE UNIQUE INDEX ON customer_revenue_summary_mat (customer_id);

SELECT count(*) FROM customer_revenue_summary_mat;
