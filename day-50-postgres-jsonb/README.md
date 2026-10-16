# Day 50 — Postgres JSONB

## Topic

Fifty days in. Every table built across this project so far has had a fixed, fully relational
schema. Today looks at a genuinely common real-world pattern: a table that mixes strict
relational columns with a JSONB column holding variable, semi-structured data - an event
payload, a settings blob, order metadata that doesn't cleanly fit a fixed set of columns.

## Setup

Built `orders_meta` (500,000 rows) with a `jsonb` column called `metadata`, holding a payment
method, a nested shipping object (country, express), a vip boolean, and a tags array - all
varying per row the way real semi-structured data does. Full setup is in `setup_jsonb.sql`,
full proof trail is in `queries.sql`.

## Operator basics

`->` returns a JSONB value, `->>` returns the same thing as plain text, and they chain to reach
into nested objects: `metadata -> 'shipping' ->> 'country'` reached straight into the nested
shipping object and returned `IN` as text, without needing a join or a separate table.

## Proof 1 — no index means a full scan, same as any other column

Filtering for `payment_method = paypal` (about 25% of rows match) with no index at all:

    Parallel Seq Scan across all 500,000 rows. Execution Time: 142.532 ms

## Proof 2 — a GIN index helps, but more modestly than expected

Added a GIN index - the index type built specifically for indexing inside composite values
like jsonb - and reran the identical query:

    Bitmap Heap Scan using idx_orders_meta_gin. Execution Time: 108.546 ms

Only about a 24% improvement. At 25% selectivity, a Bitmap Heap Scan still has to visit a
large fraction of the table's actual heap blocks no matter how it located the candidate rows,
so the win here was real but small - a genuinely useful result to report honestly rather than
only showcase the dramatic cases.

## Proof 3 — a more selective query, and why GIN indexes behave differently from B-tree

Combined two JSONB conditions (`vip = true AND payment_method = paypal`), matching only about
1.26% of the table (6,295 of 500,000 rows):

    WITH the GIN index:     Bitmap Index Scan. Execution Time: 62.559 ms
    FORCED to Seq Scan
    (same selective query): Parallel Seq Scan. Execution Time: 90.366 ms

That's roughly a 1.44x speedup - real, but nowhere near the 10-60x+ speedups B-tree indexes
gave on plain scalar columns across Days 45-48. The plan explains why: it showed "Rows Removed
by Index Recheck: 23679" and "Heap Blocks: exact=10196." A GIN index on jsonb returns a lossy
bitmap of candidate rows, which Postgres must then recheck against the actual table data to
confirm a real match - unlike a B-tree index on a plain scalar column, which can usually
confirm a match directly from the index itself.

## What to remember going forward

JSONB is genuinely useful for data that doesn't fit a fixed schema, and a GIN index does make
querying into it faster - but the two most important things about it are different from
everything learned about indexing scalar columns so far: a GIN index's speedup is often modest
even at real selectivity, because of the recheck step baked into how it works, and the honest,
measured answer here mattered more than a cherry-picked dramatic one. For data with a fixed,
known structure, a plain relational column with a plain B-tree index will almost always
outperform storing the same thing inside jsonb - JSONB earns its place specifically for the
data that is genuinely variable, not as a general substitute for proper schema design.
