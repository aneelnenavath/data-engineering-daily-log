DROP TABLE IF EXISTS perf_orders_partitioned CASCADE;

CREATE TABLE perf_orders_partitioned (
    order_id integer,
    customer_id integer,
    status text,
    amount numeric,
    order_date date
) PARTITION BY RANGE (order_date);

DO $$
DECLARE
    start_date date := date_trunc('month', CURRENT_DATE - interval '13 months');
    part_start date;
    part_end date;
    part_name text;
BEGIN
    FOR i IN 0..14 LOOP
        part_start := start_date + (i || ' months')::interval;
        part_end := start_date + ((i+1) || ' months')::interval;
        part_name := 'perf_orders_p' || to_char(part_start, 'YYYY_MM');
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF perf_orders_partitioned FOR VALUES FROM (%L) TO (%L)',
            part_name, part_start, part_end
        );
    END LOOP;
END $$;

INSERT INTO perf_orders_partitioned SELECT * FROM perf_orders;

SELECT count(*) FROM perf_orders_partitioned;
