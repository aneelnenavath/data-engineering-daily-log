# Day 49 — Retry Logic with Exponential Backoff

## Topic

Building on Day 44's API ingestion work, today tackles a different and very commonly asked
reliability question: what happens when an external dependency fails intermittently - not
because of a bug, but because of a network blip, a timeout, or a brief rate limit? Built and
proved both the naive, wrong answer and the correct one (exponential backoff with jitter).

## Setup

`flaky_api.py` simulates a real API that fails deterministically on its first 4 calls and
succeeds from the 5th call onward - a realistic stand-in for a transient blip that clears on
its own after a few seconds. It's deterministic rather than random so the proof is
reproducible every time it's run, and it logs a timestamp for every call so the actual timing
behaviour of each retry strategy can be inspected directly, not just the final outcome.

## Proof 1 — naive immediate retry fails, and fails badly

`naive_retry.py` retries up to 3 times with no delay between attempts - a common first
instinct for "just try again." Result:

    Attempt 1: FAILED
    Attempt 2: FAILED
    Attempt 3: FAILED
    Gave up after 3 attempts. The job has FAILED.

    Call timing log:
      call #1  +0.0000s  FAILED
      call #2  +0.0000s  FAILED
      call #3  +0.0000s  FAILED

All three attempts fired within the same instant - zero delay between them, hammering the
dependency with no breathing room - and the job gave up completely, even though the API would
have succeeded on the very next call (call #4 still fails, call #5 succeeds). A real flaky
dependency given no time to recover, hit three times in under a millisecond, is unlikely to
actually get healthier because of that pattern either.

## Proof 2 — exponential backoff with jitter succeeds

`backoff_retry.py` retries up to 5 times, doubling the delay after each failure and adding a
small random jitter on top. Result:

    Attempt 1: FAILED   (waited 0.63s)
    Attempt 2: FAILED   (waited 1.19s)
    Attempt 3: FAILED   (waited 2.18s)
    Attempt 4: FAILED   (waited 4.05s)
    Attempt 5: SUCCESS

    Call timing log:
      call #1  +0.0000s  FAILED
      call #2  +0.6250s  FAILED
      call #3  +1.8120s  FAILED
      call #4  +4.0000s  FAILED
      call #5  +8.0470s  SUCCESS

Two things made the difference, not one: more attempts were allowed (5 instead of 3), and the
growing delay between them gave the simulated transient failure room to actually clear. The
jitter (a small random amount added on top of the doubling delay) matters in a real system too
- without it, many clients retrying the same outage would all retry at exactly the same moment
and hit the dependency with a synchronized burst, which is close to the same hammering problem
the naive retry already caused.

## What to remember going forward

A naive retry loop with no delay doesn't just fail more often than it needs to - it makes the
underlying problem worse, by hitting an already-struggling dependency harder and faster right
when it most needs space to recover. Exponential backoff fixes both halves of that: it gives
the dependency time to recover, and it spaces out attempts from many different clients so they
don't all slam it at once. Both scripts used the exact same simulated failure pattern - the
only thing that changed was the retry strategy around it, which is the clearest way to show the
two approaches aren't a matter of degree, they produce genuinely different outcomes.
