import csv
import random

ROWS = 2_000_000
STATUSES = ["completed", "pending", "cancelled"]

random.seed(42)

with open("large_orders.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "amount", "status", "notes"])
    for i in range(1, ROWS + 1):
        amount = round(random.uniform(5, 500), 2)
        status = STATUSES[i % 3]
        notes = "standard order processed via default fulfillment pipeline"
        writer.writerow([i, 1000 + (i % 5000), amount, status, notes])

print(f"Wrote {ROWS} rows to large_orders.csv")
