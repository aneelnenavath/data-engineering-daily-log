# Day 44 — API Ingestion with Pagination

## Why this day is different

Every single data source in this project up to now has started as a static CSV someone
already had. Today builds the layer before that: pulling data from a public REST API
(JSONPlaceholder's /comments endpoint, 500 records) with proper pagination handling,
landing it as a new dbt seed, and proving the pagination logic is actually complete -
not just that it ran without error.

## Proof 1 - a realistic pagination bug, caught by independent verification

The first version of fetch_comments.py looped over a hardcoded page range
(for page in range(1, 10)) instead of detecting the real end of the data. Running it
fetched only 450 records. A separate script, verify_comments.py, called the same API
with no pagination parameters at all (which JSONPlaceholder answers by returning every
record it has) - a completely independent way of knowing the true total, reusing none of
the pagination logic being tested. It reported a true total of 500 against a fetched
total of only 450, with MATCH: False.

## Proof 2 - the real fix, verified the same independent way

fetch_comments.py was rewritten to loop with while True, stopping only when a page comes
back empty - letting the API itself be the source of truth for when the data runs out,
instead of a guessed page count. Rerunning fetch and verify reported 500 comments fetched
across exactly 10 pages, a true total of 500, a fetched total of 500, 500 unique ids, and
MATCH: True.

## Integration into dbt

The fetched data was seeded (dbt seed --select raw_comments, 500 rows loaded), given a
proper staging model (stg_comments) and tests (unique/not_null on id, not_null on
post_id and email). Full dbt build passed cleanly: 56/56.

## Key takeaway

A pagination bug like a hardcoded page count is exactly the kind of thing that looks
completely fine on the surface - the script runs, produces a file, prints a row count -
right up until you check that count against an independent source of truth. The fix
wasn't about handling errors better, it was about never trusting a guessed stopping
condition over the one signal that's actually authoritative: the API itself saying
there's no more data.
