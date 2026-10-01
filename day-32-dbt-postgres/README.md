# Day 32 — dbt Against a Real Postgres Target

## Goal
Every dbt model so far in this project ran against an embedded DuckDB file (dev.duckdb) -
convenient, but not how dbt is used in most real companies, where the warehouse is a genuine
client-server database reachable over the network. This day adds a second named profiles.yml
target pointing at a real Postgres instance running in Docker, and proves the exact same dbt
project builds, tests, and snapshots correctly against it.

## Setup
- postgres:16 running in Docker on the shared daylog-net network
- profiles.yml now has two outputs under one profile: dev (DuckDB, default) and postgres

## The debugging trail
1. Broken bare pip on Anaconda (again) - pip install dbt-postgres failed on Windows with a
   process-creation error, the same broken-Anaconda-pip issue seen earlier in this project
   inside Docker containers, this time on the host itself. Fixed with: python -m pip install dbt-postgres
2. dbt debug failed with "password authentication failed for user dbt_user", even though the
   password in profiles.yml matched the container's own POSTGRES_PASSWORD env var exactly.
3. Ruled out a stale data volume - Postgres only applies POSTGRES_PASSWORD the first time it
   initializes its data directory. The container was on a named volume, so it was removed and
   recreated with a fresh volume and a clean initdb - same error persisted.
4. Verified the container's credentials were actually correct, independent of dbt - connecting
   with psql to the container's own internal network IP (which forces Postgres's real
   scram-sha-256 password check) succeeded with the dbt_pass password.
5. Found the real cause with netstat - two different processes were both listening on port 5432:
   postgres.exe (a native PostgreSQL Windows service already on the machine, unrelated to Docker)
   and com.docker.backend.exe. The native Windows service was answering localhost:5432 with its
   own unrelated credentials before the connection ever reached the Docker container.
6. Fix: remapped the Docker container to host port 5433 instead of 5432, updated profiles.yml to
   match, and re-ran dbt debug - OK connection ok, All checks passed.

## Proof: full build against real Postgres
dbt build --target postgres --profiles-dir .
Finished running 1 incremental model, 3 seeds, 1 snapshot, 1 table model, 11 data tests, 1 view model
Completed successfully
Done. PASS=18 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=18

## Proof the data genuinely landed in Postgres (bypassing dbt entirely)
Queried directly with psql, independent of dbt:
- public.mart_customer_revenue, public.raw_customers, public.raw_events, public.raw_orders,
  public.stg_events all confirmed to exist as real tables via \dt
- SELECT COUNT(*) FROM public.mart_customer_revenue returned 9
- The snapshot table main.customers_snapshot confirmed via pg_tables

## Key takeaway
Switching dbt from DuckDB to Postgres is a trivial config change, but the real lesson of the day
was diagnostic: a port conflict with a pre-existing local service can produce an error that looks
exactly like a credentials problem, and the only way to tell the difference is to check what's
actually listening on the port rather than re-checking the password over and over.
