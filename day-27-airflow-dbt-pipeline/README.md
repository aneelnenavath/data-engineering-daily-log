# Day 27 — Orchestrating dbt from Airflow

## Objective
Days 19-25 built up Kafka and Airflow separately, then combined them on Day 25 by
having Airflow's `BashOperator` orchestrate an external Kafka script the way real
pipelines trigger a Spark job or a dbt run. Day 26 built a small dbt project on
DuckDB with staging/mart models and schema tests, proven against deliberately
planted bad data. Day 27 connects the two: Airflow orchestrates the actual `dbt
build` command from Day 26, and — the real point of the day — a failing dbt test
is proven to fail the *Airflow task itself*, not just the standalone dbt CLI run.

## Setup
The Day 26 dbt project was copied into `dags/dbt_project/` in this folder, so it
gets mounted straight into the Airflow container alongside the DAG file (no
separate volume mount needed). The local `~/.dbt/profiles.yml` was copied
alongside the project as `profiles.yml` so `dbt build --profiles-dir .` can find
its target from inside the container without needing `~/.dbt` set up there too.

The Airflow container was recreated attached to the `daylog-net` custom network
(left over from Day 25, harmless here since this DAG never touches Kafka) with
four mounts: `dags/`, `logs/`, `plugins/`, `data/`. `dbt-duckdb` was installed
into the container's Python environment with `python -m pip install dbt-duckdb`
(the same fix as Day 25 — a bare `pip install --user` fails in this venv-based
image).

## The DAG
A single-task DAG, deliberately kept simple so the orchestration boundary is
obvious:

```python
dbt_build = BashOperator(
    task_id="dbt_build",
    bash_command="cd /opt/airflow/dags/dbt_project && dbt build --profiles-dir .",
)
```

## Bug hit again: MSYS path mangling
The exact same bug family from Day 22 showed up again, this time on a bare
`docker exec`:

Git Bash's MSYS layer rewrote the leading `/opt/...` argument into a Windows
path before Docker ever saw it. Same fix as before: prefix the command with
`MSYS_NO_PATHCONV=1`. This is now the third distinct place this exact bug class
has appeared (a `docker exec` command argument on Day 22, a `docker run -v`
mount's container-side path also on Day 22, and now another bare `docker exec`
here) — worth remembering as a standing rule for this Windows/Git-Bash setup
rather than a one-off.

## Proof 1: clean data, verified beyond Airflow's green state
Triggering the DAG against the unmodified (clean) seed data reported success in
Airflow, but a green task state alone was never trusted anywhere else in this
project, so the actual task log was read directly from the mounted `logs/`
folder on the host:

Confirms all 10 checks from Day 26 (the seed, both models, and every schema
test) genuinely ran through the Airflow-orchestrated path, not just the dbt CLI
in isolation.

## Proof 2: a planted bad row fails the Airflow task itself
One row was appended to the seed with an invalid `status`:

Re-triggering the DAG produced a run with `state = failed` in
`airflow dags list-runs`. The task log confirmed the exact cause:

This is the actual point of the exercise: the `accepted_values` test failing
caused `dbt build` to exit non-zero, and Airflow's own task-instance logic
picked that up and marked the task (and the DAG run) failed — a genuine
pipeline-level gate, not a warning that gets silently ignored downstream.

## Cleanup and final verification
The bad row was removed and the DAG re-triggered a third time, returning to
`state = success`. The full run history for the day:

| run | state |
|---|---|
| 1 (clean seed) | success |
| 2 (planted bad row) | failed |
| 3 (bad row removed) | success |

## Key takeaway
A schema test only means something in production if its failure actually stops
the pipeline from proceeding on bad data — not just that the test exists in a
`schema.yml` file. Day 26 proved the tests catch bad data when run directly;
Day 27 proved that failure propagates all the way up through the orchestration
layer and stops the pipeline. Same discipline that's run through this whole
project — plant the failure, watch the safeguard actually trigger, only then
trust it — now demonstrated one layer higher than before.
