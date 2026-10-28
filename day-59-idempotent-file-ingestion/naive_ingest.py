import csv
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "incoming_orders.csv"

total_revenue = 0.0
rows = 0

with open(filename) as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_revenue += float(row["amount"])
        rows += 1

with open("revenue_ledger.txt", "a") as ledger:
    ledger.write(f"{filename}: {rows} rows, revenue {total_revenue:.2f}\n")

print(f"Processed {filename}: {rows} rows, revenue {total_revenue:.2f} (appended to ledger)")
