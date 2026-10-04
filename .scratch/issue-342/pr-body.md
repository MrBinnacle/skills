# #342: release gate refuses in its own words when git is not on PATH

## What is true now

`scripts/release_gate.py` dies with a traceback when `git` is not on PATH. It does not refuse.

Measured 2026-10-02 on a Windows host, by the author of PR #341 and again by its verifier (https://github.com/MrBinnacle/skills/pull/341#issuecomment-5947093679, row 6): running the gate with `--release --root <a seeded tree>` under `PATH=/usr/bin:/bin`, which names no directory on Windows, gives exit 1, empty stdout, and on stderr

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

raised from the gate's `git` probe, before the external spec validator is reached.

The exit code is non-zero, so a release is not passed by accident. The defect is that the reader gets a stack trace instead of the gate's own verdict line naming what it could not check, which is how every other unreadable input in this gate is reported (the `fails closed` cases in `scripts/test_release_gate.py`).

PR #341 fixed the test fixture that used to reach this state by accident and left the gate alone, because the gate's behaviour was outside #272.

## What this change does

When the gate cannot run `git`, it now refuses in its own words: it prints a refusal that names `git` as the missing dependency and which check could no longer run, in the same form as every other fail-closed input, and exits non-zero. No traceback reaches the reader on that path.

Out of scope, unchanged: making the gate work without `git`. A missing `git` is still fatal to the checks that need it; only the reporting changed.

### Call sites

Reading the gate shows more than one `git` call site can raise `FileNotFoundError`. Each is handled:

| Call site | Check that reports | Refusal text |
|---|---|---|
| `_git_ok` via `gate_clean_tree` | G9 | `G9: git could not be run - the working tree cannot be checked for cleanliness: ...` |
| `_is_git_work_tree` via `gate_spec_conformance` | G6 | `G6: git could not be run - the external spec validator cannot enumerate the published tree: ...` |
| `_git_ok` via `detect_release_ref` | defers to G6/G9 | mode detection cannot prove the ref is ordinary, so release checks run and the check that needs git reports |

The mechanism is one shared helper, `_run_git`, which converts `FileNotFoundError` into a typed `GitUnavailableError`. A missing dependency is not a non-git tree: `_is_git_work_tree` False means "not a git repository", while `GitUnavailableError` means "git could not run at all". Conflating them would turn a missing dependency into a skip. Callers catch the typed error and append a refusal under their own check ID.

When ordinary mode (no `--release`) hits a missing git during release-mode detection, the gate fails closed to release mode. Missing git is not proof the ref is ordinary; treating it as one would skip every release-only check on a host where they cannot run. G6 or G9 then reports the missing dependency in its own words.

### Observed post-fix behaviour

`--release --root <seeded tree>` under a PATH with no `git`:

```
RELEASE GATE: BLOCKED - 1 stale surface(s) at version 1.2.0:
  FAIL  G9: git could not be run - the working tree cannot be checked for cleanliness: git could not be run: [Errno 2] No such file or directory: 'git'
```

exit 1, empty stderr. Single-reason: every everyday check on a seeded tree passes; only G9 needed git on that path.

## Acceptance criteria

### 1. Refusal names `git` and the check; non-zero exit; no traceback

**Built:** `GitUnavailableError` raised from `_run_git`; `gate_clean_tree` (G9) and `gate_spec_conformance` (G6) catch it and append a refusal naming `git` and the check; `main` fails closed when `detect_release_ref` raises, so G6/G9 report.

**Test that pins it:** `case_missing_git_refuses_in_its_own_words` in `scripts/test_release_gate.py`. It runs the gate as a subprocess under `no_git_env()` — an empty PATH directory on POSIX, `PATH=/usr/bin:/bin` on Windows (the measured #342 failure path) — against a seeded lockstep tree with `--release`, and asserts:

- non-zero exit
- refusal text contains `git` and `could not be run`
- refusal text names `G9:`
- `1 stale surface(s)` (single-reason)
- no `Traceback` on stderr

**Observed before the change:** the test went red. `a release run with no git on PATH is refused` passed only because exit was already 1; every assertion about the refusal's text failed, and `no traceback reaches the reader` failed with `Traceback (most recent call last):` on stderr — the exact defect the ticket names.

**Observed after the change:** all five assertions pass. The suite exits 0.

### 2. That case goes red when the handling is removed

**Mutant applied:** `_run_git` rewritten to call `subprocess.run` directly, without the `try`/`except FileNotFoundError` that raises `GitUnavailableError`. The rest of the fix (callers, main) left in place; the typed error simply never fires.

**Named assertion that killed it:** `no traceback reaches the reader` — the mutant's stderr carries the full `FileNotFoundError: [Errno 2] No such file or directory: 'git'` stack trace from `gate_clean_tree` → `_git_ok` → `_run_git`. The text assertions also fail: stdout is empty, so `git`/`could not be run`/`G9:` are absent.

**Suite under the mutant:** exit 1, `FAILED: 6 case(s)` — both new cases, every refusal-text and no-traceback assertion.

**Mutant stderr, verbatim (traced to the gate's git probe):**

```
Traceback (most recent call last):
  File "/home/agent/workspace/scripts/release_gate.py", line 1007, in <module>
    sys.exit(main())
  ...
  File "/home/agent/workspace/scripts/release_gate.py", line 740, in gate_clean_tree
    head_ok, _ = _git_ok(root, ["rev-parse", "--verify", "HEAD"])
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'git'
```

**Restored:** the `try`/`except FileNotFoundError` → `GitUnavailableError` conversion in `_run_git`. Suite green again: 68 contract cases, exit 0.

No formal mutation receipt was written under `docs/assurance/`: the ticket does not name `scripts/mutation_receipt.py --select`, so the mutant and its output are recorded here, as the ticket requires.

### 3. `python scripts/test_release_gate.py` exits 0

**Built:** the suite itself, extended with the two #342 cases above.

**Test that pins it:** the whole suite. After the fix it exits 0 and prints

```
PASS: release gate verified across 68 contract case(s) - seeded trees, the live tree, and the CI wiring - every refusal asserting its own message, never only a non-zero exit.
```

**Windows and CI:** `no_git_env()` is written portably. On POSIX it sets `PATH` to a fresh empty directory. On Windows it sets `PATH=/usr/bin:/bin` — which names no directory, which is the measured #342 failure path — and carries `SYSTEMROOT` through so the child process can start. `python` runs through `sys.executable`'s absolute path and does not need PATH. This container is Linux; the Windows half is written to the measured failure shape and is not executed here. The existing suite already runs on Windows (PR #341, #272); nothing in this change is POSIX-only.

**Live tree:** `python scripts/release_gate.py` with no arguments still exits 0 over this repository (`RELEASE GATE: PASS - surfaces healthy at version 3.0.1`).

## Which test covers which criterion

| Criterion | Test | What it asserts |
|---|---|---|
| 1 (refusal, no traceback) | `case_missing_git_refuses_in_its_own_words` | exit ≠ 0; text names `git` and `G9`; single-reason; no `Traceback` on stderr |
| 1 (mode-detection path handled) | `case_missing_git_also_refuses_the_mode_detection_path` | ordinary-mode run with no git still refuses, names `git` and `G9`; no traceback |
| 2 (mutant goes red) | same two cases under the `_run_git` mutant | `no traceback reaches the reader` fails; suite exits 1 |
| 3 (suite green) | whole of `scripts/test_release_gate.py` | exit 0; 68 contract cases |

## Companion artifacts

- Ticket: issue #342 of MrBinnacle/skills (text as supplied in the agent brief; this container holds no GitHub token, so the issue body was not fetched from the network).
- Measured incident record: PR #341 comment https://github.com/MrBinnacle/skills/pull/341#issuecomment-5947093679, row 6 — cited from the ticket text, not re-fetched.
- Mutation receipt under `docs/assurance/`: does not exist yet — not required by this ticket.
- Changeset: not added. The acceptance criteria are the contract; the brief says adjacent work is out of scope.
- Formal mutation receipt via `scripts/mutation_receipt.py`: not run — the ticket does not name that instrument.

## Scope

Built exactly the acceptance criteria. No adjacent improvements: no attempt to make the gate work without `git`, no changes to existing tests (none were edited, weakened, skipped, or renamed), no changes outside `scripts/release_gate.py`, `scripts/test_release_gate.py`, and this evidence body.
