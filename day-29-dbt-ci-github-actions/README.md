# Day 29 — CI for dbt with GitHub Actions

## Objective
Day 27 proved a failing dbt test correctly fails the orchestrating Airflow
task. Day 28 proved a failure gets a real alert. Day 29 moves the same test
suite one step earlier: instead of only catching bad data when a scheduled
pipeline runs, GitHub Actions now runs `dbt build` automatically on every push
that touches this project, catching bad data before it's even merged - the
same "shift-left" testing idea used in application CI, applied to a data
pipeline.

## Setup
The dbt project from Days 26-28 was copied unchanged into
`day-29-dbt-ci-github-actions/dbt_project/`. Unlike everything else in this
project so far, the workflow file itself does **not** live inside this day's
folder - GitHub Actions only discovers workflows in `.github/workflows/` at
the repo root, so `day29_dbt_ci.yml` lives there instead:

```yaml
on:
  push:
    paths:
      - 'day-29-dbt-ci-github-actions/**'
      - '.github/workflows/day29_dbt_ci.yml'

jobs:
  dbt-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install dbt-duckdb
      - working-directory: day-29-dbt-ci-github-actions/dbt_project
        run: dbt build --profiles-dir .
```

The `paths:` filter means this workflow only fires on changes to this day's
folder (or the workflow file itself), so it doesn't run on every unrelated
push to other days in the repo. No Docker, no local Airflow - this runs
entirely on a fresh GitHub-hosted Ubuntu VM per push.

## Proof: three pushes, three runs, checked in the Actions log every time
Rather than trust a green check mark on its own, every run's actual `dbt
build` log was opened and read, the same discipline used for every other
"it passed" claim in this project.

| push | seed data | Actions result | log evidence |
|---|---|---|---|
| 1 (`c24eb2c`) | clean | success | `Done. PASS=10 WARN=0 ERROR=0 SKIP=0` |
| 2 (`19df644`) | planted bad row (`unknown_status`) | **failed** | `accepted_values_stg_orders_status...FAIL 1`, `Done. PASS=5 WARN=0 ERROR=1 SKIP=4`, `Error: Process completed with exit code 1.` |
| 3 (`945249d`) | bad row removed | success | `Done. PASS=10 WARN=0 ERROR=0 SKIP=0` |

Push 2 is the actual point of the day: the same `accepted_values` violation
used on Days 27 and 28 to fail a local Airflow task instead failed a GitHub
Actions run - `dbt build` exited non-zero and GitHub correctly read that exit
code as a failed job, turning the whole run red. Notably, once the staging
test failed, the downstream mart model and its three tests were **skipped**
entirely (`SKIP`) rather than run against bad data - dbt's own DAG-aware
build order refusing to build on top of a known-bad upstream result.

## Key takeaway
Every other safeguard in this project (retries, branching, dynamic mapping,
dbt tests, orchestrated dbt tests, failure alerting) has been proven the same
way: trigger the real failure condition and check independent evidence it
was actually caught, not just that it was configured. CI is no different -
a workflow file existing and a badge on the repo mean nothing until a genuine
bad push has been sent through it and watched turn red. This is also the
first day's work that runs somewhere other than this machine - GitHub's own
infrastructure - completing the arc from "manually run a script" (Day 1)
through "orchestrated and alerting local pipeline" (Days 22-28) to "tested
automatically in the cloud before merge" (Day 29).
