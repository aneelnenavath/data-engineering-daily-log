"""
Generates a reproducible sales dataset spanning 30 distinct days, sized
so each day becomes its own partition directory once written to Parquet.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

start = date(2026, 1, 1)
days = 30

rows = []
order_id = 1
for i in range(days):
    day = start + timedelta(days=i)
    num_orders = random.randint(80, 150)
    for _ in range(num_orders):
        customer_id = random.randint(1, 20)
        amount = round(random.uniform(10, 500), 2)
        rows.append([order_id, customer_id, amount, day.isoformat()])
        order_id += 1

with open("sales_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "amount", "order_date"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows across {days} days to sales_data.csv")
