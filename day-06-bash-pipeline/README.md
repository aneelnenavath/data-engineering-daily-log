# Day 6 — Bash Pipeline (Days 1 + 2 Chained)

## What this is

A Bash script (pipeline.sh) that runs Day 1's CSV cleaner and Day 2's log
parser in sequence, with command-line flags to skip either step, proper
exit-code handling, and timestamped logging to pipeline.log.

## Why exit codes matter here

Every command leaves behind an exit code in $? — 0 for success, non-zero
for failure. run_step() captures that code immediately after each Python
script runs (it has to happen right away, since $? gets overwritten by the
next command), logs whether the step succeeded or failed, and on failure
calls exit with that same code — stopping the pipeline immediately rather
than continuing on to the next step with broken or missing input.

## Arguments

--skip-clean   skip Day 1's CSV cleaner
--skip-parse   skip Day 2's log parser
(no flags)     run both steps

Verified this actually works, not just accepted silently: running with
--skip-clean produces a log with only the Day 2 step in it, and passing an
unrecognised flag prints an error and exits with code 1, confirmed by
checking $? right after.

## Logging

log() timestamps every message and uses tee -a to both print it to the
screen and append it to pipeline.log, so there's a permanent record of
every pipeline run, not just what scrolled past in the terminal.

## How to run

./pipeline.sh
./pipeline.sh --skip-clean
./pipeline.sh --skip-parse
