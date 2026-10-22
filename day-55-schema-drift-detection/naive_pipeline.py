import json

BATCH_FILES = ["batch_1.json", "batch_2.json", "batch_3.json", "batch_4.json"]

total_revenue = 0
processed = 0

for batch_file in BATCH_FILES:
    with open(batch_file) as f:
        rows = json.load(f)
    print(f"\nProcessing {batch_file}...")
    for row in rows:
        if row["status"] == "completed":
            total_revenue += row["amount"]
        processed += 1
        print(f"  order {row['order_id']}: ok")

print(f"\nDone. Processed: {processed}, Total completed revenue: {total_revenue}")
