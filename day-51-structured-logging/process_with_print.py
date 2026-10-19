import csv

ALLOWED_STATUSES = {"completed", "pending", "cancelled"}

print("Starting order batch processing...")

processed = 0
failed = 0

with open("orders_batch.csv") as f:
    for row in csv.DictReader(f):
        row_id = row["row_id"]

        if not row["customer_id"].strip():
            print(f"Problem with row {row_id}: missing customer_id")
            failed += 1
            continue

        try:
            amount = float(row["amount"])
        except ValueError:
            print(f"Problem with row {row_id}: amount is not a number ({row['amount']!r})")
            failed += 1
            continue

        if amount < 0:
            print(f"Problem with row {row_id}: negative amount ({amount})")
            failed += 1
            continue

        if row["status"] not in ALLOWED_STATUSES:
            print(f"Problem with row {row_id}: bad status ({row['status']!r})")
            failed += 1
            continue

        print(f"Row {row_id} processed OK - customer {row['customer_id']}, amount {amount}")
        processed += 1

print(f"Done. Processed: {processed}, Failed: {failed}")
