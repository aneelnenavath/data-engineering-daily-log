import os

import pandas as pd
import psutil

process = psutil.Process(os.getpid())

mem_before = process.memory_info().rss / (1024 ** 2)

df = pd.read_csv("large_orders.csv")

mem_after = process.memory_info().rss / (1024 ** 2)

total_completed = df.loc[df["status"] == "completed", "amount"].sum()

print(f"Memory before load: {mem_before:.1f} MB")
print(f"Memory after load:  {mem_after:.1f} MB")
print(f"Memory used by full load: {mem_after - mem_before:.1f} MB")
print(f"Total completed revenue: {total_completed:.2f}")
