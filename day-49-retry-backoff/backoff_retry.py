import random
import time

from flaky_api import FlakyAPI, TransientAPIError

MAX_ATTEMPTS = 5
BASE_DELAY = 0.5

api = FlakyAPI(fail_until_call=4)

print(f"Exponential backoff - up to {MAX_ATTEMPTS} attempts, delay doubles each time plus jitter\n")

for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        result = api.call()
        print(f"Attempt {attempt}: SUCCESS - {result}")
        break
    except TransientAPIError as e:
        print(f"Attempt {attempt}: FAILED - {e}")
        if attempt < MAX_ATTEMPTS:
            delay = BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 0.25)
            print(f"  Waiting {delay:.2f}s before retrying...")
            time.sleep(delay)
else:
    print(f"\nGave up after {MAX_ATTEMPTS} attempts. The job has FAILED.")

print("\nCall timing log (seconds since first call):")
start = api.call_log[0][1]
for call_number, timestamp, outcome in api.call_log:
    print(f"  call #{call_number}  +{timestamp - start:.4f}s  {outcome}")
