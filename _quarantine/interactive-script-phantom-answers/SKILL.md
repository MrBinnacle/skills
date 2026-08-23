---
name: interactive-script-phantom-answers
description: |
  A prompting script run without a TTY records fabricated answers instead of failing.
  Use when: (1) an interactive bash/python script "completed" but wrote empty or default
  values, (2) a wizard's summary says "wrote N values" yet the output file is blank,
  (3) `read -r` / `input()` returns instantly with no visible typing, (4) a y/N `confirm`
  resolved to its default that nobody chose, (5) you are about to tell a user to run an
  interactive script through an AI harness, a pipe, CI, or an editor "run" button.
  Covers the guard pattern for any script whose output becomes evidence.
author: Claude Code
version: 1.0.0
date: 2026-08-17
---

# Interactive Scripts Record Phantom Answers Without a TTY

## Problem

`read` returns EOF immediately when stdin is not a terminal. It does not error. A prompting
script therefore runs to completion, prints a cheerful summary, and writes a full set of
values that **nobody supplied**.

Empty strings are the mild case — they are at least visibly empty. The dangerous case is a
**defaulted choice**. `confirm() { read -r reply; [[ "$reply" =~ ^[Yy] ]]; }` resolves to
*no* on EOF. In the output file that `no` is byte-identical to a `no` a human typed.

Measured instance, 2026-08-17: an 8-stage provisioning wizard was run through an AI harness.
All ten values were written empty and one confirm produced `REVOCATION_SUPPORTED=no`. That
flag was the answer to the single most consequential question in the setup, and a documented
plan said a `no` there would narrow a merged architecture decision. **A fabricated answer was
one step from changing an ADR.** It was caught by inspecting the output file, not by any
guard — there was none.

## Context / Trigger Conditions

- A wizard or setup script "succeeded" but its `.env` / config / report is empty or default.
- The transcript shows two prompts printed on the same line with no input between them —
  the signature of back-to-back EOF reads.
- A summary line like `wrote 10 value(s)` alongside a file whose values are all blank.
- You are about to suggest running an interactive script via an AI tool, `cmd | script`,
  `script < /dev/null`, CI, cron, or an IDE run button.
- Any script whose output is later read as **evidence** — a fixture setup, an audit answer,
  a benchmark result, a survey capture.

## Solution

Three guards, in order of importance. All belong in the script, not in the instructions —
instructions are not enforcement.

**1. Refuse to run without a terminal, but try `/dev/tty` first.**

```bash
# Editors and some wrappers redirect stdin while a human is still watching.
# Attach to the terminal directly before giving up.
if [[ ! -t 0 && -r /dev/tty ]]; then exec < /dev/tty || true; fi

if [[ ! -t 0 ]]; then
  echo "stdin is not a terminal — refusing to run. Every prompt would read EOF" >&2
  echo "and record an empty value silently. Run this in a real terminal." >&2
  exit 1
fi
```

A bare `[[ -t 0 ]] || exit` is too strict and will be worked around. The `/dev/tty` fallback
is what makes the guard survive contact with real terminals.

**2. Loop on required values instead of accepting empty.**

```bash
need() { local k=$1 p=$2
  while :; do ask "$k" "$p"; [[ -n "${!k}" ]] && return 0
    echo "  required — this value is written to the output file." >&2
  done
}
```

**3. Give consequential yes/no questions no default at all.**

```bash
must_answer() { local r
  while :; do printf '  %s [y/n] ' "$1"
    read -r r || { echo "stdin closed mid-question — no answer recorded." >&2; exit 1; }
    case "$r" in [Yy]*) return 0;; [Nn]*) return 1;; *) echo "  type y or n";; esac
  done
}
```

`[y/N]` is fine for "continue?". It is **not** fine for anything recorded as a finding. A
default that reaches a state file is indistinguishable from an answer.

## Verification

```bash
bash script.sh < /dev/null; echo "exit=$?"   # expect non-zero
ls output.env                                 # expect: does not exist
```

Then run it for real and confirm values are non-empty. Both halves matter: a guard that
blocks the harness but also blocks the human is a regression.

## Notes

- **Fail closed on the guard, fail open on everything else.** Refusing to run costs a
  re-run. Recording a phantom answer costs a wrong decision made from it.
- **Hidden input hides corruption as well as secrets.** If a prompt reads a credential with
  `read -rs`, you cannot see what arrived. Prefer visible input plus a validity check —
  see `windows-claude-code-env` for the Git Bash Ctrl-V paste-corruption case.
- **Verify captured credentials before writing them.** One read-only API call at capture
  time turns a silent, much-later failure into an immediate, local one.
- Detection beats prevention only once. After the first phantom answer, add the guard —
  the same script will be run the same wrong way again.
- Same failure shape in Python: `input()` raises `EOFError`, which a broad
  `except Exception: pass` converts into exactly this bug.

## See also

- `windows-claude-code-env` — hidden-input paste corruption on Git Bash
- `append-only-evidence-design` — when the output is an evidence store
