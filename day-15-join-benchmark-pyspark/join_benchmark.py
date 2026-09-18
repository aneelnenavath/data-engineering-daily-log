import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

spark = SparkSession.builder.appName("Day15JoinBenchmark").getOrCreate()

orders = spark.read.csv("orders_large.csv", header=True, inferSchema=True)
customers = spark.read.csv("customers_dim.csv", header=True, inferSchema=True)

print(f"orders: {orders.count()} rows, customers: {customers.count()} rows")


def timed_join(join_df, label, trials=3):
    times = []
    for i in range(trials):
        start = time.time()
        result_count = join_df.count()
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  {label} trial {i + 1}: {elapsed:.3f}s (result rows: {result_count})")
    avg = sum(times) / len(times)
    print(f"  {label} average: {avg:.3f}s")
    return avg


print("\n=== No hint (auto-broadcast disabled -> forces a shuffle/sort-merge join) ===")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
no_hint_df = orders.join(customers, on="customer_id")
no_hint_df.explain()
no_hint_avg = timed_join(no_hint_df, "No-hint join")

print("\n=== Broadcast hint (small customers table explicitly broadcast) ===")
broadcast_df = orders.join(broadcast(customers), on="customer_id")
broadcast_df.explain()
broadcast_avg = timed_join(broadcast_df, "Broadcast join")

print("\n=== Summary ===")
print(f"No-hint (sort-merge) average: {no_hint_avg:.3f}s")
print(f"Broadcast average:            {broadcast_avg:.3f}s")
if broadcast_avg > 0:
    print(f"Broadcast was {no_hint_avg / broadcast_avg:.2f}x faster")

spark.stop()
