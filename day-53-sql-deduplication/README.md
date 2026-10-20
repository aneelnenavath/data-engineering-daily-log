# Day 53 — SQL Deduplication with Window Functions

## What this demonstrates

Real data feeds routinely contain duplicate records - the same logical
entity ingested more than once. Sometimes that's a true byte-for-byte
resend (an at-least-once message delivery firing twice). Sometimes it's
a newer version of the same record arriving as a brand new row instead
of an UPDATE - a status change, a corrected amount - which looks, to a
naive dedup check, like two completely unrelated rows. Today's problem:
proving the difference between those two cases, and showing the fix
that actually handles both.

## The data

orders_dupes has 800 rows but only 500 distinct order_ids:

    500 base orders, all status='pending', timestamp 2026-10-01
    150 exact resends of order_id 1-150 (identical rows, same timestamp)
    150 updated duplicates of order_id 151-300 (status changed to
        'completed', amount adjusted, newer timestamp 2026-10-02)

## Proof 1 - duplicates confirmed

    SELECT COUNT(*), COUNT(DISTINCT order_id) FROM orders_dupes;

    total_rows | distinct_orders
    -----------+----------------
           800 |             500

300 duplicate rows exist against the true 500 unique orders.

## Proof 2 - naive DISTINCT only catches exact resends

    SELECT COUNT(*) FROM (SELECT DISTINCT * FROM orders_dupes) t;

    count
    -------
      650

DISTINCT correctly collapsed the 150 exact resends (800 -> 650), but
left all 150 stale-vs-updated pairs completely untouched. To DISTINCT,
a 'pending'/$241.91/Oct-1 row and a 'completed'/$246.91/Oct-2 row for
the same order_id look like two entirely separate, legitimate rows,
because every column actually does differ. This is the real-world
failure mode: DISTINCT silently fails to deduplicate exactly the kind of
duplicate that matters most.

## Proof 3 - ROW_NUMBER() partitioned by the business key is the real fix

    SELECT COUNT(*)
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
        FROM orders_dupes
    ) t
    WHERE rn = 1;

    count
    -------
      500

Partitioning by order_id and ordering by updated_at DESC numbers every
row within each order's group by recency. Filtering to rn = 1 keeps
exactly one row per order_id - the most recent one - landing exactly on
the true count of 500.

## Proof 4 - confirming the kept row is the correct one, not an arbitrary pick

    SELECT order_id, status, amount, updated_at,
           ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
    FROM orders_dupes
    WHERE order_id = 200
    ORDER BY rn;

    order_id | status    | amount | updated_at          | rn
    ---------+-----------+--------+---------------------+----
          200 | completed | 246.91 | 2026-10-02 14:30:00 |  1
          200 | pending   | 241.91 | 2026-10-01 09:00:00 |  2

rn = 1 kept the newer, correct 'completed' row at the updated amount,
and correctly discarded the stale 'pending' row - not an arbitrary
choice between two identical rows, but a deliberate pick of the most
authoritative version of that order.

## Why this matters

DISTINCT deduplicates rows; it does not deduplicate entities. The
moment a duplicate record is a genuinely different row - a later
update, a corrected value - DISTINCT cannot tell that it belongs to the
same real-world thing as an earlier row. PARTITION BY on the true
business key, ordered by a recency column, is what actually expresses
"keep one row per entity, specifically the latest one" - connecting
directly to the idempotent upsert work from Day 47: this is the same
problem, solved at query time instead of load time.
