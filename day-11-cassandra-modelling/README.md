# Day 11 — Cassandra Data Modelling

Replaces an earlier SQLite stand-in with real Apache Cassandra, run via a
single-node `cassandra-node1` Docker container, driven through `cqlsh`.

## The core lesson: query-first modelling

Day 7 designed a MySQL schema by normalizing entities (customers, orders,
products) and relying on JOINs and indexes to answer whatever question came
up later. Cassandra rejects that approach outright: there are no ad-hoc
JOINs, and a query that doesn't hit the partition key is refused rather than
silently slow.

So instead of one normalized `orders` table, this keyspace has **two**
tables holding the same underlying data, each shaped around one query:

- `orders_by_customer` — partition key `customer_id`, clustering key
  `order_id`. Answers "all orders for this customer" efficiently.
- `orders_by_product` — partition key `product_name`, clustering key
  `order_id`. Answers "all orders for this product" efficiently.

The order data is deliberately duplicated across both tables. In Cassandra,
storage is cheap and joins are not, so denormalizing for the read pattern is
the correct design, not a shortcut.

## Setup

```bash
docker run -d --name cassandra-node1 -p 9042:9042 cassandra:latest
# wait for "Startup complete" in the logs, then:
docker exec -it cassandra-node1 cqlsh -e "DESCRIBE CLUSTER;"
```

Schema and sample data live in `schema.cql`, loaded with:

```bash
docker cp ./schema.cql cassandra-node1:/schema.cql
docker exec -it cassandra-node1 cqlsh -f /schema.cql
```

## Proof it works

```sql
SELECT * FROM ecommerce.orders_by_customer WHERE customer_id = 1;
-- returns Alice's 2 orders

SELECT * FROM ecommerce.orders_by_product WHERE product_name = 'Laptop';
-- returns all 3 customers who bought a Laptop
```

## Proof the partition key actually matters

```sql
SELECT * FROM ecommerce.orders_by_customer WHERE order_id = 103;
```

`order_id` is only a clustering key here, not the partition key, so
Cassandra can't route the query to one node — it refuses rather than scan
every partition silently. This is the concrete reason `orders_by_product`
exists as its own table instead of an index on `orders_by_customer`.
