import requests
import csv

resp = requests.get("https://jsonplaceholder.typicode.com/comments")
resp.raise_for_status()
true_total = len(resp.json())

with open("seeds/raw_comments.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

fetched_total = len(rows)
fetched_ids = set(r["id"] for r in rows)

print(f"True total (independent unpaginated API call): {true_total}")
print(f"Fetched total (from CSV):                       {fetched_total}")
print(f"Unique ids in CSV:                               {len(fetched_ids)}")
print(f"MATCH: {true_total == fetched_total == len(fetched_ids)}")
