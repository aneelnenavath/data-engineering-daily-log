# Day 9 — HDFS & Hive Basics

A 5-container Hadoop/Hive stack (namenode, datanode, hive-metastore-postgresql,
hive-metastore, hive-server) brought up with Docker Compose, used to load a
CSV into HDFS and query it through an external Hive table.

## Bring up the stack
docker compose up -d

## Gotcha: Git Bash / MINGW64 path mangling
Running `hdfs dfs -ls /` from Git Bash fails with:
    ls: No FileSystem for scheme "C"
This isn't a Hadoop problem — MSYS auto-rewrites a bare `/` argument into a
Windows path before Docker ever sees it. Fix: prefix the command with
MSYS_NO_PATHCONV=1, e.g.
    MSYS_NO_PATHCONV=1 docker exec -it namenode hdfs dfs -ls /

## Loading the CSV into HDFS
docker cp ./customers_sample.csv namenode:/tmp/customers_sample.csv
docker exec -it namenode hdfs dfs -mkdir -p /data/customers
docker exec -it namenode hdfs dfs -put /tmp/customers_sample.csv /data/customers/
Verified with `hdfs dfs -ls` (real byte size) and `hdfs dfs -cat`
(byte-identical content) rather than trusting a clean exit code alone.

## External Hive table
docker exec -it hive-server beeline -u "jdbc:hive2://localhost:10000"

    CREATE EXTERNAL TABLE customers (
      customer_id INT, name STRING, city STRING, country STRING
    )
    ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION '/data/customers'
    TBLPROPERTIES ("skip.header.line.count"="1");

EXTERNAL means dropping the table later deletes only Hive's metadata, never
the underlying HDFS files.

## Proof the table reads HDFS live, not a one-time snapshot
A second CSV (customers_sample_2.csv) was added straight into the same HDFS
directory, bypassing Hive entirely, with the table definition never touched.
Re-running `SELECT * FROM customers` afterward returned 8 rows instead of 6 -
confirming Hive re-scans its backing directory at query time rather than
caching anything from table creation.

## Note
Running a shell command while still inside a `beeline` session doesn't fail
outright - beeline buffers it as an incomplete SQL statement and shows a
continuation prompt instead. `!quit` on a clean prompt returns to the regular
shell.
