# Day 40 — dbt Snapshots (Slowly Changing Dimension Type 2)

## What this is

A deep dive into `customers_snapshot`, a snapshot that already existed in this project
from earlier setup but had never been explained, tested, or actually proven to work.
A dbt snapshot tracks how a row changes over time: instead of overwriting a row in
place, it end-dates the old version and inserts a new one, so the full history is
always queryable.

```sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema='main',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
    )
}}

select * from {{ ref('raw_customers') }}

{% endsnapshot %}
```

This uses the `timestamp` strategy: dbt only considers a row "changed" by comparing the
`updated_at` column between runs, rather than comparing every column's actual value.

## Proof 1 — the timestamp strategy genuinely ignores a change if updated_at doesn't move

Changed customer 1's `tier` from `silver` to `gold` in the seed, but left `updated_at`
untouched, then reran `dbt seed` + `dbt snapshot`. Querying `customers_snapshot`
afterwards showed the row completely unchanged: still one row, still `tier = silver`,
`dbt_valid_to` still empty - the snapshot had no way of knowing anything had changed,
because the only thing it checks is `updated_at`.

## Proof 2 — bumping updated_at triggers real SCD Type 2 history

Bumped `updated_at` to a later timestamp alongside the tier change, reran `dbt seed` +
`dbt snapshot`, and queried again. This time two rows appeared for customer 1:

| customer_id | name          | tier   | dbt_valid_from       | dbt_valid_to         |
|-------------|---------------|--------|-----------------------|-----------------------|
| 1           | Alice Johnson | silver | 2026-09-01 09:00:00  | 2026-10-06 12:00:00  |
| 1           | Alice Johnson | gold   | 2026-10-06 12:00:00  | (empty - current)    |

The old `silver` row was not deleted or overwritten - it was end-dated at exactly the
moment the new version became current. The new `gold` row is the current version,
identifiable by its empty `dbt_valid_to`. This is genuinely how dimensional history is
tracked in a real warehouse.

## Final state

This change was kept rather than reverted, since it's real, meaningful history and not
an artificial broken state - that's the entire point of a snapshot. Added a
`snapshots/schema.yml` with tests on the snapshot's own metadata columns
(`dbt_scd_id` unique/not-null, `customer_id` not-null, `dbt_valid_from` not-null). Full
`dbt build` passed cleanly: 46/46 (2 incremental models, 4 seeds, 1 snapshot, 3 table
models, 33 data tests, 1 unit test, 2 view models).

## Key takeaway

The `timestamp` strategy is not "detect any change to this row" - it is specifically
"detect a change to this one column." A source system that updates a value without also
bumping its own `updated_at`/`modified_at` field will silently produce stale history, and
this is exactly the kind of gap that's easy to miss until you deliberately test it rather
than just trust the mechanism to behave the way its name suggests.
