# Day 52 — Pydantic Validation

## What this demonstrates

Every pipeline so far in this project has assumed incoming data is already
well-formed. Today's problem: what happens to a batch job when one record
in it is malformed, and how per-record validation at the ingestion
boundary fixes it.

Pydantic (v1.10.12, confirmed installed) is used here for a different
purpose than Great Expectations (Day 43). Great Expectations validates
value distributions across a whole dataset. Pydantic validates the
structure and types of a single record, which is exactly the boundary
where a batch job first touches external data.

## The data

raw_orders.py defines 10 raw order dicts, 4 of them deliberately broken
in different ways:

    row 3 - amount is the string "fifty" instead of a number
    row 5 - amount is -25.00, numeric but semantically invalid
    row 7 - customer_id key is missing entirely
    row 9 - status is "refunded", not in the allowed set

## Proof 1 - unvalidated processing crashes the whole batch

process_without_validation.py loops over all 10 records and blindly does
total_revenue += order["amount"] with no checks at all.

Result: it crashed outright on row 3 with

    TypeError: unsupported operand type(s) for +=: 'float' and 'str'

Only orders 1 and 2 were processed before the crash. Orders 4 through 10
- including 4, 6, 8, and 10, which are all perfectly valid - were never
even reached. One bad record destroyed the entire batch's results.

## Proof 2 - Pydantic validation isolates bad records instead

order_model.py defines an Order model (Pydantic v1 syntax: BaseModel and
validator, not v2's field_validator) with order_id: int, customer_id:
int, amount: float, and status constrained to a Literal of "completed",
"pending", "cancelled". A custom validator additionally rejects any
amount below zero.

process_with_validation.py wraps each record in a try/except
ValidationError block instead of trusting it directly. A record that
fails validation is logged with the exact field and reason, counted as
rejected, and the loop continues to the next record rather than stopping.

Result, running against the identical 10-record dataset:

    Order 1: processed, amount=49.99
    Order 2: processed, amount=120.5
    Order 3: REJECTED
        field=amount reason=value is not a valid float
    Order 4: processed, amount=89.25
    Order 5: REJECTED
        field=amount reason=amount must be non-negative
    Order 6: processed, amount=33.1
    Order 7: REJECTED
        field=customer_id reason=field required
    Order 8: processed, amount=210.0
    Order 9: REJECTED
        field=status reason=unexpected value; permitted: 'completed', 'pending', 'cancelled'
    Order 10: processed, amount=18.6

    Done. Processed: 6, Rejected: 4, Total revenue: 521.44

All 4 deliberately broken records were caught, each with a precise and
auditable reason tied to the exact field that failed. All 6 valid
records were processed despite the bad ones being present anywhere in
the batch. 521.44 is exactly the sum of the 6 valid amounts
(49.99+120.50+89.25+33.10+210.00+18.60), confirming nothing invalid
leaked into the total.

## Why this matters

A single malformed record should never be allowed to take down an
entire batch job's worth of otherwise-good data. Validating structure
and types at the point data enters a pipeline - not after an
unhandled exception already killed the job - turns a total outage into
a small, precisely logged set of rejected records, while everything
valid still gets processed and the revenue total is still correct.
