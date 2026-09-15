# Day 10 — Sqoop Import Practice

Full and incremental import from MySQL into HDFS/Hive using Apache Sqoop,
built on top of Day 9's HDFS/Hive stack plus Day 7's MySQL container.

## Setup (installed manually inside the `namenode` container - bde2020
images don't ship Sqoop)
- Downloaded Sqoop 1.4.7 (hadoop260 build) + MySQL Connector/J 8.0.28
- Connected `ecommerce-mysql` onto the Day 9 Docker network:
  docker network connect day-09-hdfs-hive-basics_default ecommerce-mysql

## Gotchas hit and fixed
1. Missing `commons-lang-2.6.jar` - Sqoop 1.4.7 needs Commons Lang 2.x;
   Hadoop 3.x only ships Commons Lang 3, a different incompatible library.
2. Hadoop 3.x's hadoop-functions.sh has "bad substitution" bugs when
   launching a real MapReduce task under old Sqoop - worked around by
   setting mapreduce.framework.name=local permanently in mapred-site.xml,
   since this stack has no YARN ResourceManager anyway.
3. ClassNotFoundException for the table's generated ORM class under
   LocalJobRunner - fixed by pointing --outdir/--bindir at a fixed folder
   and adding it to HADOOP_CLASSPATH before the JVM starts.
4. `sqoop job --create` (Sqoop's built-in "saved job" feature) has a real
   bug: it silently drops --table/--connect/--check-column/--last-value
   when storing certain flag combinations (confirmed via `sqoop job
   --show`, which never listed them). Worked around with
   run_incremental_import.sh - a small script that tracks the last
   imported customer_id in last_value.txt and passes it back in as
   --last-value, doing manually what the saved-job feature was supposed
   to do automatically.
5. A crashed terminal run of that script, before last_value.txt existed
   yet, defaulted to --last-value 0 and silently re-imported the whole
   table as a duplicate file. Diagnosed via `hdfs dfs -cat ... | sort |
   uniq -c` (every row appearing exactly twice) and file sizes/timestamps,
   fixed by deleting the one stray part file. The script itself was then
   changed to fail loudly instead of silently defaulting to 0.

## Files
- run_incremental_import.sh - incremental import + bookmark tracking
- last_value.txt - current bookmark (customer_id already imported through)

## Result
customers_from_mysql (Hive external table over /data/sqoop/customers)
holds all 7 rows, verified duplicate-free.
