import requests
import csv

BASE_URL = "https://jsonplaceholder.typicode.com/comments"
PAGE_SIZE = 50

all_comments = []
page = 1
while True:
    resp = requests.get(BASE_URL, params={"_page": page, "_limit": PAGE_SIZE})
    resp.raise_for_status()
    data = resp.json()
    if not data:
        break
    all_comments.extend(data)
    page += 1

print(f"Fetched {len(all_comments)} comments across {page - 1} page(s)")

with open("seeds/raw_comments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "post_id", "name", "email", "body"])
    for c in all_comments:
        writer.writerow([c["id"], c["postId"], c["name"], c["email"], c["body"].replace("\n", " ")])

print("Written to seeds/raw_comments.csv")
