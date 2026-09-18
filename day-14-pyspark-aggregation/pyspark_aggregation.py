from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, count, avg, round as _round, desc

spark = SparkSession.builder.appName("Day14Aggregation").getOrCreate()

df = spark.read.csv("sales_data.csv", header=True, inferSchema=True)

print("=== Raw schema ===")
df.printSchema()
print(f"Total rows read: {df.count()}")

agg_df = (
    df.groupBy("product_name")
    .agg(
        _round(_sum("amount"), 2).alias("total_revenue"),
        count("*").alias("num_orders"),
        _round(avg("amount"), 2).alias("avg_order_value"),
    )
    .orderBy(desc("total_revenue"))
)

print("\n=== Revenue by product ===")
agg_df.show()

output_path = "product_revenue_parquet"
agg_df.write.mode("overwrite").parquet(output_path)
print(f"Written to {output_path}/")

print("\n=== Re-reading the Parquet output to prove it's genuinely on disk ===")
reloaded = spark.read.parquet(output_path)
reloaded.orderBy(desc("total_revenue")).show()

spark.stop()
