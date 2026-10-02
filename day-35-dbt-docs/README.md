# Day 35 — dbt Documentation & Auto-Generated Data Lineage

## Goal
Every proof in this project so far has lived in terminal output - PASS/FAIL counts, row counts,
log lines. This exercise generates dbt's built-in documentation website: an interactive DAG
showing exactly how data flows through the whole project, plus column-level descriptions, tests,
and compiled SQL for every model - all generated automatically from the schema.yml files and model
code already written across every previous day.

## What was filled in
Descriptions were missing or incomplete on several models from earlier days (stg_events, the marts
columns, the raw_shipments source). These were filled in before generating anything, since the docs
site is only as useful as the descriptions behind it.

## A real gotcha, caught and fixed
After the first `dbt docs generate` / `dbt docs serve`, the lineage graph showed raw_shipments and
raw.raw_shipments as two disconnected nodes. This is a genuine dbt behavior worth knowing: declaring
a source in sources.yml does NOT automatically wire it into the DAG - the connection is only drawn
once a model actually queries it with source(). The Day 33 source freshness check existed, but
nothing downstream ever referenced it. Fixed by adding a real staging model, stg_shipments.sql,
that selects from source('raw', 'raw_shipments') - after rebuilding and regenerating, the lineage
graph correctly showed raw.raw_shipments -> stg_shipments connected like every other node.

## Proof
- Full lineage graph: every source/seed flowing through staging into the mart and the snapshot, with
  the real dependency edges, generated automatically - no diagram drawn by hand.
- Opened the mart_customer_revenue documentation page directly and confirmed the model description,
  both column descriptions, all 4 data tests (including the custom non_negative test from Day 34),
  the Depends On lineage back to stg_orders, and the actual compiled SQL all render correctly from
  the project's own schema.yml and model files.

## Key takeaway
dbt's documentation site isn't a separate thing to maintain - it's generated directly from the same
schema.yml descriptions and ref()/source() calls already written for testing and lineage purposes.
The only real gotcha is that a source declaration by itself is inert until something downstream
actually calls source() on it - the DAG reflects what's actually queried, not what's merely declared.
