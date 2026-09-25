# Day 23 — Airflow Sensors and Conditional Branching

## Objective
Introduce two Airflow concepts not covered on Day 22: a sensor that waits
for an upstream file to actually arrive, and conditional branching that
routes execution differently depending on a data-quality check - proving
both behaviors with concrete evidence rather than assuming the DAG's shape
matches its intent.

## DAG design
`day23_conditional_pipeline` has five tasks:
- `wait_for_file` (FileSensor) polls every 5 seconds for
  `data/incoming/orders.csv` to exist, timing out after 120 seconds.
- `check_quality` (BranchPythonOperator) reads the CSV once it arrives and
  checks every row's `amount` for a null or negative value - reused logic
  from Day 12's data quality checker - then routes to one of two branches.
- `process_good_data` runs only when no bad rows are found, computing and
  writing the total revenue.
- `quarantine_bad_data` runs only when bad rows are found, recording the
  offending order IDs via XCom from `check_quality`.
- `finish` joins both branches back together using the
  `none_failed_min_one_success` trigger rule, so it still runs correctly
  even though exactly one of the two branches above it is always skipped.

## Proving the sensor actually waits
The DAG was triggered with `data/incoming/orders.csv` deliberately absent.
15 seconds later - long enough for several 5-second poke cycles - the run
was still shown as `running`, not `success`, with the incoming folder still
empty. Only after the file was created did the sensor's next poke find it
and the run proceed to completion, confirmed by the sensor's own recorded
start (15:23:12) and end (15:24:07) times spanning roughly 55 seconds of
genuine polling.

## Proving the branch is genuinely conditional, both ways
Two runs were triggered. The first used a CSV with one negative-amount row:
`process_good_data` came back `skipped` and `quarantine_bad_data` came back
`success`, correctly recording `bad_order_ids=['3']`. The second run used
clean data with no bad rows, and the result flipped exactly as expected:
`process_good_data` succeeded with `total_revenue=117.5`, while
`quarantine_bad_data` was the one skipped this time. Airflow's `skipped`
state, not just a task's absence, is the direct evidence that the branch
decision was actually being evaluated per run rather than one path being
unreachable.

## Verification
The good-data run's computed total, 117.5, was cross-checked independently
against `25.50 + 40.00 + 18.25 + 33.75` calculated outside the DAG entirely,
confirming an exact match.

## Key takeaway
A DAG that "runs successfully" says nothing on its own about whether a
sensor actually waited or a branch actually branched - both are easy to get
silently wrong (a sensor that succeeds instantly because its path doesn't
point where intended, or a branch that always takes the same route because
of a logic bug) while still reporting a clean run. Checking task-level
states - `skipped` versus `success`, and real elapsed time on a sensor -
is what turns an assumption into a verified behavior.
