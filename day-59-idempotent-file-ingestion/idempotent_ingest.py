import csv
import hashlib
import json
import os
import sys

MANIFEST_FILE = "processed_manifest.json"


def file_checksum(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {}
    with open(MANIFEST_FILE) as f:
        return json.load(f)


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)


filename = sys.argv[1] if len(sys.argv) > 1 else "incoming_orders.csv"

checksum = file_checksum(filename)
manifest = load_manifest()

if checksum in manifest:
    print(f"SKIPPED: {filename} (checksum {checksum[:12]}...) was already processed "
          f"as part of run '{manifest[checksum]['original_filename']}' - not reprocessing.")
    sys.exit(0)

total_revenue = 0.0
rows = 0

with open(filename) as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_revenue += float(row["amount"])
        rows += 1

with open("revenue_ledger.txt", "a") as ledger:
    ledger.write(f"{filename}: {rows} rows, revenue {total_revenue:.2f}\n")

manifest[checksum] = {"original_filename": filename, "rows": rows, "revenue": round(total_revenue, 2)}
save_manifest(manifest)

print(f"Processed {filename}: {rows} rows, revenue {total_revenue:.2f} "
      f"(checksum {checksum[:12]}... recorded)")
