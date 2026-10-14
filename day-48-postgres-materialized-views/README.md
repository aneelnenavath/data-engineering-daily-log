# Day 48 — Postgres Materialized Views

## Topic

Continuing the Postgres performance arc from Days 45-47 (indexing, partitioning, upserts),
today looks at pre-computing an expensive query's result and storing it as its own object -
a materialized view - instead of storing just the query itself, which is all a plain view is.
The win is real, but so is the limitation: a materialized view goes stale the moment the
underlying data changes, and nothing updates it automatically.

## Setup

Reused the 500,000-row `perf_orders` table from Days 45-46. Built two objects with an
identical definition - total orders and total revenue grouped by customer_id, across 49,999
distinct customers - one as a plain `VIEW`, one as a `MATERIALIZED VIEW` with a unique index
on customer_id. Full setup is in `setup_materialized_view.sql`, full proof trail is in
`queries.sql`.

## Proof 1 — a plain view is not inherently slow, but a materialized view is still faster where it matters

Filtering the plain view down to one customer was actually fast (1.312 ms), because Postgres
pushed the WHERE clause down through the view definition and used an existing index before
aggregating. But a query with nothing to push down - finding the top 10 customers by revenue -
has to aggregate all 500,000 rows into all 49,999 groups every time it runs:

    Plain view (top 10 by revenue):          GroupAggregate over the full table.
                                              Execution Time: 655.421 ms

    Materialized view (same query):          Seq Scan over the already-computed 49,999
                                              rows - no aggregation at query time at all.
                                              Execution Time: 10.524 ms

That's roughly a 62x speedup, because all the expensive aggregation work happened once, at
creation time, rather than on every single query.

## Proof 2 — the limitation: materialized views go silently stale

Checked customer 1 in both views as a baseline: 2 orders, $243.06, matching exactly. Then
inserted a brand new $5,000 order for that customer directly into `perf_orders`, simulating
new data arriving - and rechecked both views:

    Plain view:          3 orders, $5243.06 - picked up the new order instantly, because
                          it recomputes live on every query.

    Materialized view:   still 2 orders, $243.06 - completely unaware the new row exists,
                          even though it is sitting right there in the underlying table.

Nothing about this is a bug or an error - it's the defining tradeoff of a materialized view.
It traded live accuracy for query speed, and that trade has to be managed deliberately.

## Proof 3 — fixing staleness, and refreshing without blocking readers

Running `REFRESH MATERIALIZED VIEW customer_revenue_summary_mat;` brought it back in sync
immediately - rechecking customer 1 showed 3 orders, $5243.06, matching the live data again.
A plain REFRESH takes an exclusive lock and blocks all reads against the view while it
rebuilds, which matters for a materialized view queried frequently. `REFRESH MATERIALIZED
VIEW CONCURRENTLY` avoids that lock, but it requires a unique index on the materialized view
to work at all - the exact reason a unique index on customer_id was created during setup.
Ran successfully once that index was in place.

## What to remember going forward

A materialized view earns its keep when a query is expensive and the data doesn't need to be
perfectly live - dashboards, daily reports, anything where a few minutes or hours of staleness
is an acceptable tradeoff for a 60x+ speedup. It is not a drop-in replacement for a plain view
in every case: a plain view with a well-chosen filter can already be fast through predicate
pushdown, and a materialized view needs an explicit refresh strategy (a scheduled job, a
pipeline hook, CONCURRENTLY to avoid locking out readers) or it will confidently return wrong,
stale numbers with no warning that anything is out of date.
