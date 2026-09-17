# Day 13 — Analytical Queries with DuckDB

Moves from row-oriented, transactional engines (MySQL in Day 7, Cassandra
in Day 11) to DuckDB — an embedded, columnar OLAP engine built specifically
for exactly this kind of query: aggregations and window functions over a
whole dataset, with no server process to run.

## Data

`generate_data.py` produces a reproducible (fixed random seed) synthetic
dataset: ~200 orders across 5 customers spread over 90 days (Jan 1 – Mar 31,
2026), with enough day-to-day variation for a rolling revenue trend and
month-over-month growth to actually be visible rather than flat.

## Queries (`analytical_queries.py`)

1. **Rolling 7-day revenue** — a window function (`ROWS BETWEEN 6
   PRECEDING AND CURRENT ROW`) over daily revenue totals, smoothing out
   single noisy days.
2. **Top 5 customers by total revenue** — straightforward aggregation,
   used here mainly as a cross-check (see below).
3. **Month-over-month revenue growth** — monthly totals compared via
   `LAG()`, as a percentage change from the previous month.

## Cross-check

The top-5-customers total ($26,031.27) and the sum of the three monthly
totals ($9,927.91 + $7,666.60 + $8,436.76 = $26,031.27) match exactly —
the same underlying rows, aggregated two different ways, confirming
neither query is silently dropping or double-counting orders.

## A real gotcha: raw MoM growth vs. days-in-month

March showed +10.0% revenue growth over February. But January has 31
days, February has 28, and March has 31 again — daily revenue was
actually ~$320/day in January and only ~$273-274/day in *both* February
and March. The "+10% growth" is almost entirely explained by March
simply having 3 more days than February, not by any real increase in
order volume. A fairer month-over-month comparison would normalize to
revenue-per-day rather than comparing raw monthly totals directly —
otherwise a shorter month can look like a decline, and the month right
after it can look like a recovery, when the underlying daily rate barely
moved.
