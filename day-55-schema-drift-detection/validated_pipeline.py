import json

from schema_check import REFERENCE_SCHEMA, diff_schema

BATCH_FILES = ["batch_1.json", "batch_2.json", "batch_3.json", "batch_4.json"]

total_revenue = 0.0
processed = 0
skipped = 0

for batch_file in BATCH_FILES:
    with open(batch_file) as f:
        rows = json.load(f)

    print(f"\nProcessing {batch_file}...")

    drift = diff_schema(REFERENCE_SCHEMA, rows)
    if drift["new_columns"] or drift["missing_columns"] or drift["type_changes"]:
        print("  SCHEMA DRIFT DETECTED:")
        if drift["new_columns"]:
            print(f"    new columns present:   {drift['new_columns']}")
        if drift["missing_columns"]:
            print(f"    expected columns missing: {drift['missing_columns']}")
        for col, expected, actual in drift["type_changes"]:
            print(f"    type changed: {col} expected {expected}, got {actual}")
    else:
        print("  no schema drift detected")

    for row in rows:
        status = row.get("status")
        if status is None:
            skipped += 1
            print(f"  order {row['order_id']}: SKIPPED (missing status)")
            continue

        amount = row.get("amount")
        if not isinstance(amount, (int, float)):
            skipped += 1
            print(f"  order {row['order_id']}: SKIPPED (amount is {type(amount).__name__}, not numeric)")
            continue

        if status == "completed":
            total_revenue += amount
        processed += 1
        print(f"  order {row['order_id']}: ok")

print(f"\nDone. Processed: {processed}, Skipped: {skipped}, Total completed revenue: {total_revenue}")
