# Day 31 — dbt Snapshots for Slowly Changing Dimensions (SCD Type 2)

## Objective
Day 30 covered dbt's incremental materialization, which is built to
*deliberately ignore* rows it has already loaded on later runs - the right
tool when a source is append-only and old data never changes. Day 31 covers
the opposite problem: a source table (a customer dimension, in this case)
whose rows genuinely mutate over time, where every past state actually needs
to stay queryable. dbt's built-in `snapshot` feature implements classic Type 2
Slowly Changing Dimensions for exactly this - instead of overwriting a
changed row, it closes out the old version and opens a new one, so the full
history of every change is preserved.

## The snapshot
A `raw_customers` seed (5 customers with a `tier` and an `updated_at`
timestamp) feeds a snapshot definition:

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

The `timestamp` strategy compares each row's `updated_at` against whatever
dbt already has snapshotted for that `unique_key`. If it's newer, dbt closes
the old version (sets `dbt_valid_to`) and inserts a new open version
(`dbt_valid_to` left empty) - all handled automatically by `dbt snapshot`,
no manual SCD2 merge logic required.

## Proof: a real change, checked at the row level

**Snapshot 1 (baseline).** `dbt snapshot` run against the initial 5-row seed.
Confirmed all 5 customers present with `dbt_valid_to` empty - every row is
currently the "open" / current version, since none of them has changed yet.

**A real business event.** The seed was updated so customer 2 (Ben Carter)
moves from `silver` to `gold`, with `updated_at` two weeks later than his
original row. Every other customer's row was left completely unchanged.
`dbt seed` followed by a second `dbt snapshot` run.

**Result, queried directly from the snapshot table:** customer 2 now has
**two rows** - the original `silver` version with `dbt_valid_to` populated
(`2026-09-15 10:00:00`, the moment it was closed out), and a new `gold`
version with `dbt_valid_to` empty (the current one). Grouping the whole
table by `customer_id` and counting rows confirmed the scope of the change
was exactly right: customer 2 shows `version_count = 2`, and all four other
customers show `version_count = 1` - the snapshot opened a new version only
for the row that genuinely changed and left everyone else completely
untouched.

| customer_id | name | version_count |
|---|---|---|
| 1 | Alice Johnson | 1 |
| 2 | Ben Carter | **2** |
| 3 | Chidi Okafor | 1 |
| 4 | Diya Sharma | 1 |
| 5 | Ewan MacGregor | 1 |

## Key takeaway
Incremental models (Day 30) and snapshots (Day 31) look superficially similar
- both compare new data against what's already loaded - but they solve
opposite problems. An incremental model skips rows it's already seen because
old data is assumed not to matter again. A snapshot's entire purpose is the
reverse: assume a row *will* change, and never let a changed value silently
replace history. Choosing between them isn't a technical detail, it's a
modeling decision that depends entirely on whether the business genuinely
needs to answer "what was this customer's tier on any given date in the
past" - and having triggered a real change and watched the old version get
closed out rather than overwritten is real proof the mechanism works, not
just a description of what SCD Type 2 is supposed to do.
