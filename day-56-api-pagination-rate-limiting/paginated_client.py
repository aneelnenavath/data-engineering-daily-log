import time

from mock_api import MockOrdersAPI, RateLimitedError

api = MockOrdersAPI()

all_records = []
cursor = None
page_num = 0

while True:
    try:
        response = api.get_page(cursor=cursor)
    except RateLimitedError as e:
        print(f"  rate limited - waiting {e.retry_after}s before retrying...")
        time.sleep(e.retry_after)
        continue

    page_num += 1
    records = response["records"]
    all_records.extend(records)
    print(f"Page {page_num}: fetched {len(records)} records (running total: {len(all_records)})")

    cursor = response["next_cursor"]
    if cursor is None:
        break

print(f"\nDone. Total records fetched: {len(all_records)}")
print(f"Total API calls made (including rate-limited ones): {api.call_count}")
