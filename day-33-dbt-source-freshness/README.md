# Day 33 — dbt Source Freshness Checks

## Goal
Every test written so far in this project checks whether data is *correct* - not null, unique,
within an accepted set of values. This exercise checks something different: whether data is
*current*. dbt's source freshness feature compares a loaded_at timestamp against configurable
thresholds and flags a source as stale if it hasn't been updated recently enough - a very common
real-world question: how do you catch an upstream feed that's quietly stopped updating, before
downstream reports go stale without anyone noticing?

## Setup
A new seed, raw_shipments.csv, defined as a dbt source (not referenced with ref(), the normal way
to query it in production) with:
- loaded_at_field: loaded_at
- warn_after: 1 day
- error_after: 3 days

## Proof: all three states, deliberately triggered

| Data age           | Expected state | Actual result              |
|---------------------|-----------------|-----------------------------|
| Same day (hours old) | PASS            | PASS in 0.03s                |
| ~2 days old          | WARN            | WARN in 0.02s                |
| ~11 days old         | ERROR           | ERROR STALE in 0.02s, non-zero exit |

Each state was triggered by editing the seed's loaded_at timestamps directly, running
`dbt seed --full-refresh` to reload it, then running `dbt source freshness` and reading the real
result - not just describing the thresholds. The data was then restored to a fresh timestamp
before committing, so the repo is left in a passing state.

## Key takeaway
dbt source freshness turns "is our data still arriving" from a question someone eventually notices
and asks into something that can be checked automatically, the same way the schema tests earlier in
this project turned "is our data still correct" into an automatic check. Both error_after and
warn_after returning a genuine non-zero exit code on failure means this plugs into the same CI and
Airflow failure-handling built on earlier days without any extra wiring.
