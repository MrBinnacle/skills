# PR body — issue #296: refresh path for demand rows

## Decision

Option A chosen: build a refresh path. A script reads the usage log and rewrites each
card's `Dispatches recorded` row with the current count and measurement date.

**Reason:** Option B (hand-written rows) leaves them to rot — a row written once and never
moved is a dated claim that stopped being checked. `AGENTS.md:128` already requires a
factual claim to be dated and the check recorded where it is relied on; B satisfies the
letter while leaving 19 cards carrying figures nobody re-measures.

**Coupling inverted from the ticket's option A:** the script ships in the public repository
but the log lives in the private research repo. The log path is an input
(`SKILL_USAGE_LOG` env var), not a hard-coded assumption. Absence is a normal outcome
rather than a crash.

## What was built

### `scripts/refresh_dispatch_counts.py`

Reads the JSONL usage log, computes per-card dispatch counts from baseline + delta
records (skipping anomaly records), and rewrites every published card's `Dispatches
recorded` row in `EVIDENCE.md`. The date written is the `ts` of the newest record
consumed, not today's date.

Key behaviours:
- Reads log path from `SKILL_USAGE_LOG` env var; defaults to the sibling private
  research checkout's state-dir usage log relative to repo root.
- **Missing log:** prints `SKIP: usage log not found at <path>`, changes no card, exits 0.
- **Empty log:** rewrites every nonzero row to zero. Already-zero rows keep their
  card-specific diagnosis (hook-unobservable prose on `pull-rebase` /
  `stale-deploy`) and only move the measurement date — a full replace would erase
  the harvest pass's unobservable-vs-insurance discriminator.
- **Log with data:** writes the count and measurement date per card.
- Only matches bare skill names, not `plugin:skill` form — those are different install
  paths and adding them would overstate demand. `pluginUsage` is never read.

### `scripts/test_refresh_dispatch_counts.py`

11 tests across three control classes plus edge cases. All pass.

### `AGENTS.md` harvest step

Step 2 of "The pass" now names the script and says when to run it.

## Acceptance criteria

### Criterion 1: Outcome chosen and recorded

Option A, recorded in the ticket. Done before this PR.

### Criterion 2: Script exists, harvest step names it, controls ran

**What was built:** `scripts/refresh_dispatch_counts.py` and
`scripts/test_refresh_dispatch_counts.py`. AGENTS.md step 2 now contains a "Refresh
dispatch rows" paragraph naming the script.

**Tests that pin it:**

| Control | Test | Assertion |
|---|---|---|
| Control 1: fixture log → known row | `TestControl1FixtureLog::test_nonzero_count` | Log with `im-up: 42` produces a row containing `42 dispatches` and `measured 2026-09-12`. |
| Control 1: baseline + delta | `TestControl1FixtureLog::test_baseline_plus_delta` | Baseline 10 + delta 5 → `15 dispatches`. |
| Control 1: absent skill → zero | `TestControl1FixtureLog::test_absent_skill_gets_zero` | Log names `vacuous-check` only; `im-up` gets `No recorded dispatch`. |
| Control 1: plugin key ignored | `TestControl1FixtureLog::test_plugin_key_not_counted` | `plugin:im-up: 99` does not add to bare `im-up` count. |
| Control 1: anomaly skipped | `TestControl1FixtureLog::test_anomaly_records_skipped` | Baseline 10 + anomaly + delta 3 → 13, not 10 or 23. |
| Control 2: empty log → zero | `TestControl2EmptyLog::test_empty_log_writes_zero` | Empty log rewrites every card to `No recorded dispatch`; nonzero originals change; output is `PASS` not `SKIP`. |
| Control 2: unobservable prose kept | `TestControl2EmptyLog::test_empty_log_preserves_unobservable_diagnosis` | `pull-rebase` and `stale-deploy` still say `this counter cannot see` after an empty-log rewrite. |
| Control 3: missing log → no change | `TestControl3MissingLog::test_missing_log_no_change` | Missing log leaves every EVIDENCE.md byte-identical; output is `SKIP` not `PASS`. |
| Control 3: skip message | `TestControl3MissingLog::test_skip_message_names_path` | Output contains `SKIP` and `usage log not found`. |

**Observed:** All 13 tests pass. The existing `validate_card_files.py` gate remains green
(published cards all carry SKILL.md/gotchas.md/EVIDENCE.md; every EVIDENCE.md states
the three contract rows).

### Additional edge cases

| Test | What it pins |
|---|---|
| `test_plugin_usage_not_counted` | `pluginUsage` figures (e.g. 17262) never appear in a demand row. |
| `test_multiple_skills_in_log` | Multiple skills in one log are all rewritten correctly. |
| `test_date_from_newest_record` | Date comes from the newest record's `ts`, not today. |
| `test_row_passes_validator_format` | Rewritten row satisfies `validate_card_files.py` dispatch checks (no `must open with a nonzero integer` or `states no 'measured <date>'` errors). |
