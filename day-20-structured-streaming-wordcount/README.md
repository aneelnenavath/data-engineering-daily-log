# Day 20 — Structured Streaming Word Count

A Spark Structured Streaming word count reading from a live TCP socket,
built without relying on `nc` (netcat), which isn't reliably available
on Windows/Git Bash.

## The socket source (`stream_source.py`)

Since the classic version of this exercise assumes a second interactive
terminal running `nc -lk 9999`, this instead uses a small Python TCP
server that waits for Spark's socket source to connect, then streams out
8 sentences with a 2-second delay between each - genuinely arriving over
time, which is the actual point of testing a *streaming* word count
rather than a batch one.

## A real Windows/Hadoop checkpoint bug, not a shutdown-timing issue

The first version used Spark's built-in stateful `groupBy("word").count()`,
which relies on Spark's checkpoint-based state store to track running
totals across micro-batches. That failed with
`[CANNOT_WRITE_STATE_STORE.CANNOT_COMMIT]`, caused by an
`InterruptedIOException` inside `RawLocalFileSystem.setPermission()` -
Hadoop's Windows compatibility layer shells out to an external process
to `chmod` a checkpoint temp file, and that subprocess call itself got
interrupted. Tracing the stack confirmed this was happening during real
task execution, not during query shutdown - a genuine Windows/Hadoop
checkpoint-commit compatibility issue, in the same family as Day 14's
`winutils.exe`/`hadoop.dll` problems but one level deeper (a permission
race rather than a missing binary).

Rather than keep debugging Hadoop's internal Windows file-permission
handling, the fix followed the same judgment call as Day 10's Sqoop
workaround: replace the built-in stateful operator with `foreachBatch`
and a plain Python dictionary tracking running word counts across
batches. This sidesteps Spark's internal checkpoint-based state store
entirely, since there's no longer a stateful aggregation operator in the
query plan for it to protect.

## Verification

The final word counts were checked against a manual line-by-line count
of the 8 source sentences - `the: 7`, `fox: 3`, `dog: 3`,
`streaming: 3`, `spark: 2`, `arrives: 2`, and every other word matched
exactly, confirming the streaming aggregation was correct across all 8
micro-batches, not just superficially plausible.
