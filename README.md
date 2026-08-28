# Data Engineering Daily Log

One small, real task a day, each producing something worth committing — Mon–Fri only.
Every folder here is one day's work: code, a short README explaining the task, and
whatever output the task produced (a cleaned file, a diagram, a query result).

This plan was built from a 35-day starter plan, then checked against my actual resume
(three portfolio projects: TfL transit pipeline, banking transaction pipeline, retail
data pipeline) to make sure every technology on the resume gets deliberate daily
practice — not just the ones that are easy to demo. Days marked **[NEW]** were added
for that reason; **[REPLACED]** means the original day was upgraded from a simulated
version to the real tool.

Progress tracker (interactive, saves state independently of any chat):
https://claude.ai/code/artifact/b7a7fcf3-6cab-49d6-98bc-87c445212408

## Week 1 — Python, SQL & Shell Foundations

| Day | Folder | Task |
|---|---|---|
| 1 | `day-01-csv-cleaner` | CSV data cleaner (Python, pandas) — load a messy CSV, fix it, log what changed |
| 2 | `day-02-log-parser` | Log file parser (Python, regex) — extract IP/timestamp/status from a web log |
| 3 | `day-03-window-functions-sql` | Window functions practice (SQL, SQLite) — RANK, LAG/LEAD, running totals |
| 4 | `day-04-json-to-csv` | JSON-to-CSV converter (Python) — pull a public API, flatten nested JSON |
| 5 | `day-05-csv-cleaner-tests` | Unit tests for Day 1 (pytest) — 5+ edge cases |
| 6 | `day-06-bash-pipeline` | **[NEW]** Bash pipeline script — chain Day 1 + Day 2 into one shell script with args, exit codes, logging |

## Week 2 — Relational Databases & Hadoop Ecosystem

| Day | Folder | Task |
|---|---|---|
| 7 | `day-07-ecommerce-schema` | E-commerce schema design (MySQL) — 5-table schema + Mermaid ER diagram |
| 8 | `day-08-join-strategy-mysql` | Join strategy comparison (MySQL, EXPLAIN) — INNER vs LEFT vs correlated subquery |
| 9 | `day-09-hdfs-hive-basics` | **[NEW]** HDFS + Hive basics — load a CSV into HDFS, create an external Hive table, run HiveQL |
| 10 | `day-10-sqoop-import` | **[NEW]** Sqoop import practice — full + incremental import from MySQL into Hive, saved job |
| 11 | `day-11-cassandra-modelling` | **[REPLACED]** Real Cassandra data modelling (cqlsh) — `orders_by_customer` / `orders_by_product` with real partition + clustering keys, not a SQLite stand-in |
| 12 | `day-12-data-quality-checker` | Data quality checker (Python) — null rates, duplicate keys, out-of-range values |
| 13 | `day-13-analytical-queries-duckdb` | Analytical queries practice (SQL, DuckDB) — rolling 7-day revenue, top customers, MoM growth |

## Week 3 — Big Data & Spark

| Day | Folder | Task |
|---|---|---|
| 14 | `day-14-pyspark-aggregation` | PySpark aggregation script — group/aggregate a CSV, write Parquet |
| 15 | `day-15-join-benchmark-pyspark` | Join strategy benchmark (PySpark) — broadcast vs. no hint, timed |
| 16 | `day-16-spark-sql-join` | Spark SQL version of Day 15's join — temp views, compare explain() plans |
| 17 | `day-17-star-schema` | Star schema diagram — 1 fact + 3+ dimension tables, Mermaid ER |
| 18 | `day-18-partitioned-parquet` | Partitioned Parquet table — partition by date, confirm partition pruning |

## Week 4 — Streaming & Orchestration

| Day | Folder | Task |
|---|---|---|
| 19 | `day-19-kafka-producer-consumer` | Kafka producer & consumer (Docker) |
| 20 | `day-20-structured-streaming-wordcount` | Structured Streaming word count from a socket stream |
| 21 | `day-21-kafka-checkpoint-recovery` | Checkpoint recovery demo — kill/restart consumer, confirm clean resume |
| 22 | `day-22-mini-etl` | Mini ETL pipeline — extract/transform/load as three clean functions |
| 23 | `day-23-airflow-dag-etl` | Airflow DAG wrapping Day 22's ETL — scheduled 2-task DAG |
| 24 | `day-24-ssh-tunnel-sshoperator` | **[NEW]** SSH tunnelling + Airflow SSHOperator — reverse SSH tunnel, remote start/stop of a service with an idempotent PID check |

## Week 5 — Cloud: AWS & Snowflake

| Day | Folder | Task |
|---|---|---|
| 25 | `day-25-s3-upload-download` | S3 upload/download script (boto3) |
| 26 | `day-26-ec2-provisioning` | **[NEW]** EC2 provisioning — launch/stop an instance via boto3, connect over SSH, note right-sizing trade-offs |
| 27 | `day-27-iam-least-privilege` | Least-privilege IAM policy for Day 25's script — no wildcards |
| 28 | `day-28-fernet-airflow-variables` | **[NEW]** Fernet-encrypted Airflow Variables — generate a key, store a secret encrypted, retrieve it in a DAG without ever printing it |
| 29 | `day-29-lambda-stub` | Lambda function stub — triggers on S3 upload, logs file name/size |
| 30 | `day-30-glue-athena` | Glue crawler + Athena query against Day 25's S3 data |
| 31 | `day-31-snowflake-load-query` | **[NEW]** Snowflake — load Day 25's data, run analytical queries, compare to the Athena approach |
| 32 | `day-32-dockerize-script` | Dockerize an earlier script — run in a container with a mounted volume |

## Week 6 — Polish & Interview-Readiness

| Day | Folder | Task |
|---|---|---|
| 33 | `day-33-readme-overhaul` | README overhaul for one main project — architecture diagram, setup, "what I'd do differently" |
| 34 | `day-34-backfill-tests` | Add pytest suites to two earlier scripts |
| 35 | `day-35-bug-postmortem` | Bug postmortem — one real bug: what broke, how found, how fixed |
| 36 | `day-36-refactor-pass` | Refactor the messiest script — better names, smaller functions, type hints |
| 37 | `day-37-recap-readme` | 42-day recap README with links; short LinkedIn recap post |

## Week 7 — Advanced SQL & Python Patterns

| Day | Folder | Task |
|---|---|---|
| 38 | `day-38-ctes-recursive` | CTEs & recursive queries — subquery → CTE, RECURSIVE CTE over an employee-manager hierarchy |
| 39 | `day-39-oop-pipeline` | Python OOP — refactor Day 22's ETL into Extractor/Transformer/Loader classes |
| 40 | `day-40-decorators-context-managers` | `@timer` decorator; a context manager that always closes a DB connection safely |
| 41 | `day-41-generators-large-files` | Rewrite Day 2's log parser as a generator — memory-light on a large file |
| 42 | `day-42-custom-exceptions` | Add a `DataQualityError` to Day 12's checker — raised clearly on failed checks |

## How the resume gaps map to days

- **Hadoop (HDFS, Hive, Sqoop)** → Days 9, 10 — used throughout the retail pipeline project (`hdfs fsck`, external/partitioned Hive tables, saved Sqoop jobs)
- **Apache Cassandra** → Day 11 — real `cqlsh`, not a simulation
- **Snowflake** → Day 31
- **SSH tunnelling & Airflow SSHOperator** → Day 24 — the orchestration pattern from the banking pipeline
- **EC2 + right-sizing** → Day 26 — the fix applied in the TfL pipeline
- **Fernet-encrypted Airflow Variables** → Day 28 — the credential fix applied in the TfL pipeline
- **Bash** → Day 6
