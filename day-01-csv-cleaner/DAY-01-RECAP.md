# Day 1 Recap — The Story of One Messy CSV

## The setup

You had 15 rows of fake customer signups, and they were broken in four specific,
realistic ways: inconsistent casing (`London` vs `LONDON` vs `london`), stray
whitespace (`' Manchester '` with invisible padding), missing required fields (two
customers had no email), and duplicate rows recorded under different IDs. Nothing
exotic — this is what real data actually looks like on a Tuesday.

## Meeting the dataframe

The first move was `pd.read_csv("messy_customers.csv", dtype=str)`. That one line
pulled the whole CSV into memory as a **dataframe** — pandas' name for a table:
rows and columns, indexable, filterable, transformable. If PySpark is already in
your head from your coursework, this will feel familiar, because it's the same
mental model. The difference that actually matters — and comes up constantly in
interviews — is *when* the work happens. Pandas is eager: `pd.read_csv(...)` reads
the file immediately, and the whole thing sits in your machine's RAM. Spark is
lazy: nothing runs until you call an action like `.show()` or `.collect()`, and
when it does run, the work can be split across a whole cluster. Same shape of
tool, very different engine underneath.

## The NaN detour

Empty cells didn't show up as blank strings — they showed up as `NaN`. That name is
a historical accident: `NaN` stands for "Not a Number," borrowed from numeric
computing standards, and pandas repurposed it as a universal "missing" marker even
for text columns, because the library it's built on (NumPy) didn't originally have
anything better. It behaves a lot like SQL's `NULL` — you can't test for it with
`==` (`NaN == NaN` is `False`, just like `NULL = NULL` is `NULL`, not `TRUE`) — you
need a dedicated check instead: `.isna()` in pandas, `IS NULL` in SQL. Same trap,
two languages.

## Making pandas show you the mess, instead of hunting for it yourself

Three commands did the real investigative work:

- `df['city'].unique()` — surfaced every distinct value in a column. Instead of
  scanning 15 rows by eye, one line showed you there were 13 different spellings
  of 5 real cities.
- `df.isna().sum()` — `.isna()` turns every cell into True/False, `.sum()` adds up
  the Trues per column (Python counts `True` as `1`). One line, a full missing-data
  report.
- `df.duplicated()` / `df.duplicated(subset=...)` — flagged repeated rows. The
  first version compared *every* column, including `customer_id`, and found
  nothing — because two rows describing the same customer had different surrogate
  IDs. Excluding `customer_id` from the comparison (`subset=compare_cols`) is what
  actually caught it. A machine can't tell you which column is "identity" and
  which is "business data" — that's a judgment call, and it's the kind of decision
  an interviewer wants to hear you explain.

All three of those follow the same pattern, called **boolean indexing**: build a
column of True/False values, then wrap it in `df[...]` to pull out only the rows
where it's True. You'll use this pattern constantly — it's arguably the single
most important pandas idiom.

## The order-of-operations lesson

This was the real "aha" of the day. Running `.duplicated()` before normalizing
text caught 2 of the 3 duplicates — Karen Wu's second row was hiding behind
`Glasgow` vs `glasgow`, invisible to an exact string comparison. Only after
running `.str.strip()`, `.str.title()`, and `.str.lower()` across the messy
columns did re-running the duplicate check catch all 3. The lesson generalizes
far beyond this exercise: **cleaning steps aren't independent — their order
changes the result.** Normalize before you deduplicate, or your dedup logic
silently misses things.

## The four cleaning primitives

By the end, you'd used exactly four pandas operations to go from 15 messy rows to
10 clean ones:

1. `.str.strip()` / `.str.title()` / `.str.lower()` — text normalization, applied
   column-wide via the `.str` accessor.
2. Boolean masking + `~` (the NOT operator) — `df[~mask]` to keep everything
   *except* the rows a mask flags, used to drop rows missing required fields.
3. `.fillna('unknown')` — filling recoverable gaps rather than losing whole rows.
4. `.drop_duplicates(subset=..., keep='first')` — the "do it" version of
   `.duplicated()`, actually removing the flagged rows instead of just showing
   them.

That's the entire cleaning pipeline. `clean_csv.py` just packages these same four
ideas into a reusable script with logging — nothing in that file is a new concept
you haven't now typed yourself.

## The git/GitHub mechanics

Separate from the pandas work, today also covered: creating folders from a
terminal (`mkdir`, `cd`), writing files directly from the command line with
`cat > file << 'EOF'`, the difference between local and `--global` git config
(local config needs an initialized repo to write into; global applies everywhere,
which is why it fixed the "not in a git directory" error), and the standard
five-command sequence to turn a folder into a pushed GitHub repo:
`git init` -> `git add .` -> `git commit -m "..."` -> `git branch -M main` ->
`git remote add origin <url>` -> `git push -u origin main`. You'll run a version of
this — usually just `add`/`commit`/`push`, since `init` and `remote` only happen
once — every single day for the rest of this plan.

## What to remember going into Day 2

Tomorrow's task is a log file parser using regex — different domain, but the same
underlying skill: look at messy raw input, decide what "correct" means, and write
code that gets you there deliberately, one verified step at a time, rather than
guessing.
