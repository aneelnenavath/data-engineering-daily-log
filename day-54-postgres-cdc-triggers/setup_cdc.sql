DROP TABLE IF EXISTS orders_cdc_log;
DROP TABLE IF EXISTS orders_cdc;

CREATE TABLE orders_cdc (
    order_id INT PRIMARY KEY,
    customer_id INT,
    status TEXT,
    amount NUMERIC(10,2),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE orders_cdc_log (
    log_id SERIAL PRIMARY KEY,
    operation TEXT NOT NULL,
    order_id INT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT now()
);

CREATE OR REPLACE FUNCTION log_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO orders_cdc_log (operation, order_id, old_data, new_data)
        VALUES ('INSERT', NEW.order_id, NULL, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO orders_cdc_log (operation, order_id, old_data, new_data)
        VALUES ('UPDATE', NEW.order_id, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO orders_cdc_log (operation, order_id, old_data, new_data)
        VALUES ('DELETE', OLD.order_id, row_to_json(OLD), NULL);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_cdc_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders_cdc
FOR EACH ROW EXECUTE FUNCTION log_order_changes();
