import random

import pandas as pd

ROWS = 1_000_000
STATUSES = ["completed", "pending", "cancelled"]

random.seed(42)

df = pd.DataFrame({
    "order_id": range(1, ROWS + 1),
    "customer_id": [1000 + (i % 5000) for i in range(ROWS)],
    "product_id": [2000 + (i % 800) for i in range(ROWS)],
    "warehouse_id": [i % 12 for i in range(ROWS)],
    "status": [STATUSES[i % 3] for i in range(ROWS)],
    "amount": [round(random.uniform(5, 500), 2) for _ in range(ROWS)],
    "shipping_cost": [round(random.uniform(2, 25), 2) for _ in range(ROWS)],
    "notes": ["standard order processed via default fulfillment pipeline" for _ in range(ROWS)],
})

df.to_csv("orders.csv", index=False)
df.to_parquet("orders.parquet", index=False)

print(f"Wrote {ROWS} rows x {len(df.columns)} columns to orders.csv and orders.parquet")
