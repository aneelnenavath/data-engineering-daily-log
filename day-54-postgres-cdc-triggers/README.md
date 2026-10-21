# Day 54 — Change Data Capture (CDC) Basics with Postgres Triggers

## What this demonstrates

Every table in this project so far has only ever shown current state -
querying it tells you what a row looks like right now, nothing about how
it got there or what it used to be. The moment a row is updated or
deleted, its previous value is gone forever unless something was
deliberately capturing that history as it happened. That's the core
idea behind Change Data Capture: recording every INSERT, UPDATE, and
DELETE as it occurs, independently of whatever the main table ends up
looking like afterward.

Production CDC systems typically read a database's write-ahead log
(e.g. Debezium against Postgres logical replication) rather than using
triggers, because triggers add overhead to every write and logical
replication doesn't. Triggers are used here because they demonstrate
the same core concept - capturing every change with its full
before/after state - using nothing but plain SQL and psql.

## The setup

orders_cdc is the main table. orders_cdc_log is a separate table that
only ever grows - rows are written to it, never updated or deleted. A
PL/pgSQL trigger function fires AFTER every INSERT, UPDATE, or DELETE on
orders_cdc and writes one row into orders_cdc_log recording the
operation type, the full old values (as JSONB, via row_to_json(OLD)),
the full new values (row_to_json(NEW)), and a timestamp - using
Postgres's special TG_OP variable to tell the three operation types
apart.

## The sequence tested

    INSERT INTO orders_cdc (order_id, customer_id, status, amount)
        VALUES (1, 501, 'pending', 99.50);
    UPDATE orders_cdc SET status = 'completed', amount = 150.00, updated_at = now()
        WHERE order_id = 1;
    DELETE FROM orders_cdc WHERE order_id = 1;

## Proof - the main table has zero memory of order 1

    SELECT * FROM orders_cdc WHERE order_id = 1;
    (0 rows)

After the delete, orders_cdc has no trace this order ever existed, was
ever updated, or had any prior values. If this table were the only
source of truth, that entire history would be permanently unrecoverable.

## Proof - the log table has the complete history regardless

    SELECT log_id, operation, order_id, old_data, new_data, changed_at
    FROM orders_cdc_log ORDER BY log_id;

    log_id | operation | old_data                  | new_data
    -------+-----------+----------------------------+----------------------------
         1 | INSERT    | NULL                       | pending,   amount=99.50
         2 | UPDATE    | pending,   amount=99.50     | completed, amount=150.00
         3 | DELETE    | completed, amount=150.00    | NULL

Every operation is captured with a full before-and-after snapshot and a
timestamp, completely independent of whatever orders_cdc itself ends up
containing. The INSERT correctly has no old_data (nothing existed yet).
The UPDATE has both the old and new values, proving the exact change
that happened. The DELETE captured the row's final state as old_data
immediately before it vanished from the main table.

## Why this matters

Querying a table only ever answers "what does this look like right
now." Auditing, debugging a data discrepancy, reconstructing what
happened before an incident, or feeding downstream systems that care
about changes rather than snapshots all require a record of every
change as it happens, not just the current state. A trigger-based log
table is the simplest possible way to demonstrate that principle;
production systems get the same effect with far lower write overhead by
reading the database's write-ahead log instead of firing a trigger on
every row.
