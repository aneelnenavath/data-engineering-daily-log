import time

import pandas as pd

COLUMNS_WANTED = ["order_id", "amount"]

start = time.perf_counter()
csv_df = pd.read_csv("orders.csv", usecols=COLUMNS_WANTED)
csv_time = time.perf_counter() - start

start = time.perf_counter()
parquet_df = pd.read_parquet("orders.parquet", columns=COLUMNS_WANTED)
parquet_time = time.perf_counter() - start

print(f"CSV read (2 of 8 columns):     {csv_time:.3f}s, {len(csv_df)} rows")
print(f"Parquet read (2 of 8 columns): {parquet_time:.3f}s, {len(parquet_df)} rows")
print(f"Parquet was {csv_time / parquet_time:.1f}x faster")

assert csv_df["amount"].sum() == parquet_df["amount"].sum(), "totals disagree!"
print(f"Totals match exactly: {csv_df['amount'].sum():.2f}")

print("\n--- Fairness check: reading ALL 8 columns from both formats ---")

start = time.perf_counter()
csv_full = pd.read_csv("orders.csv")
csv_full_time = time.perf_counter() - start

start = time.perf_counter()
parquet_full = pd.read_parquet("orders.parquet")
parquet_full_time = time.perf_counter() - start

print(f"CSV read (all 8 columns):     {csv_full_time:.3f}s")
print(f"Parquet read (all 8 columns): {parquet_full_time:.3f}s")
print(f"Parquet was {csv_full_time / parquet_full_time:.1f}x faster even reading everything")
