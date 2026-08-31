---
name: container-green-host-red-detached-child-holds-tempdir
description: |
  A hook or script self-test passes in a Linux CI/factory container and fails on the
  Windows host where the hook actually runs. Use when: (1) a Python self-test aborts with
  `PermissionError: [WinError 32] The process cannot access the file because it is being
  used by another process` at `TemporaryDirectory` cleanup, after the early checks passed;
  (2) `ignore_cleanup_errors=True` on the obvious tempdir does NOT clear it; (3) the code
  under test launches a detached child (`subprocess.Popen(..., start_new_session=True)`)
  and a test runs it with `cwd=<tempdir>`; (4) a Windows-only `endswith(".claude/state/x")`
  path assertion fails on backslashes. The child inherited the tempdir as its cwd and holds
  it for its lifetime; the fix is in the product (pin the child's cwd), not the test.
author: Claude Code
version: 1.0.0
date: 2026-08-29
---

# Container-green, host-red: a detached child holds the test's tempdir

## Problem

A factory/CI gate runs a hook's self-test inside a Linux container and reports green. The
hook is then wired into `settings.json` (and its self-test into the session receiver
checks) on a Windows host. On that host the same suite exits 1 part-way through: the first
block of checks prints `ok`, then a `PermissionError [WinError 32]` traceback from
`tempfile.TemporaryDirectory.__exit__`, and every later check never runs. The receiver
now rejects the next session packet on a "trusted check" that never reached its second
case.

Observed 2026-08-29 in a private steering repository (board-drift sweep hooks): 19/19 gate checks
green in-container; on the host 15/57, then abort.

## Context / Trigger Conditions

- Windows host; Python 3.12/3.13; suite uses `tempfile.TemporaryDirectory()` per test.
- The code under test launches a long-lived detached child: `subprocess.Popen([...],
  start_new_session=True)` with no `cwd=` argument.
- Some test runs the parent with `subprocess.run(..., cwd=td)` where `td` is the tempdir.
- Symptom order: early `ok` lines → `WinError 32 ... being used by another process:
  'C:\\Users\\...\\Temp\\tmpXXXX'` naming the **directory**, not a file → suite aborts.
- Red herring: the first tempdir you suspect (the one whose test polls for an output
  file) is not the holder. Adding `ignore_cleanup_errors=True` there changes nothing.

## Solution

1. **Find the holder by the frame, not the message.** The traceback's `in test_...` frame
   names the test whose tempdir is locked. Look for `cwd=td` in that test.
2. **Fix the product, not the test:** the detached launcher pins its child's cwd to the
   project root (or another directory that outlives the test):

   ```python
   root = os.environ.get("CLAUDE_PROJECT_DIR")
   if not root or not os.path.isdir(root):
       root = os.path.dirname(os.path.dirname(_HERE))
   subprocess.Popen([sys.executable, _DETACHED], cwd=root,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True)
   ```

   An inherited cwd is a latent defect in production too: the child keeps whatever
   directory the hook was launched from locked for its lifetime.
3. **Publish outputs atomically** in the child: write `<path>.tmp`, then `os.replace(tmp,
   path)`. A poller that keys on `path.exists()` then never sees a half-written or
   still-open file, which is the second Windows-only lock.
4. **Compare path parts, not joined suffixes**: `Path(p).parts[-3:] == (".claude",
   "state", "x.json")` instead of `p.endswith(".claude/state/x.json")`.
5. On the test whose child may still be exiting at block end, `TemporaryDirectory(
   ignore_cleanup_errors=True)` is a legitimate belt-and-braces, but it is not the fix.

## Verification

Run the suite on the host: exit 0 and the full check count (here `all green (57 checks)`).
Before the fix: exit 1, the early block only, `WinError 32` naming a temp **directory**.
Confirm with `grep -n "cwd=td"` that the located test is the one in the traceback frame.

## Example

Three defects survived a 19-check container gate and were found only by running the
self-test on the host before merging: inherited cwd (abort), non-atomic cache write
(race), slash-joined path assertion (backslashes). Fixed forward on the factory branch
(`945c684`), re-run 57/57, then merged. Rule adopted in the project: a PR that wires a
hook into `settings.json` or a receiver check into `session-boundary.json` gets its
self-test run on the host before merge — the gate is not the host.

## Notes

- Windows refuses `rmdir` on a directory that is any process's cwd; Linux does not, which
  is why the container never sees it.
- `start_new_session=True` is a POSIX `setsid`; on Windows it is ignored, so "detached" is
  weaker there too — the child survives parent exit only because Windows does not kill
  children by default. Measure, do not assume.
- See also: `windows-claude-code-env` (Problem 9, CRLF; cp1252 console encoding) for the
  other Windows-only classes that pass a Linux gate.

## References

- Python `tempfile.TemporaryDirectory(ignore_cleanup_errors=...)` — added in 3.10; it
  swallows the error, it does not release the holder.
- Python `subprocess.Popen` — `cwd` and `start_new_session` semantics per platform.
