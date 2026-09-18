"""
Generates a reproducible synthetic sales dataset for PySpark aggregation
practice: ~300 orders across 6 products and 5 customers, with a fixed
random seed so the same data comes back every time this runs.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

products = {
    "Laptop": (800, 1500),
    "Headphones": (50, 150),
    "Desk Chair": (100, 300),
    "Monitor": (150, 500),
    "Keyboard": (30, 100),
    "Mouse": (15, 60),
}
customers = [101, 102, 103, 104, 105]
start = date(2026, 1, 1)
days = 90

rows = []
order_id = 1
for i in range(days):
    day = start + timedelta(days=i)
    num_orders = random.randint(2, 5)
    for _ in range(num_orders):
        product_name = random.choice(list(products.keys()))
        low, high = products[product_name]
        amount = round(random.uniform(low, high), 2)
        customer_id = random.choice(customers)
        rows.append([order_id, customer_id, product_name, amount, day.isoformat()])
        order_id += 1

with open("sales_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "product_name", "amount", "order_date"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to sales_data.csv")
