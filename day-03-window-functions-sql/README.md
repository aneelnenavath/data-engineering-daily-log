# Day 3 — SQLite Window Functions

## What this is

15 rows of sample sales data (salesperson, region, date, amount), loaded from
sales.csv into a SQLite database, then explored using window functions —
SQL's tool for calculations that need to look across multiple rows at once,
without collapsing them into a single summary row the way GROUP BY does.

## Files

- sales.csv — raw input data
- queries.sql — the four window function queries, with comments
- sales.db — the SQLite database (generated locally, not committed to git)

## Queries and reasoning

RANK() PARTITION BY region — ranks each sale within its own region, highest
amount first. PARTITION BY is what makes this "per region" instead of one
global ranking across all 15 rows — without it, North's biggest sale and
South's biggest sale wouldn't both get to be rank 1.

SUM() OVER (ORDER BY sale_date) — a running total across all sales in date
order. One thing worth flagging: rows that share the exact same sale_date
get the same running total, because SQLite's default window frame treats
tied ORDER BY values as one peer group rather than crediting them one at a
time. Confirmed correct by checking the final row equals the plain sum of
the whole amount column.

LAG(amount) PARTITION BY salesperson — compares each sale to that same
person's previous sale. The first row per person is NULL, since there's
nothing before it. Also confirmed LAG follows the previous row in the
result set, not the previous calendar day — a person's gap days don't
change the logic.

LEAD(amount) PARTITION BY salesperson — same idea as LAG, mirrored to look
at the next row instead of the previous one. Last row per person is NULL.

## How to run

Open sqlite3 sales.db, then run:
.mode column
.headers on
.read queries.sql
