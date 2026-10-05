# #354 — Evidence scope row on every published card, checked against the linked receipt

Rework after verifier failure at `0a8fd9d`. This body describes the branch as it now stands at head, not only this run's changes.

## What the branch ships

Every published card's `EVIDENCE.md` carries an `| **Evidence scope** | ... |` row. The card-files validator requires the row. Conformance O5 derives its value from the receipt the card's `Receipt:` clause names under `--harness-root`, including the no-receipt case O5 previously skipped by returning CANNOT-CHECK.

Closed set (skills#353 / R1):

- `UNMEASURED — no receipt.`
- `NOT DEMONSTRATED — receipt verdict <VERDICT>; no effect is shown.`
- `UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).`
- For a KEEP receipt with a `verdict_scope` object, skill-harness's own scope line from `skill_harness/sitegen/render.py::_scope_line`, filled field by field, with the HTML wrapper `<p class="scope-line">…</p>` removed and without HTML escaping:
  - standard: `Shown here: effect on {task_family}, {model}, {delivery}, measured {tested_at}. Not shown: other task families, models, environments, or real-world incidence.`
  - carried-forward (`currentness.state == "CARRIED_FORWARD"` only): `demonstrated on {model}; carried forward to {current_model} under the sentinel rule; not re-validated on {current_model}.`

Field defaults mirror the harness `_string_field`: a missing or non-string field reads as its placeholder (`unknown task family`, `unknown model`, `unknown delivery`, `unknown date`, `current model`). The `verdict_scope` object itself is never printed. SERS receipts carry no `scope_carried_forward` key; carried-forward is decided from `currentness.state` only.

Live tree counts at head (`git rev-parse --short HEAD` = `15804b9`):

- 14 published cards carry the row (`find skills -name SKILL.md | wc -l` → 14; `grep -rl '| \*\*Evidence scope\*\*' skills/*/*/EVIDENCE.md | wc -l` → 14).
- 13 read `UNMEASURED — no receipt.`
- 1 (`skills/engineering/pull-rebase`) reads `NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.`

Quarantine cards and `scripts/fixtures/` are exempt (published-card walk is `skills/<bucket>/<card>` only).

Changeset `.changeset/issue-354-evidence-scope.md` declares **major**, citing ADR 0002 (`docs/adr/0002-a-release-is-a-delivery-event.md`): changing the on-disk shape of a card is a major change.

## Files in the branch diff

`git diff --name-only origin/main...HEAD` at final head (22 files):

- `.changeset/issue-354-evidence-scope.md`
- `.github/workflows/tests.yml`
- `scripts/fixtures/card-missing-evidence-row/skills/engineering/rowless-card/EVIDENCE.md`
- `scripts/fixtures/card-missing-gotchas/skills/engineering/poison-card/EVIDENCE.md`
- `scripts/test_validate_card_files.py`
- `scripts/test_validate_conformance.py`
- `scripts/validate_card_files.py`
- `scripts/validate_conformance.py`
- `skills/engineering/clirunner-env/EVIDENCE.md`
- `skills/engineering/closure-mode/EVIDENCE.md`
- `skills/engineering/halt-as-deliverable/EVIDENCE.md`
- `skills/engineering/im-down/EVIDENCE.md`
- `skills/engineering/im-up/EVIDENCE.md`
- `skills/engineering/mocked-stub/EVIDENCE.md`
- `skills/engineering/pretooluse-prose/EVIDENCE.md`
- `skills/engineering/pull-rebase/EVIDENCE.md`
- `skills/engineering/stale-deploy/EVIDENCE.md`
- `skills/engineering/vacuous-check/EVIDENCE.md`
- `skills/meta/dead-predicate/EVIDENCE.md`
- `skills/orchestration/decision-rights/EVIDENCE.md`
- `skills/orchestration/disposition-schema/EVIDENCE.md`
- `skills/orchestration/subagent-handback/EVIDENCE.md`

`git diff --shortstat origin/main...HEAD` at final head: `22 files changed, 1101 insertions(+), 49 deletions(-)`.

## Acceptance criteria

### 1. Each fixture runs through the validator entry point; red without its clause, green with it; refusal names the card and the row

| Fixture | Satisfies it | Test that pins it | Observed |
|---|---|---|---|
| Published card missing `Evidence scope` | `REQUIRED_EVIDENCE_ROWS` includes `EVIDENCE_SCOPE_ROW` in `scripts/validate_card_files.py` | `case_missing_evidence_scope_row_is_rejected` in `scripts/test_validate_card_files.py` | Before: removing `EVIDENCE_SCOPE_ROW` from `REQUIRED_EVIDENCE_ROWS` left the suite green (suite printed PASS; card without the row was accepted). After: the case is red without the row and green with it; the refusal names `skills/engineering/scopeless-card` and `Evidence scope`. |
| No-receipt card whose row is anything but the `UNMEASURED` sentence | `evidence_scope_breaches` compares the stated row to `expected_evidence_scope([])` | `case_evidence_scope_no_receipt_wrong_sentence_is_fail` in `scripts/test_validate_conformance.py` | Before: a wrong row on a no-receipt card was O5 CANNOT-CHECK (scope was never checked without `--harness-root`). After: O5 is FAIL; detail names the card, `Evidence scope`, and both sentences. |
| CANT_TELL_YET receipt with a row reading `Shown here: ...` | Scope check runs after receipt resolution and before a CANT verdict when the comparison itself is fine | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` | Before: O5 never compared the scope sentence. After: FAIL; refusal names the card, the row, `Shown here` and `NOT DEMONSTRATED`. |
| KEEP receipt with `verdict_scope` — exact scope line passes, one-word change refused | Derivation fills harness `_scope_line` fields; row must equal that text | `case_evidence_scope_keep_with_scope_exact_passes` and `case_evidence_scope_keep_one_word_change_is_fail` | Before: the branch rendered `DEMONSTRATED — {scope}.`, which is not skill-harness's wording; the exact line and the one-word mutant both graded against the wrong sentence. After: the exact R2 fixture sentence passes O5; replacing `trap-discipline` with `trap discipline` is FAIL and the refusal names both sentences. |
| Carried-forward KEEP — carried-forward sentence passes, standard sentence refused | Carried-forward decided from `currentness.state == "CARRIED_FORWARD"` only | `case_evidence_scope_carried_forward_beats_standard` | Before: the branch used `scope_carried_forward` / `carried_forward` keys that SERS does not carry, and the wrong DEMONSTRATED sentences. After: the sentinel-rule sentence passes; writing the standard `Shown here: …` sentence on the same receipt is FAIL. |
| Quarantine card with no row passes | Published-card walk excludes `_quarantine/` | `case_evidence_scope_quarantine_card_with_no_row_passes` (conformance) and `case_quarantine_card_with_no_row_is_exempt` (card-files) | Before and after: quarantine owes no row; O5 stays CANNOT-CHECK on the published card and the live gate stays green. |
| Scoreboard still passes a card carrying the new row | `Evidence scope` is not a scoreboard controlled field; the live tree still derives | `case_scoreboard_passes_a_card_carrying_evidence_scope` | After: `validate_scoreboard.py` PASS line still reports `records derive 14 admitted, 1 measured…`. |

R2 extras that also run through the entry point:

- `case_evidence_scope_keep_without_delivery_is_unknown_delivery` — KEEP fixture with `delivery_mechanism` absent yields `unknown delivery` and passes O5.
- `case_evidence_scope_empty_row_is_refused_with_its_own_message` — an empty row is refused with the empty-row message (R4).
- `case_evidence_scope_live_tree_rows_match_the_closed_set` — live tree: 13 UNMEASURED + pull-rebase NOT DEMONSTRATED, no fourth shape.

### 2. Every clause this ticket adds has a mutant that its named assertion kills

Mutation receipts (mutant applied to the working tree, named test run, mutant then reverted). The instrument is the suite itself; this tree ships no `scripts/mutation_receipt.py`.

| Clause | Mutant | Test that turns red |
|---|---|---|
| Card-files contract-row set includes `Evidence scope` | Drop `EVIDENCE_SCOPE_ROW` from `REQUIRED_EVIDENCE_ROWS` | `case_missing_evidence_scope_row_is_rejected` → FAIL (suite accepted a card with no row) |
| Empty-row refusal has its own message | Delete the `if not stated:` branch in `evidence_scope_breaches` | `case_evidence_scope_empty_row_is_refused_with_its_own_message` → FAIL (message became the mismatch sentence) |
| Standard KEEP template is harness wording | Change `effect` → `effects` in `SCOPE_LINE_TEMPLATE` | `case_scope_line_drift_vs_harness_render` → FAIL (ours vs harness `_scope_line`); `case_evidence_scope_constants_are_the_closed_set` → FAIL |
| Carried-forward KEEP template is harness wording | Change `re-validated` → `revalidated` in `SCOPE_LINE_CARRIED_TEMPLATE` | `case_scope_line_drift_vs_harness_render` → FAIL (carried-forward fixture); `case_evidence_scope_constants_are_the_closed_set` → FAIL |
| Carried-forward from `currentness.state` only | Decide carried-forward from `receipt.get("scope_carried_forward")` instead | `case_evidence_scope_carried_forward_beats_standard` → FAIL (carried sentence became the standard sentence; standard sentence no longer refused) |
| Missing `delivery_mechanism` reads `unknown delivery` | Default `""` instead of `"unknown delivery"` | `case_evidence_scope_keep_without_delivery_is_unknown_delivery` → FAIL |
| Drift test compares against the harness render | Remove/neutralise the comparison in `case_scope_line_drift_vs_harness_render` | Not claimed as a constant mutant; the CI step greps for `skills derivation equals harness _scope_line` and refuses a skip, so a disabled case fails CI rather than staying green in silence. |

### 3. Drift test passes against the skill-harness checkout CI uses; fails when one word of a constant changes

- `case_scope_line_drift_vs_harness_render` imports `skill_harness.sitegen.render._scope_line` from `<root>/src`, renders the R2 KEEP fixtures (standard with delivery, standard without delivery, carried-forward), strips `<p class="scope-line">`, unescapes HTML, and asserts equality with `conformance.expected_evidence_scope` for the same receipt. It does not look for named constants in the harness.
- Without `SKILL_HARNESS_ROOT` it skips with a named reason: `scope-line drift skipped: SKILL_HARNESS_ROOT is not set to a skill-harness checkout…`.
- With `SKILL_HARNESS_ROOT=/home/agent/scratch/skill-harness` (skill-harness main `b48ee47`): all three comparisons PASS.
- One-word constant mutation (`effect` → `effects` or `re-validated` → `revalidated`): both the drift case and `case_evidence_scope_constants_are_the_closed_set` turn red (see mutation receipts above).
- `.github/workflows/tests.yml` step **Evidence scope drift against skill-harness** checks out `MrBinnacle/skill-harness` at its default branch, `pip install -e`s it in that step only, runs `SKILL_HARNESS_ROOT=… python scripts/test_validate_conformance.py`, and greps that the drift case ran and did not skip. It runs on `matrix.os == 'ubuntu-latest'` only.
- The PR body therefore may claim the drift test catches a wording change: the CI step runs it.

### 4. Full validator suite and `python scripts/release_gate.py` pass at head and on a CRLF checkout

LF head (`15804b9`, this workspace):

- `PYTHONUTF8=1 SKILL_HARNESS_ROOT=… python scripts/test_validate_conformance.py` → PASS
- `PYTHONUTF8=1 python scripts/test_validate_card_files.py` → PASS
- `PYTHONUTF8=1 python scripts/validate_conformance.py` → PASS (14 cards, 0 FAIL)
- `PYTHONUTF8=1 python scripts/validate_card_files.py` → PASS
- `PYTHONUTF8=1 python scripts/validate_scoreboard.py` → PASS
- `PYTHONUTF8=1 python scripts/release_gate.py` → `RELEASE GATE: PASS`
- Also green: skill-formats, disposition-counts, path-residue, voice-provenance, brand-kit, eval-corpora, site-links, standing-costs, scoreboard suite, captured-exit handling, im-down/im-up parity (`no-drift`) and the stale-packet poison control (`REJECTED`).

CRLF checkout (`git -c core.autocrlf=true clone` + checkout of `agent/issue-354` at `15804b9`):

- 303 tracked text files carry CRLF, including `scripts/validate_conformance.py`, `scripts/test_validate_conformance.py`, `skills/engineering/vacuous-check/SKILL.md` and `skills/meta/dead-predicate/SKILL.md`.
- Same suites: conformance PASS (including drift against skill-harness), card-files PASS, live conformance PASS, live card-files PASS, scoreboard PASS, release_gate PASS.
- `scripts/validate_card_files.py` measures SKILL.md size on content with CRLF collapsed to LF, so an at-limit card is not red for its line endings (R5-related; `case_skill_size_uses_normalized_line_endings`).

R5 line endings: `scripts/validate_conformance.py` on `origin/main` is CRLF (942 CRLF lines). The branch keeps CRLF (1143 CRLF lines at head); the three-dot diff shows the real content change, not a whole-file EOL rewrite.

### 5. Changeset declares major, citing ADR 0002

`.changeset/issue-354-evidence-scope.md`:

- `"mrbinnacle-skills": major`
- Cites `docs/adr/0002-a-release-is-a-delivery-event.md` and quotes: "Changing the install path, or the on-disk shape of a card, is a major change."

### 6. PR body lists only files in the diff; every count matches a command run at the final head

- File list above is exactly `git diff --name-only origin/main...HEAD` at `15804b9` (22 files).
- Counts: 14 published cards; 13 UNMEASURED; 1 NOT DEMONSTRATED (pull-rebase); 22 diff files; shortstat `22 files changed, 1101 insertions(+), 49 deletions(-)` — each from the commands printed in this body at final head.
- The scratch hand-off path is not part of the published branch diff and is not listed above.

## Rework deltas this run (relative to `0a8fd9d`)

- **R1**: Replaced `DEMONSTRATED — {scope}.` / `DEMONSTRATED — {scope} (carried forward).` with skill-harness `_scope_line` wording; derivation fills fields with harness defaults; carried-forward from `currentness.state` only.
- **R2**: KEEP fixtures are SERS 1.6.0 objects (`verdict_scope` object, `currentness` object or null, `subject_identity` object or null); one fixture omits `delivery_mechanism` → `unknown delivery`.
- **R3**: Drift test imports `_scope_line` and renders fixtures (no constant-hunting); CI step checks out skill-harness and runs the test on ubuntu-latest.
- **R4**: Empty-row clause has its own assertion; deleting `if not stated:` turns that case red.
- **R5**: `scripts/validate_conformance.py` keeps CRLF; the size check measures content, not checkout EOL.
- **R6**: Changeset and this body state the drift CI step and the final-head counts.

## Reproduce

```bash
SKILL_HARNESS_ROOT=<skill-harness checkout> python scripts/test_validate_conformance.py
python scripts/test_validate_card_files.py
python scripts/validate_conformance.py
python scripts/release_gate.py
# CRLF: git -c core.autocrlf=true clone <this repo> <dir> && cd <dir> && git checkout agent/issue-354
#       then re-run the same suite commands there.
```

Verifier note from the ticket: O5's receipt resolution serves the no-receipt case without a separate validator function — `evidence_scope_breaches` derives `UNMEASURED — no receipt.` from the card alone when no `Receipt:` clause is present, and still runs when `--harness-root` is omitted.
