# Day 58 — Memory-Efficient Processing: Chunked Reading for Large Files

## What this demonstrates

"How would you process a file too large to fit in memory?" is one of
the most commonly asked practical data engineering interview questions.
The naive instinct - pandas.read_csv() with no arguments - loads every
row of a file into memory before any processing can begin. That's
harmless for a small file, but for a genuinely large one it either
slows a machine to a crawl or fails outright with an out-of-memory
error. Today's problem: measure the real difference between loading a
large file whole versus processing it in chunks, and confirm the
chunked approach is not just lower-memory but exactly as correct.

## The data

generate_data.py wrote 2,000,000 order rows to large_orders.csv - a
167 MB file, large enough to produce a clearly measurable difference in
actual memory usage.

## Proof 1 - loading the whole file at once

full_load.py measures the Python process's real resident memory (RSS,
via psutil) before and after a single pandas.read_csv() call loading
the entire file, then computes the sum of amount for all completed
orders.

    Memory before load: 78.8 MB
    Memory after load:  156.2 MB
    Memory used by full load: 77.4 MB
    Total completed revenue: 168295997.46

Holding the complete 2-million-row DataFrame in memory at once cost
77.4 MB of real RAM, on top of whatever else is running on the machine.

## Proof 2 - processing the same file in chunks

chunked_load.py reads the identical file via
pd.read_csv(chunksize=50_000), summing each 50,000-row chunk's
completed-order amounts into a running total and discarding the chunk
immediately afterward - the full dataset never exists in memory at
once. Peak memory is tracked across every chunk rather than measured
once at the end.

    Memory before processing: 79.0 MB
    Peak memory during chunked processing: 84.1 MB
    Memory used (peak - before): 5.1 MB
    Rows processed: 2000000
    Total completed revenue: 168295997.46

Peak memory used was 5.1 MB - roughly 15x less than the full load - and
all 2,000,000 rows were processed, producing the exact same total to
the cent: 168295997.46.

## Why this matters

The chunked version isn't an approximation or a faster-but-less-accurate
shortcut - it produces an identical, exact result while using a small
fraction of the peak memory, because it never needs to hold more than
one chunk's worth of data at a time. This is what actually lets a
pipeline scale to files larger than available RAM: the constraint
becomes how much memory one chunk needs, not how large the entire file
is. A full load that works fine on a 167 MB test file will simply fail
once the real file is 10 or 50 times larger; the chunked version's
memory usage barely changes at all, since it was never proportional to
the file size in the first place.
