#!/bin/sh
# Check an installed skill folder on YOUR machine against this collection's
# published commitment: every file is .md, .txt, .py or .json, plus compiled
# Python that has its readable source sitting beside it.
#
# WHY THIS EXISTS AS SOMETHING YOU RUN
#   The CI check in this repository is code in the repository it guards, run by
#   CI configured in that repository. It buys resistance to forgetting; it buys
#   nothing against intent, and its green tick is invisible to you. This is the
#   same check, aimed at the copy you actually have. Do not take our word for it.
#
#   The two find commands below are the whole check. Read them and type them
#   yourself if you would rather not run a script you downloaded -- that is the
#   point, and the published SECURITY.md carries the same two commands.
#
# USAGE
#   ./check-installed-skills.sh ~/.claude/skills/im-up
#
#   Exits 0 and prints PASS when the commitment holds.
#   Exits 1 and lists every unexpected file when it does not.
set -eu

TARGET=${1:-}
if [ -z "$TARGET" ]; then
    echo "usage: check-installed-skills.sh <path to an installed skill folder>" >&2
    echo "example: check-installed-skills.sh ~/.claude/skills/im-up" >&2
    exit 2
fi
if [ ! -d "$TARGET" ]; then
    echo "REJECTED: not a directory: $TARGET" >&2
    exit 2
fi

unexpected_files() {
# 1. Nothing but the declared formats. Compiled Python is step 2.
find -L "$TARGET" -type f \
  ! -name '*.md' ! -name '*.txt' ! -name '*.py' ! -name '*.json' \
  ! \( -path '*/__pycache__/*.pyc' ! -path '*/__pycache__/*/*' \)

# 2. Every compiled file sits directly in __pycache__ with its source beside it.
find -L "$TARGET" -path '*/__pycache__/*.pyc' ! -path '*/__pycache__/*/*' -exec sh -c \
  'for f; do d=${f%/__pycache__/*}; b=${f##*/}; [ -f "$d/${b%%.*}.py" ] || echo "$f"; done' _ {} +

# Both print nothing when the commitment holds on your machine.
# -L matters: installs are symlinked, and find without it skips them.
}

found=$(unexpected_files)

if [ -n "$found" ]; then
    echo "REJECTED: files in $TARGET that the commitment does not cover:" >&2
    echo "$found" | sed 's/^/  - /' >&2
    echo "" >&2
    echo "Compiled Python (__pycache__/*.pyc) is expected when a skill has run," >&2
    echo "and is listed here only when the .py it came from is missing." >&2
    exit 1
fi

echo "PASS: every file in $TARGET is .md, .txt, .py or .json, or compiled Python with its source beside it"
