#!/usr/bin/env bash
set -uo pipefail

LOG_FILE="pipeline.log"
RUN_CLEAN=true
RUN_PARSE=true

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S')  $1" | tee -a "$LOG_FILE"
}

run_step() {
    local step_name="$1"
    local script_path="$2"

    log "START  $step_name"
    python "$script_path"
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "OK     $step_name"
    else
        log "FAILED $step_name (exit code $exit_code)"
        exit $exit_code
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
        --skip-clean) RUN_CLEAN=false ;;
        --skip-parse) RUN_PARSE=false ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
    shift
done

log "Pipeline started"

if [ "$RUN_CLEAN" = true ]; then
    run_step "Day 1 CSV cleaner" "../day-01-csv-cleaner/clean_csv.py"
fi

if [ "$RUN_PARSE" = true ]; then
    run_step "Day 2 log parser" "../day-02-log-parser/log_parser.py"
fi

log "Pipeline finished successfully"
