import os

import pandas as pd
import psutil

process = psutil.Process(os.getpid())

mem_before = process.memory_info().rss / (1024 ** 2)
peak_mem = mem_before

total_completed = 0.0
rows_seen = 0

for chunk in pd.read_csv("large_orders.csv", chunksize=50_000):
    total_completed += chunk.loc[chunk["status"] == "completed", "amount"].sum()
    rows_seen += len(chunk)

    current_mem = process.memory_info().rss / (1024 ** 2)
    if current_mem > peak_mem:
        peak_mem = current_mem

print(f"Memory before processing: {mem_before:.1f} MB")
print(f"Peak memory during chunked processing: {peak_mem:.1f} MB")
print(f"Memory used (peak - before): {peak_mem - mem_before:.1f} MB")
print(f"Rows processed: {rows_seen}")
print(f"Total completed revenue: {total_completed:.2f}")
