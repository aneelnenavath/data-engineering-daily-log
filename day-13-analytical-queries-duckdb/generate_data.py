"""
Generates a synthetic but reproducible sales dataset for analytical query
practice: ~90 days of orders across 5 customers, with enough day-to-day
randomness that a rolling 7-day revenue trend and month-over-month growth
are both visible in the result.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)  # fixed seed -> same data every time this is run

customers = [101, 102, 103, 104, 105]
start = date(2026, 1, 1)
days = 90

rows = []
order_id = 1
for i in range(days):
    day = start + timedelta(days=i)
    num_orders = random.randint(1, 4)
    for _ in range(num_orders):
        customer_id = random.choice(customers)
        amount = round(random.uniform(15, 250), 2)
        rows.append([order_id, customer_id, day.isoformat(), amount])
        order_id += 1

with open("sales_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "order_date", "amount"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows across {days} days to sales_data.csv")
