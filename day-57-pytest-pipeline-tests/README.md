# Day 57 — Unit Testing Pipeline Logic with pytest

## What this demonstrates

Every day of this project so far has been verified the same way: run a
script, read the printed output, and manually confirm it looks right.
That works for a one-off proof, but it doesn't scale - nobody re-reads
every line of console output every time a small change is made to
production code, which is exactly how a subtle regression slips through
unnoticed. Today's problem: build an automated test suite that catches
a regression immediately and precisely, with an exact expected-vs-actual
diff, instead of relying on a human to notice.

## The code under test

transform.py's normalize_order() takes a raw order record, strips and
lowercases its status, rejects anything outside the allowed status set,
converts amount to a float, rejects a negative amount, and returns a
clean record including a tax-inclusive total computed via a TAX_RATE
constant.

## The test suite

test_transform.py covers the happy path, whitespace/case handling,
string-to-float conversion, the tax calculation itself, a genuine
boundary case (a zero-amount order should be allowed, producing zero
tax), and both validation failures (invalid status, negative amount) via
pytest.raises. Run against the correct implementation:

    7 passed in 0.44s

## Proof - a subtle one-character bug is caught immediately and precisely

Changed one line in the tax calculation:

    "amount_with_tax": round(amount * TAX_RATE, 2)
        became
    "amount_with_tax": round(amount + TAX_RATE, 2)

A single character change - multiplication to addition - that still
runs without error and still produces a plausible-looking number on a
quick glance. Re-running the identical test suite:

    FAILED test_normalizes_a_clean_record - amount_with_tax: 51.2 != 60.0
    FAILED test_computes_tax_inclusive_total_correctly - assert 101.2 == 120.0
    FAILED test_zero_amount_is_allowed - assert 1.2 == 0.0
    3 failed, 4 passed in 0.77s

3 of 7 tests failed immediately, each with an exact diff pinpointing the
broken field - nothing vague, no "something looks wrong." The other 4
tests (status handling, type coercion, both validation checks) kept
passing correctly, since that code was never touched. The
test_zero_amount_is_allowed failure is the sharpest signal of all:
asserting 1.2 == 0.0 means a supposedly free order came out with a tax
charge of exactly TAX_RATE itself - a dead giveaway that addition had
replaced multiplication, caught in under a second by re-running a
command that already existed, with zero manual inspection required.

Reverted the change and confirmed the suite is green again: 7 passed.

## Why this matters

Manual verification - running a script and reading its output - doesn't
survive code changing over time; nobody re-checks every prior behavior
by eye every time a line changes. An automated test suite turns that
same verification into something that re-runs in under a second and
reports exactly what broke, down to the specific field and the specific
expected value, the moment a regression is introduced - not whenever
someone happens to notice.
