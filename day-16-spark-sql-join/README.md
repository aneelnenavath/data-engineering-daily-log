# Day 16 — Spark SQL Version of Day 15's Join Benchmark

Re-runs Day 15's broadcast-vs-shuffle join comparison, but through Spark
SQL (temp views, plain SQL strings, and the `/*+ BROADCAST() */` SQL hint
syntax) instead of the DataFrame API. Same dataset as Day 15, copied over
directly, so results are directly comparable.

## What's different from Day 15

- `orders.createOrReplaceTempView("orders")` registers a DataFrame under
  a name so it can be queried with plain SQL strings via `spark.sql(...)`,
  instead of chaining DataFrame methods.
- The broadcast hint is written inline in the SQL itself —
  `SELECT /*+ BROADCAST(c) */ ...` — rather than wrapping a DataFrame in
  Python's `broadcast()` function.
- The plan is read via a SQL `EXPLAIN` statement
  (`spark.sql("EXPLAIN ...").show()`), which returns the plan as a
  single-row, single-column result with the whole plan embedded as one
  string (literal `\n` characters inside it), rather than `.explain()`
  printing pretty-formatted lines straight to the console the way Day 15
  did.

## Results

| Strategy | Physical plan operator | Avg. time (3 trials) |
|---|---|---|
| No hint | `SortMergeJoin` | 0.478s |
| `/*+ BROADCAST(c) */` | `BroadcastHashJoin` | 0.256s |

Broadcast was 1.86x faster. Both returned exactly 50,000 rows.

## Two real observations

1. **The absolute timings differ from Day 15's (1.183s/0.343s/3.45x
   yesterday vs. 0.478s/0.256s/1.86x today) despite identical data and an
   identical join.** That's normal run-to-run variance between separate
   process launches (JVM warm-up, OS file caching) - not a real
   difference between the SQL and DataFrame APIs. Only the *relative*
   comparison within a single run (broadcast beats sort-merge) is a
   trustworthy claim here; the precise speedup ratio isn't something to
   over-interpret across separate benchmark runs.
2. **The physical plan for each strategy is identical to Day 15's -
   `SortMergeJoin` and `BroadcastHashJoin` - despite the query being
   written as SQL strings instead of DataFrame method calls.** Spark SQL
   and the DataFrame API are two front-ends over the same Catalyst
   optimizer and execution engine, so an equivalent join compiles down to
   the same physical plan regardless of which syntax expressed it. The
   choice between them is a readability/workflow preference, not a
   performance one.
