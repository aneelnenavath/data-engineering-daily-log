TOTAL_RECORDS = 250
PAGE_SIZE = 50

ALL_RECORDS = [
    {"order_id": i, "customer_id": 1000 + i, "amount": round(10 + (i * 1.37) % 490, 2)}
    for i in range(1, TOTAL_RECORDS + 1)
]


class RateLimitedError(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__(f"rate limited, retry after {retry_after}s")


class MockOrdersAPI:
    """Simulates a paginated REST API. Every 3rd call returns a 429-style
    rate limit error instead of data, requiring the caller to wait and
    retry rather than treating it as fatal or ignoring it."""

    def __init__(self):
        self.call_count = 0

    def get_page(self, cursor=None):
        self.call_count += 1

        if self.call_count % 3 == 0:
            raise RateLimitedError(retry_after=1.5)

        offset = 0 if cursor is None else int(cursor)
        page = ALL_RECORDS[offset:offset + PAGE_SIZE]
        next_offset = offset + PAGE_SIZE
        next_cursor = str(next_offset) if next_offset < TOTAL_RECORDS else None

        return {"records": page, "next_cursor": next_cursor}
