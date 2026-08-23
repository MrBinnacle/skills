---
name: bash-cwd-drift-false-clean-grep
description: |
  Catch the false all-clear produced when the Bash tool's persistent working
  directory drifts and a verification grep silently searches the wrong tree.
  Use when: (1) a `grep -rn` over known-present strings returns nothing and you
  are about to conclude the repo is clean, (2) an earlier `cd subdir/` in the
  session was followed by a repo-root-relative command, (3) a "no matches"
  result is being used as evidence rather than as an absence of evidence,
  (4) a stale-claim sweep or a pre-commit consistency check returns empty,
  (5) `ls`/`cat` on a root file reports No such file or directory. The Bash
  tool persists cwd across calls, so a grep with relative paths reports zero
  matches instead of erroring, and zero matches reads exactly like a passing
  check. Includes the guard that turns a silent miss into a loud one.
author: Claude Code
version: 1.0.0
date: 2026-08-18
---

# Bash cwd drift turns a verification grep into a false all-clear

## Problem

The Bash tool's working directory **persists between calls**. A `cd subdir/` earlier in the
session is still in effect many calls later. When a verification command uses paths relative
to the repo root, it searches a tree that does not contain them.

For most commands this is loud — `cat`, `ls`, `git add` error out. **For `grep` it is
silent in the worst possible direction**: multi-path `grep` reports "no matches" for files it
could not open, and no matches is exactly what a clean repository looks like.

The result is a verification step that returns *pass* without having examined anything.

## Context / Trigger conditions

- A `grep -rn` for strings you know are present returns nothing.
- Earlier in the session a command ran `cd <subdir>` — often to run a test suite or a build.
- You are running a stale-claim sweep, a pre-commit consistency check, or a
  "did I miss this string anywhere else" pass, and it comes back empty.
- A subsequent `ls` or `cat` on a repo-root file says `No such file or directory`.
- The empty result is about to be reported to a user as "verified: nothing else to fix."

## Root cause

Two behaviours compose:

1. **cwd persists across Bash tool calls.** Shell variables and functions do not; the
   directory does.
2. **`grep` with several path arguments treats an unopenable path as a non-match** in the
   aggregate exit status when other paths matched — and when *none* opened, it prints its
   errors and still produces the empty result you were looking for. Pipe through `head` or
   redirect stderr and the errors disappear entirely, leaving a clean-looking empty output.

Neither is a bug. Together they turn "I could not look" into "I looked and found nothing."

## Solution

**Prefix every verification command with an absolute `cd`.** Not the first one — every one.

```sh
cd /c/Users/you/projects/repo && grep -rn "pattern" CONTEXT.md docs/ README.md
```

Or use absolute paths in the command itself. Either works; picking one and applying it
consistently is what matters, because the trap fires on the call you did not think needed it.

**Make an empty result prove it looked.** Add a positive control — a string you know is
present — to the same command:

```sh
cd "$REPO" && grep -rn "pattern-under-test\|KNOWN-PRESENT-STRING" <paths>
```

If the known string does not come back, the search did not happen, and the empty result for
the real pattern means nothing.

**Never pipe a verification grep straight into `head` without reading stderr.** The path
errors are the only signal that the search was hollow.

## Verification

Confirm the drift directly rather than inferring it:

```sh
pwd
```

Then re-run the grep from the repo root and compare. A result that changes between the two
is a caught false clean. A result that is empty from both is a real negative.

## Example

2026-08-18. A session was checking whether a corrected claim still stood anywhere else in a
repository — a documented recurring failure in that project, where the same false claim had
previously stood in three surfaces at once.

```sh
grep -rn "#18\|#19\|#24" CLAUDE.md README.md CONTEXT.md PRODUCT.md docs/ .claude/state/checkpoint.md
# (no output)
```

That is a clean sweep, and it was about to be reported as one. But `CONTEXT.md` had been
edited to mention `#19` four calls earlier — the result was impossible.

`pwd` returned the `slice/` subdirectory. A `cd slice` from a test run, six calls back, was
still in effect. Re-run from the repo root, the same grep returned five matches, two of
which were the corrections just made and one of which needed inspection.

The specific damage this avoided: the sweep existed *because* that repository had shipped
the same stale claim across multiple files five separate times. A false clean would have
been the sixth, produced by the very check designed to prevent it.

## Notes

- **The cost is asymmetric.** A cwd error on a write is loud and gets fixed in seconds. A cwd
  error on a read is silent and gets reported as a passing check.
- **This is the same shape as any tool whose failure mode is an empty result**: a blocked
  crawler that returns no results, a depth-limited `find`, a search over an index that does
  not include the target. In all of them, *absence of evidence* is being rendered as
  *evidence of absence* by the tool's output format.
- The discipline generalises to one line: **an empty result is only evidence if the search
  could have found the thing.** Prove the search could, then trust the emptiness.
- Related: `hidden-and-plugin-skill-reachability` covers the depth-limited-`find` instance of
  the same fallacy.

## References

Observed directly, 2026-08-18, Windows / Git Bash under Claude Code. The cwd-persistence
behaviour is documented in the Bash tool's own description ("Working directory persists
between calls"); the consequence for verification greps is not, which is why this exists.
