CREATE KEYSPACE IF NOT EXISTS ecommerce WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE ecommerce;

CREATE TABLE orders_by_customer (
  customer_id int,
  order_id int,
  order_date timestamp,
  product_name text,
  amount decimal,
  PRIMARY KEY (customer_id, order_id)
);

CREATE TABLE orders_by_product (
  product_name text,
  order_id int,
  customer_id int,
  order_date timestamp,
  amount decimal,
  PRIMARY KEY (product_name, order_id)
);

INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (1, 101, '2026-09-01', 'Laptop', 999.99);
INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (1, 102, '2026-09-03', 'Headphones', 79.99);
INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (2, 103, '2026-09-02', 'Laptop', 999.99);
INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (2, 104, '2026-09-05', 'Desk Chair', 149.50);
INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (3, 105, '2026-09-04', 'Headphones', 79.99);
INSERT INTO orders_by_customer (customer_id, order_id, order_date, product_name, amount) VALUES (3, 106, '2026-09-06', 'Laptop', 999.99);

INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Laptop', 101, 1, '2026-09-01', 999.99);
INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Headphones', 102, 1, '2026-09-03', 79.99);
INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Laptop', 103, 2, '2026-09-02', 999.99);
INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Desk Chair', 104, 2, '2026-09-05', 149.50);
INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Headphones', 105, 3, '2026-09-04', 79.99);
INSERT INTO orders_by_product (product_name, order_id, customer_id, order_date, amount) VALUES ('Laptop', 106, 3, '2026-09-06', 999.99);
