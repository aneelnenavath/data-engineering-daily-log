# Day 51 — Structured Logging for Data Pipelines

## Topic

Every script in this project so far has used print() for its own output, which is fine while
watching it run interactively but falls apart the moment someone has to investigate a failure
after the fact, from a saved log file rather than a live terminal. Today builds and proves
exactly why - and fixes it with Python's logging module configured to emit structured JSON.

## Setup

`orders_batch.csv` holds 20 order rows, 4 of them deliberately invalid: a non-numeric amount
(row 5), a negative amount (row 11), an invalid status (row 14), and a missing customer_id
(row 17). Both scripts below run the exact same validation logic against this exact same data -
the only thing that changes between them is how the output is logged.

## Proof 1 — print() logging makes failures invisible to search

`process_with_print.py` validates all 20 rows and correctly identifies all 4 bad ones,
printing a line like "Problem with row 5: amount is not a number ('abc')" for each. Redirected
to a file (`run.log`) and searched the standard way anyone would start investigating a job's
logs:

    grep "ERROR" run.log

Result: nothing. Zero matches. The job genuinely had 4 real failures, but because print() has
no enforced concept of a log level or a consistent vocabulary, there is no reliable way to
search for them - someone investigating this log would wrongly conclude the run was completely
clean.

## Proof 2 — structured JSON logging makes failures precisely searchable

`process_with_logging.py` runs identical validation logic, but through Python's logging module
with a custom JSON formatter - every line is a single JSON object with a timestamp, an actual
`level` field (INFO or ERROR), a job name, a message, and extra context fields (row_id, reason)
attached per failure. Running the same search:

    grep "ERROR" run_structured.log

Result: exactly the 4 real failures, each with its row_id and the precise reason visible right
in the match - amount_not_numeric:abc, negative_amount:-50.0, invalid_status:unknown_status,
missing_customer_id.

## Proof 3 — real field-level parsing, not just text matching

Went a level further with `jq`, a real JSON parser, rather than relying on grep matching
substrings:

    jq -r 'select(.level=="ERROR") | "\(.row_id)\t\(.reason)"' run_structured.log

Result: a clean, exact table of row_id and reason for every failure - genuine structured field
extraction. This is something the print()-based log cannot do reliably at all, since nothing in
it was ever a real, addressable field - only string fragments.

## What to remember going forward

print() output looks identical, in the terminal, to structured logging - both show up as lines
of text while a script runs. The difference only becomes visible once something goes wrong and
someone has to search a saved log after the fact, which is exactly when it matters most. A log
line with an enforced level and real fields can be filtered and parsed with total precision; a
log line that is just a human-readable sentence cannot be, no matter how descriptive the
sentence is. The fix costs very little - a formatter and a few extra keyword arguments - and
the difference it makes during an actual incident is the difference between finding every
failure in one command and manually reading the whole log hoping nothing was missed.
