# Day 56 — API Pagination & Rate Limiting

## What this demonstrates

Real APIs almost never return all their data in a single response - they
paginate, typically returning a cursor or page token that tells the
caller where the next chunk starts. They also commonly rate-limit
callers, responding with a 429-style error and a retry-after value
instead of data if requests come in too fast. Code that doesn't follow
pagination to completion, or that doesn't respect a rate limit, fails in
ways that are easy to miss entirely - a pipeline can run cleanly, with
no error raised anywhere, while still silently working with a fraction
of the real dataset.

## The mock API

mock_api.py simulates a paginated endpoint holding 250 order records
split into pages of 50. get_page(cursor) returns a page of records plus
a next_cursor telling the caller where to continue, or None once
there's nothing left. Separately, every 3rd call made to the API -
regardless of whether it's a fresh page request or a retry - raises
RateLimitedError instead of returning data, exactly like a real API
returning HTTP 429 with a Retry-After header.

## Proof 1 - a naive client silently fetches a fraction of the data

naive_client.py calls get_page() once, takes the result, and assumes
that's everything.

    Fetched 50 records.
    API calls made: 1
    Done - assuming this is all the data.

The true dataset has 250 records. The naive client silently walked away
with 20% of it. No error was raised anywhere - the only reason this is
even detectable is knowing the true total in advance, which a real
pipeline usually doesn't have.

## Proof 2 - a paginated, rate-limit-aware client gets everything

paginated_client.py loops on get_page(cursor), following next_cursor
until it comes back None, and wraps each call in a try/except that
catches RateLimitedError specifically: on a rate limit it waits exactly
as long as the API said to (retry_after), then retries the identical
request without advancing the cursor.

    Page 1: fetched 50 records (running total: 50)
    Page 2: fetched 50 records (running total: 100)
      rate limited - waiting 1.5s before retrying...
    Page 3: fetched 50 records (running total: 150)
    Page 4: fetched 50 records (running total: 200)
      rate limited - waiting 1.5s before retrying...
    Page 5: fetched 50 records (running total: 250)

    Done. Total records fetched: 250
    Total API calls made (including rate-limited ones): 7

All 250 records were retrieved - the complete dataset. Both rate limit
events were caught and handled correctly: the client paused for the
exact duration requested and successfully retried, rather than crashing
on the exception or treating a 429 as a sign to give up. The loop only
stopped once next_cursor genuinely came back None.

## Why this matters

A pipeline that only reads the first page of a paginated API can run
with a completely clean exit code and no errors in its logs while still
missing the vast majority of real data - this is one of the quietest,
hardest-to-catch categories of data engineering bug, because nothing
about the failure looks like a failure. Following the cursor to
completion and treating a rate limit as a signal to wait rather than an
error to crash on are both required for an ingestion job to actually be
correct, not just error-free.
