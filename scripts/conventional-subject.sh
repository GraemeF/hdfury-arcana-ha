#!/usr/bin/env bash
# Checks that a pull request's title is a Conventional Commit subject.
# The repo squash-merges with the title as the subject, so the title is the
# line main keeps. CONTRIBUTING.md states the rule.
#
# Usage: conventional-subject.sh '<subject>'

set -euo pipefail

subject="$1"
max_length=72
types="build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test"
pattern="^($types)(\([a-z0-9_-]+\))?!?: [^ ].*$"

refuse() {
    echo "Refused the subject: $subject" >&2
    echo "$1" >&2
    echo "CONTRIBUTING.md gives the rule for a pull request's title." >&2
    exit 1
}

if [[ ! "$subject" =~ $pattern ]]; then
    refuse "A subject has the form type(scope): description, where type is one of ${types//|/, } and the scope is optional."
fi

if [[ "$subject" == *. ]]; then
    refuse "A subject does not end with a full stop."
fi

if (( ${#subject} > max_length )); then
    refuse "A subject is at most $max_length characters, and this one is ${#subject}."
fi
