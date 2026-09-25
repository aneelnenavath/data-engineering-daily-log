# Day 22 — Airflow DAG Orchestration

## Objective
Build an Airflow DAG with dependent tasks (extract -> transform -> load) and
prove, not just configure, that Airflow's automatic retry mechanism actually
recovers a task from a genuine failure.

## Setup
Ran Airflow 2.9.3 via Docker in `standalone` mode (a single container running
its own lightweight SQLite-backed scheduler + webserver), with the `dags`,
`logs`, `plugins`, and `data` folders bind-mounted from the host so the DAG
file and its output could be inspected directly.

## A subtler variant of the MSYS path bug
Two separate MSYS path-mangling issues showed up today, from the same root
cause as Days 9, 19, and 21 but in a new shape. The first was familiar:
`docker exec ... ls /opt/airflow/dags` got its absolute Linux path rewritten
into a bogus Windows path by Git Bash. The second was more subtle and much
easier to miss: the *volume mount itself*, in the original `docker run -v
"$(pwd)/dags:/opt/airflow/dags"` command, had its container-side path
mangled the same way. Docker didn't error - it silently fell back to the
image's own empty built-in `/opt/airflow/dags` directory, so the container
started successfully and looked healthy, but the DAG file written to the
host folder was invisible to Airflow. The fix in both cases was the same
`MSYS_NO_PATHCONV=1` prefix, but the volume-mount version is the more
dangerous of the two: it fails silently with a healthy-looking container,
rather than throwing an obvious error.

## DAG design
`day22_etl_pipeline` has three PythonOperator tasks: `extract` writes 20
synthetic orders to CSV, `transform` computes total revenue, and `load`
reads the final result. `transform` was deliberately written to raise a
`RuntimeError` on its first attempt (using a flag file to detect "have I
already tried once") and only succeed on the second, with `retries=1` and a
10-second `retry_delay` configured on the DAG's default args.

## Verification
Triggering the DAG showed an overall `success` state, which on its own would
have been too easy to take on faith. Airflow keeps a separate log file per
task attempt, so `attempt=1.log` and `attempt=2.log` for the `transform` task
were checked directly: attempt 1 shows the deliberate `RuntimeError`, attempt
2 shows `Transform succeeded on retry. Total revenue: 410.0` - concrete proof
the retry mechanism fired rather than the task simply succeeding first try.
That total was then cross-checked independently with `awk` directly against
the raw CSV, completely outside Python and Airflow, confirming 410 exactly.

## Key takeaway
A container reporting healthy and a DAG reporting `success` are both
necessary but not sufficient evidence on their own. The volume-mount bug in
particular would have been easy to miss without checking that the DAG file
was actually visible inside the container - a claimed success wrapped around
a mount that silently pointed at nothing.
