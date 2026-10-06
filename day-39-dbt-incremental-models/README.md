# Day 39 — dbt Incremental Models

## What this is

A new model, `fct_orders_incremental`, built on top of `stg_orders` and materialized as
`incremental` rather than the default `view`/`table`. Instead of rebuilding the whole
table on every run, it only loads orders that are new since the last run, using
`order_id` as the incremental cursor (the source data has no timestamp column, so the
ever-increasing integer id is used instead — a common real-world situation).

```sql
{{ config(materialized='incremental', unique_key='order_id') }}

select order_id, customer_id, amount, status
from {{ ref('stg_orders') }}

{% if is_incremental() %}
where order_id > (select max(order_id) from {{ this }})
{% endif %}
```

## Proof 1 — first run loads everything, later runs only load what's new

- First `dbt build` (table doesn't exist yet): loaded all 16 seed rows, `max(order_id) = 17`.
- Added two new orders (`order_id` 18 and 19) to the seed, reran `dbt seed` + `dbt build`
  with no `--full-refresh`: row count went to exactly 18, `max(order_id)` became 19 —
  only the two new rows were added, not a full rebuild.

## Proof 2 — the real limitation: an id-based incremental filter misses edits to old rows

This is the part that actually proves it's incremental rather than just correct:

1. Changed order 1's status in the seed from `completed` to `cancelled`, reran `dbt seed`
   and `dbt run --select fct_orders_incremental` (still no full refresh).
2. Queried `fct_orders_incremental` for `order_id = 1` — it still showed `completed`.
   The row's id (1) was nowhere near the current max (19), so the incremental filter
   never looked at it again, even though the underlying source data had changed.
3. Ran `dbt run --select fct_orders_incremental --full-refresh` — this time order 1
   correctly showed `cancelled`, because a full refresh ignores the incremental logic
   and rebuilds the whole table from scratch.

This is a genuine, well-known limitation of a simple append-by-id incremental strategy:
it only ever picks up brand-new rows, never edits to rows it has already loaded. Catching
updates to historical rows would need a different approach (e.g. a `merge` strategy keyed
on `unique_key` combined with a `modified_at`-style column), which is a natural next step
beyond today's scope.

## Final state

Order 1 was restored back to `completed` (undoing the test edit), the two new orders
(18, 19) were kept as a permanent record of the dataset having legitimately grown, and a
final `dbt build --full-refresh` across the whole project passed cleanly: 42/42
(2 incremental models, 4 seeds, 1 snapshot, 3 table models, 29 data tests, 1 unit test,
2 view models).

## Key takeaway

A clean, error-free incremental run proves nothing about whether the incremental logic
is actually correct — both a true incremental run and an accidental full rebuild can
produce the same row count. The real proof came from deliberately editing a row that
should be *outside* the incremental window and showing the model genuinely ignored it,
then showing `--full-refresh` is the correct remedy when historical data needs to be
reprocessed.
