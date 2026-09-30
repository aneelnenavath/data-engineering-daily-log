# Day 30 — dbt Incremental Models

## Objective
Days 26-29 built and tested a dbt project using `table` and `view`
materializations, where every run fully rebuilds the model from scratch. That
doesn't scale once a source table has millions of historical rows and only a
small daily batch is genuinely new. Day 30 covers dbt's `incremental`
materialization, and proves - with real before/after evidence, not just
reading the docs - the specific tradeoff every incremental model makes: it's
fast because it deliberately skips reprocessing rows it has already loaded,
which means a correction to old data silently won't show up until you
explicitly force a full rebuild.

## The model
A new model, `stg_events`, built on a fresh `raw_events` seed (an events
table with an `event_id`, `customer_id`, `event_type`, `amount`, and
`loaded_at`):

```sql
{{
  config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='append'
  )
}}

select
    event_id,
    customer_id,
    event_type,
    amount,
    loaded_at
from {{ ref('raw_events') }}

{% if is_incremental() %}
where event_id > (select coalesce(max(event_id), 0) from {{ this }})
{% endif %}
```

`is_incremental()` is false on the very first run (the table doesn't exist
yet), so every row loads. On every run after that, it's true, and the model
only selects rows past whatever `event_id` is already the highest value in
the table - a simple high-water-mark pattern.

## Proof: three builds, two claims tested independently

**Run 1 (initial load).** 10 seed rows, `dbt build`. Verified with `dbt show
--inline` (not `dbt show --select`, which expects a model name and not raw
SQL - `--select` with a full SQL string silently fails with "selection
criterion does not match" warnings): `row_count = 10`, event 5 shows its
original amount, `60.00`.

**Run 2 (incremental, with a planted correction).** The seed was updated two
ways at once: 5 new rows appended (`event_id` 11-15) and event 5's amount
"corrected" from `60.00` to `999.00`, simulating a real-world late correction
to already-ingested data. A normal `dbt build` (no `--full-refresh`) was run.
Result: `row_count = 15` - the new rows were picked up - but event 5 **still
showed `60.00`**, not `999.00`. This is the actual point of the exercise: the
incremental filter correctly ignored event 5 because its `event_id` (5) is
below the existing high-water mark (10), so it was never re-selected. If
event 5 had shown `999.00` here, that would mean the incremental filter was
broken, not working correctly.

**Run 3 (`--full-refresh`).** Same seed, `dbt build --full-refresh`. Result:
`row_count` still 15, but event 5 now shows `999.00`. `--full-refresh` drops
the table and rebuilds it entirely from the current seed content, so the
correction finally lands.

| run | command | row_count | event 5 amount |
|---|---|---|---|
| 1 | `dbt build` (first run) | 10 | 60.00 (original) |
| 2 | `dbt build` (incremental) | 15 | 60.00 (correction ignored) |
| 3 | `dbt build --full-refresh` | 15 | 999.00 (correction picked up) |

## Key takeaway
An incremental model skipping already-loaded rows isn't a bug to work around
- it's the entire mechanism that makes incremental models fast, and it's
exactly why `--full-refresh` exists as an explicit, deliberate escape hatch
for whenever historical data actually needs to be reprocessed (a schema
change, a backfill, a correction like this one). Understanding this tradeoff
- and being able to demonstrate it with real before/after row-level evidence
rather than just reciting the concept - is one of the most commonly asked
dbt interview questions, and this exercise is designed to be exactly that
demonstration.
