# Day 24 — Airflow Dynamic Task Mapping

## Objective
Use Airflow's dynamic task mapping (`.expand()`) to process a runtime-
determined list of files with one task instance per file, and prove the
mapping is genuinely dynamic - not just "three tasks that happen to run" -
by changing the input list and confirming the task count changes with it.

## DAG design
`day24_dynamic_mapping`, built with the TaskFlow API rather than classic
operators, since dynamic mapping is what TaskFlow is designed for:
- `generate_regional_files` writes one CSV per region from a `REGIONS`
  dict and returns the list of file paths.
- `process_file` is expanded over that list with
  `process_file.expand(file_path=file_paths)`, so Airflow creates one
  mapped task instance per file at run time, each computing that region's
  total and writing a per-region summary.
- `aggregate_totals` collects every mapped instance's result and sums them
  into a grand total.

## A different Airflow gotcha than the mount bug
Unlike Days 22 and 23, the DAG file parsed cleanly with no import errors
and correctly appeared in `airflow dags list`, but `airflow dags trigger`
kept failing with `DagNotFound ... not found in DagModel`. The cause: a
new DAG file is picked up by the DAG *processor's* file parse fairly
quickly, but syncing into the scheduler's metadata database depends on the
directory rescan interval - `scheduler.dag_dir_list_interval`, confirmed at
300 seconds (5 minutes) by default. The file had landed a couple of minutes
after the container's initial scan, so it wasn't going to be picked up
again for several more minutes. Restarting the container triggered a fresh
initial scan of everything already in the folder, which is what actually
resolved it - not a code fix, but recognizing which internal clock was
actually blocking progress.

## Proving the mapping is genuinely dynamic
A first run with three regions (north, south, east) produced exactly three
`process_file` task instances, at map indexes 0, 1, and 2, with totals of
100.0, 40.0, and 40.0 and a grand total of 180.0 - all matching hand
calculations. A fourth region (west, total 10.0) was then added to the
`REGIONS` dict with no other change to the DAG's logic, and the second run
produced four `process_file` instances (map indexes 0-3) and a grand total
of 190.0. The task count changed because the input list changed, not
because the DAG's code did - which is the actual claim dynamic task
mapping makes.

## Verification
The final grand total, 190.0, was recomputed independently by summing every
region CSV directly with a standalone Python script outside the DAG
entirely, confirming an exact match.

## Key takeaway
Dynamic task mapping's real value is that the DAG's shape adapts to data
discovered at run time rather than being fixed at write time - proving that
claim requires actually changing the input and watching the task count
change with it, not just running the DAG once and counting three tasks
that were going to be three regardless. Separately, an Airflow scheduling
interval (the DAG directory rescan) turned out to be the blocker here
rather than a code or environment bug - a reminder that "no error" and
"not yet processed" can look identical from the outside.
