import time
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Day16SparkSQLJoin").getOrCreate()

orders = spark.read.csv("orders_large.csv", header=True, inferSchema=True)
customers = spark.read.csv("customers_dim.csv", header=True, inferSchema=True)

# Temp views - this is the Spark SQL equivalent of a DataFrame: registering
# it under a name so plain SQL strings can reference it, instead of chaining
# DataFrame methods like Day 15 did.
orders.createOrReplaceTempView("orders")
customers.createOrReplaceTempView("customers")

print(f"orders: {orders.count()} rows, customers: {customers.count()} rows")


def timed_sql(query, label, trials=3):
    times = []
    for i in range(trials):
        start = time.time()
        result_count = spark.sql(query).count()
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  {label} trial {i + 1}: {elapsed:.3f}s (result rows: {result_count})")
    avg = sum(times) / len(times)
    print(f"  {label} average: {avg:.3f}s")
    return avg


no_hint_sql = """
    SELECT o.order_id, o.customer_id, o.amount, c.customer_name, c.region
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
"""

broadcast_sql = """
    SELECT /*+ BROADCAST(c) */ o.order_id, o.customer_id, o.amount, c.customer_name, c.region
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
"""

print("\n=== No hint (auto-broadcast disabled -> forces a shuffle/sort-merge join) ===")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
spark.sql(f"EXPLAIN {no_hint_sql}").show(truncate=False)
no_hint_avg = timed_sql(no_hint_sql, "No-hint SQL join")

print("\n=== Broadcast hint via SQL comment syntax: /*+ BROADCAST(c) */ ===")
spark.sql(f"EXPLAIN {broadcast_sql}").show(truncate=False)
broadcast_avg = timed_sql(broadcast_sql, "Broadcast SQL join")

print("\n=== Summary ===")
print(f"No-hint (sort-merge) average: {no_hint_avg:.3f}s")
print(f"Broadcast average:            {broadcast_avg:.3f}s")
if broadcast_avg > 0:
    print(f"Broadcast was {no_hint_avg / broadcast_avg:.2f}x faster")

spark.stop()
