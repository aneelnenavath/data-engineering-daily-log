-- Proof 1: highly selective lookup (customer_id)
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE customer_id = 12345;
CREATE INDEX idx_perf_orders_customer_id ON perf_orders(customer_id);
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE customer_id = 12345;

-- Proof 2: moderately selective filter (~33% of rows, one status value)
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE status = 'completed';
CREATE INDEX idx_perf_orders_status ON perf_orders(status);
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE status = 'completed';

-- Proof 3: low selectivity filter (~67% of rows, two status values)
EXPLAIN ANALYZE SELECT * FROM perf_orders WHERE status IN ('completed', 'pending');
