#!/usr/bin/env bash
# Wrapper script for task verify steps
# Reduces output verbosity for agent consumption
#
# Usage: run-step.sh "Step Name" command [args...]
#
# Behavior:
#   VERBOSE=1: Stream output in real-time (full output)
#   Default:   Show only pass/fail, reveal output on failure

set -uo pipefail

STEP_NAME="$1"
shift

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [[ "${VERBOSE:-}" == "1" ]]; then
    # Verbose mode: stream output directly
    echo "==> $STEP_NAME"
    "$@"
    exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        echo "==> $STEP_NAME passed"
    else
        echo "==> $STEP_NAME FAILED"
    fi
    exit $exit_code
fi

# Quiet mode: capture output, show only on failure
temp_output=$(mktemp)
trap "rm -f '$temp_output'" EXIT

if "$@" > "$temp_output" 2>&1; then
    echo -e "${GREEN}✓${NC} $STEP_NAME"
    exit 0
else
    exit_code=$?
    echo -e "${RED}✗${NC} $STEP_NAME"
    echo ""
    echo "--- Output ---"
    cat "$temp_output"
    echo "--- End ---"
    exit $exit_code
fi
