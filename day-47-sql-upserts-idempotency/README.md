# Day 47 — SQL Upserts and Idempotent Loads

## Topic

A pipeline that reruns itself - after a timeout, a retry, a crash partway through - is one
of the most common real failure modes in data engineering, and one of the most commonly asked
interview questions is simply: what happens if your job runs twice? Today builds and proves
both the naive answer (silent data duplication) and the correct one (`INSERT ... ON CONFLICT
DO UPDATE`, Postgres's upsert syntax).

## Setup

Built `orders_feed`, a 5,000-row staging table simulating a daily extract from an external
source, and `orders_current`, a target table a pipeline loads into - deliberately created
WITHOUT a primary key at first, since a missing uniqueness constraint is the real root cause
behind this entire class of bug. Full setup is in `setup_upsert_demo.sql`, the upsert script
itself is in `upsert_load.sql`, and the full proof trail is in `queries.sql`.

## Proof 1 — the naive reload silently duplicates data

Ran a plain `INSERT INTO orders_current SELECT * FROM orders_feed;` once - count(*) came back
as 5,000, exactly right. Then reran the identical statement, simulating a pipeline retry after
what looked like a transient failure:

    First run:   INSERT 0 5000   count(*) = 5000
    Second run:  INSERT 0 5000   count(*) = 10000

No error was raised either time. Checking a single row directly confirmed it: order_id 1 came
back as two byte-for-byte identical rows. Every downstream aggregate on this table - revenue,
order counts, anything - would now silently be exactly double, with nothing in the logs to
indicate anything had gone wrong.

## Proof 2 — the fix: a primary key plus ON CONFLICT DO UPDATE

Rebuilt `orders_current` with `order_id` as a real PRIMARY KEY, then replaced the naive load
with an upsert: insert each row normally, but on a conflicting order_id, update the existing
row's columns instead of inserting a duplicate. Ran it twice:

    First run:   INSERT 0 5000   count(*) = 5000
    Second run:  INSERT 0 5000   count(*) = 5000  (unchanged)

The row count stayed exactly the same across both runs - the rerun was fully safe. One nuance
worth noting: "INSERT 0 5000" on the second run does NOT mean 5,000 new rows were added. It's
the total number of rows the statement processed, including every row that hit the conflict
and became an update instead of an insert. The real idempotency proof is the unchanged row
count, not that message.

## Proof 3 — upserts track real changes, not just protect uniqueness

An important distinction from `ON CONFLICT DO NOTHING`, which would silently throw away a
genuine update: changed order 1's status and amount directly in the source feed
(`orders_feed`), then reran the exact same `upsert_load.sql` script with no code changes at
all. Result: order 1 in `orders_current` now shows the new status and the new amount - the
real change propagated correctly - still exactly one row, and the total count is still 5,000.
The upsert isn't just deduplicating identical reruns, it's genuinely keeping the target table
in sync with whatever the source currently says.

## What to remember going forward

A target table with no primary key will accept a naive reload as many times as you run it,
duplicating silently with no error raised at any point - this is a design mistake, not a bug
that announces itself. The fix is two things together: a real uniqueness constraint on the
natural key, and a load statement written to use it (`ON CONFLICT DO UPDATE`, not a plain
`INSERT`). Done right, a pipeline becomes safe to retry, safe to rerun by hand, and safe to
accidentally trigger twice - and it still correctly reflects whatever the source system's
current state actually is, rather than just refusing to duplicate stale data.
