"""
Generates two CSVs sized to make broadcast-vs-shuffle join strategy
actually matter: a large 'orders' fact table and a tiny 'customers'
dimension table, with a fixed random seed for reproducibility.
"""
import csv
import random

random.seed(42)

# Small dimension table - exactly the kind of table you'd want broadcast
# to every executor instead of shuffled.
customers = [
    (1, "Alice Johnson", "North"), (2, "Bob Smith", "South"),
    (3, "Carla Diaz", "East"), (4, "David Lee", "West"),
    (5, "Emma Wilson", "North"), (6, "Frank Chen", "South"),
    (7, "Grace Kim", "East"), (8, "Henry Patel", "West"),
    (9, "Isla Brown", "North"), (10, "Jack Nguyen", "South"),
]
with open("customers_dim.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_id", "customer_name", "region"])
    writer.writerows(customers)

# Large fact table - 50,000 orders referencing those 10 customers.
num_orders = 50_000
with open("orders_large.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "amount"])
    for order_id in range(1, num_orders + 1):
        customer_id = random.randint(1, 10)
        amount = round(random.uniform(10, 500), 2)
        writer.writerow([order_id, customer_id, amount])

print(f"Wrote {len(customers)} rows to customers_dim.csv")
print(f"Wrote {num_orders} rows to orders_large.csv")
