# Day 55 — Schema Evolution / Schema Drift Detection

## What this demonstrates

Real data feeds change shape over time: a new column gets added
upstream, an existing column's type quietly shifts, or a column
disappears. Code that implicitly assumes every batch looks exactly like
the first one it ever saw either fails loudly and unpredictably, or -
worse - keeps running and silently drops or mishandles the new shape of
the data. Today's problem: detect schema drift explicitly, before any
row-level processing happens, instead of discovering it from a crash or
not discovering it at all.

## The data

Four batches of order records simulate a feed changing shape over four
days:

    batch_1.json - the baseline shape: order_id, customer_id, status,
        amount, order_date
    batch_2.json - gains an unexpected new column, discount_code
    batch_3.json - is missing the status column entirely
    batch_4.json - has amount as a quoted string instead of a number

## Proof 1 - a naive fixed-schema pipeline fails in two different ways

naive_pipeline.py assumes every row has a status key and a numeric
amount, with no schema checking at all.

Batch 1 processed fine. Batch 2 also "succeeded" - but completely
silently: the new discount_code column was never noticed or logged
anywhere, even though the schema genuinely changed. Batch 3 crashed
outright on its first row:

    KeyError: 'status'

Because the crash was unhandled, batch 4 - two perfectly processable
orders - was never even reached. One missing column took down
everything downstream of it, and the one real schema change that didn't
crash the job (batch 2) passed with zero indication anything had
changed at all.

## Proof 2 - explicit schema comparison catches all three kinds of drift

schema_check.py defines a REFERENCE_SCHEMA describing the expected
columns and types, and a diff_schema() function that inspects a batch's
actual keys and inferred value types against it, returning exactly
which columns are new, which expected columns are missing, and which
columns changed type.

validated_pipeline.py runs this check against every batch before
touching any rows, and also processes rows defensively - a missing
status or a non-numeric amount is skipped with a precise, logged reason
instead of raising an unhandled exception. Result, run against the
identical four batches:

    batch_1.json - no schema drift detected, all 3 orders processed
    batch_2.json - SCHEMA DRIFT DETECTED: new columns present: ['discount_code']
        all 3 orders still processed correctly
    batch_3.json - SCHEMA DRIFT DETECTED: expected columns missing: ['status']
        both orders SKIPPED (missing status), job continues
    batch_4.json - SCHEMA DRIFT DETECTED: type changed: amount expected float, got str
        both orders SKIPPED (amount is str, not numeric), job continues

    Done. Processed: 6, Skipped: 4, Total completed revenue: 273.09

All four batches were fully evaluated with nothing crashing. Every
instance of drift was reported with the exact column and the exact
nature of the change, every skipped row has a precise reason attached,
and the final revenue total (273.09) is exactly the sum of the four
genuinely valid completed orders - 49.99 + 75.00 + 60.00 + 88.10.

## Why this matters

A fixed-schema assumption baked silently into processing code fails in
the worst possible way: either a hard crash that takes unrelated good
data down with it, or - just as bad - no failure at all, so a real
change to the data goes completely unnoticed until something downstream
quietly breaks. Comparing each batch's actual schema against a known
reference before processing turns both failure modes into a precise,
auditable report of exactly what changed, while still processing
everything that can safely be processed.
