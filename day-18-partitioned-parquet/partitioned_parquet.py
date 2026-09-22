from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("Day18PartitionedParquet").getOrCreate()

df = spark.read.csv("sales_data.csv", header=True, inferSchema=True)
print(f"Total rows: {df.count()}")
print(f"Distinct order_date values: {df.select('order_date').distinct().count()}")

output_path = "sales_partitioned"
df.write.mode("overwrite").partitionBy("order_date").parquet(output_path)
print(f"Written partitioned Parquet to {output_path}/")

reloaded = spark.read.parquet(output_path)

target_date = "2026-01-15"

print("\n=== Plan WITHOUT a partition filter (baseline) ===")
reloaded.explain()

print(f"\n=== Plan WITH a partition filter (order_date = {target_date}) ===")
filtered = reloaded.filter(col("order_date") == target_date)
filtered.explain()

filtered_count = filtered.count()
print(f"\nRows for {target_date}: {filtered_count}")

# Cross-check against the source CSV directly, bypassing Spark entirely
import csv
csv_count = 0
with open("sales_data.csv") as f:
    for row in csv.DictReader(f):
        if row["order_date"] == target_date:
            csv_count += 1
print(f"Same date counted directly from the CSV: {csv_count}")

spark.stop()
