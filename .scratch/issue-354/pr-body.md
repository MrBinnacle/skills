# #354 — Evidence scope row on every published card, checked against the linked receipt

Branch `agent/issue-354`. Head `7f4dbf9c6dd3bdb374e7b33ea08b791449c0cfbc`. Base `origin/main`. Diff against that base: **22 files changed, 1606 insertions(+), 49 deletions(-)** (command: `git diff --shortstat origin/main...HEAD` at head `7f4dbf9`).

## What this branch ships

Every published card's `EVIDENCE.md` carries an `| **Evidence scope** | ... |` row. CI refuses a published card whose row is missing or disagrees with what the card's linked receipt shows. The row's value is derived from the receipt conformance O5 already resolves from the card's `Receipt:` clause under `--harness-root`, using the closed set from skills#353.

The four closed-set sentences are:

- `UNMEASURED — no receipt.`
- `NOT DEMONSTRATED — receipt verdict <VERDICT>; no effect is shown.`
- `UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).`
- For a KEEP receipt with a `verdict_scope` object: skill-harness's own scope line, standard or carried-forward form, filled field by field.

R3-3 adds one more shape for multi-receipt cards: when a card links more than one receipt and none is a usable KEEP, the NOT DEMONSTRATED row names every distinct verdict among the linked receipts, in receipt order, deduplicated (for example `NOT DEMONSTRATED (CANT_TELL_YET, NO_LIFT)`). A public row must not hide a linked verdict.

Thirteen cards read the UNMEASURED sentence. `pull-rebase` reads `NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.` against its CANT_TELL_YET receipt. Quarantine cards and `scripts/fixtures/` are exempt.

## Files in the diff

Command: `git diff --name-only origin/main...HEAD` at head `7f4dbf9`. Twenty-two files:

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

Per-file stat at the same head:

| File | + / − |
|---|---|
| `.changeset/issue-354-evidence-scope.md` | +9 / −0 |
| `.github/workflows/tests.yml` | +32 / −0 |
| `scripts/fixtures/card-missing-evidence-row/.../EVIDENCE.md` | +1 / −0 |
| `scripts/fixtures/card-missing-gotchas/.../EVIDENCE.md` | +1 / −0 |
| `scripts/test_validate_card_files.py` | +125 / −0 |
| `scripts/test_validate_conformance.py` | +1180 / −44 |
| `scripts/validate_card_files.py` | +20 / −2 |
| `scripts/validate_conformance.py` | +224 / −3 |
| 14 published-card `EVIDENCE.md` files | +1 / −0 each |

Command: `git diff --numstat origin/main...HEAD` at head `7f4dbf9`. Totals: 1606 insertions, 49 deletions.

## Mechanism

### Card-files validator (`scripts/validate_card_files.py`)

`EVIDENCE_SCOPE_ROW = "Evidence scope"` joins `REQUIRED_EVIDENCE_ROWS`. Presence is this script's contract; the value is O5's. A card missing the row is refused by `evidence_breaches` with a message naming the row. Quarantine cards and `scripts/fixtures/` are not published cards here, so they owe nothing.

### Conformance validator (`scripts/validate_conformance.py`)

O5's `check_receipt_agreement` calls `evidence_scope_breaches` in both modes. Without `--harness-root`, a scope breach is still a FAIL; without any breach the cell stays CANNOT-CHECK. With `--harness-root`, the scope check runs after the receipt comparison and before a CANNOT-CHECK verdict, so a wrong scope sentence is never buried.

`expected_evidence_scope(receipts)` derives the row from the loaded receipt objects:

1. No receipts → `UNMEASURED — no receipt.`
2. Any KEEP receipt with a usable `verdict_scope` object → the harness scope line (carried-forward when `currentness.state == "CARRIED_FORWARD"`, decided from that key alone).
3. Any KEEP receipt but none with a usable scope object → `UNSCOPED`.
4. No KEEP receipts → NOT DEMONSTRATED. One distinct verdict keeps the single sentence; several use `NOT DEMONSTRATED (V1, V2, ...)`, in receipt order, deduplicated.

Field defaults mirror skill-harness's `_string_field`: a missing or non-string field reads `unknown task family`, `unknown model`, `unknown delivery`, `unknown date`, or `current model`. A non-object `verdict_scope` on a KEEP receipt derives UNSCOPED; the harness `_scope_line` returns `""` for that case, which is why the row states the closed-set refusal rather than inventing a Shown here sentence.

The scope-line templates are constants in this file with a comment naming `skill_harness/sitegen/render.py::_scope_line` as the source. The drift test imports that function from `<SKILL_HARNESS_ROOT>/src`, renders the KEEP fixtures through it, strips the `<p class="scope-line">` wrapper, unescapes HTML, and asserts equality with this repository's derivation. It does not look for named constants in the harness. Without `SKILL_HARNESS_ROOT` it skips with a named reason. N1: the test asserts `harness_render.__file__` lies under `SKILL_HARNESS_ROOT`, so an editable install of skill-harness from another checkout cannot silently answer the drift question.

`evidence_scope_breaches` strips `* ` and backticks from the stated row before comparing, so a correct sentence wrapped in bold or backticks is accepted. It refuses an empty row with its own message (`EVIDENCE.md states no Evidence scope row ... empty row is the same refusal`).

A card whose only Receipt clause is a `not current` history link to a missing or unreadable file is not refused for a correct NOT DEMONSTRATED sentence: `_linked_receipt_dicts` marks that case unresolvable, and `evidence_scope_breaches` leaves the row to the receipt check rather than deriving UNMEASURED from an empty list.

### CI (`.github/workflows/tests.yml`)

A dedicated step on ubuntu-latest checks out `MrBinnacle/skill-harness` at its default branch, runs `pip install -e` on that checkout, then runs `SKILL_HARNESS_ROOT=<checkout> python scripts/test_validate_conformance.py`. The step greps for the drift assertion line and fails if the case skipped. Without this step the drift test's claim would rest on a local checkout alone; with it, CI runs the comparison against current skill-harness main.

### Changeset (`.changeset/issue-354-evidence-scope.md`)

Declares **major** and cites ADR 0002: "Changing the install path, or the on-disk shape of a card, is a major change." The description states the closed set, the multi-receipt form, the drift mechanism, and the CI step.

### Published cards

Fourteen `EVIDENCE.md` files gain one row each. Thirteen read `UNMEASURED — no receipt.`. `skills/engineering/pull-rebase/EVIDENCE.md` reads `NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.`

## Acceptance criteria

### 1. Each fixture runs through the validator entry point; red without its clause, green with it

Every case below is a real tree on disk, run through the real `validate_conformance.py` (or `validate_card_files.py`) as a subprocess. Each refusal names the card and the row.

| Criterion | Test | What pins it | Observed |
|---|---|---|---|
| Published card missing `Evidence scope` | `case_missing_evidence_scope_row_is_rejected` in `scripts/test_validate_card_files.py` | `validate_card_files.py` adds `Evidence scope` to `REQUIRED_EVIDENCE_ROWS`; `evidence_breaches` refuses an absent row | Without the row in the fixture's EVIDENCE.md the gate exits nonzero and prints `no Evidence scope row`; with the row restored the same tree passes |
| No-receipt card whose row is anything but the UNMEASURED sentence | `case_evidence_scope_no_receipt_wrong_sentence_is_fail` in `scripts/test_validate_conformance.py` | `evidence_scope_breaches` derives `UNMEASURED — no receipt.` from the empty receipt list and refuses any other stated sentence | Row set to `Shown here: nothing measured.` → O5 FAIL naming `alpha-card` and `Evidence scope`, run nonzero; correct UNMEASURED row → CANNOT-CHECK (receipt), not FAIL |
| CANT_TELL_YET receipt with a row reading `Shown here: ...` | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` | `expected_evidence_scope` returns the NOT DEMONSTRATED sentence for a non-KEEP receipt | Row set to `Shown here: the bare arm passed.` → O5 FAIL naming both sentences |
| KEEP receipt with `verdict_scope`; exact scope line passes, one-word change refused | `case_evidence_scope_keep_with_scope_exact_passes` and `case_evidence_scope_keep_one_word_change_is_fail` | Templates equal skill-harness `_scope_line` wording; `stated != expected` refuses any deviation | Exact SERS-shaped KEEP receipt with full scope object → O5 PASS; same receipt with `trap-discipline` changed to `trap discipline` → O5 FAIL |
| Carried-forward KEEP; carried-forward sentence passes, standard refused | `case_evidence_scope_carried_forward_beats_standard` | Carried-forward is decided from `currentness.state` only; the sentinel-rule template is used | Receipt with `currentness.state = CARRIED_FORWARD` → carried sentence PASS; standard `Shown here:` sentence → FAIL naming both shapes |
| Quarantine card with no row passes | `case_evidence_scope_quarantine_card_with_no_row_passes` | Conformance walks `skills/*/*/SKILL.md` only; `_quarantine/` is outside that glob | Quarantine candidate without the row does not fail the run |
| Scoreboard validator still passes a card carrying the new row | `case_scoreboard_passes_a_card_carrying_evidence_scope` in `scripts/test_validate_card_files.py` | `CONTROLLED_FIELDS` stays `("Screen result", "Paired verdict")`; Evidence scope is not a scoreboard field | Live tree with all fourteen rows present → `validate_scoreboard.py` PASS |

### 2. Every clause this ticket adds has a mutant that its named assertion kills

R3 found three clauses whose mutants survived. Each now has a named fixture and a named assertion. The mutants were applied one at a time to `scripts/validate_conformance.py`, the suite was run with `SKILL_HARNESS_ROOT=<skill-harness checkout>`, and the named assertion went red in every case. The tree was restored to clean head bytes after each mutant.

| Mutant | Edit | Named assertion that turns red | Test name |
|---|---|---|---|
| M16 | `if not isinstance(scope, dict):` → `if not scope:` | `a KEEP receipt with a non-object verdict_scope derives UNSCOPED` — under the mutant the derivation returns a Shown here sentence with unknown-field defaults instead of UNSCOPED | `case_evidence_scope_keep_non_object_verdict_scope_is_unscoped` |
| M31 | `.strip("* ")` → `.strip()` in `evidence_scope_breaches` | `a bold-wrapped correct Evidence scope row is accepted on O5` — under the mutant the stated `**UNMEASURED — no receipt.**` is compared unwrapped and refused | `case_evidence_scope_bold_wrapped_row_is_accepted` |
| M32 receipts[0] | multi-verdict branch replaced by `receipts[0]` single pick | `two linked receipts derive NOT DEMONSTRATED naming both verdicts` — under the mutant the row names only CANT_TELL_YET | `case_evidence_scope_multi_receipt_names_every_verdict` |
| M32 receipts[-1] | multi-verdict branch replaced by `receipts[-1]` single pick | same assertion — under the mutant the row names only NO_LIFT | same test |

Earlier-round mutants stay killed. The suite carries named assertions for M1–M15 (field defaults, non-string fields, missing `subject_model`), M23–M24 (history link to missing file / invalid JSON), M26 (no-receipt refusal under `--harness-root`), the empty-row message (R4), the N1 import-path check, and the drift comparison. Those assertions were written in earlier rounds of this branch and were verified green at head `515a557` before this round's changes; this round did not remove them.

### 3. Drift test passes against the skill-harness checkout CI uses, and fails when one word of the constant changes

Test: `case_scope_line_drift_vs_harness_render` in `scripts/test_validate_conformance.py`. CI step: `Evidence scope drift against skill-harness` in `.github/workflows/tests.yml`.

Observed at head `7f4dbf9` with `SKILL_HARNESS_ROOT=/home/agent/skill-harness-tmp` (clone of `MrBinnacle/skill-harness` default branch): the drift assertion line `skills derivation equals harness _scope_line for ...` printed `ok` for all ten KEEP fixtures (standard with and without delivery/model_id/task_family/tested_at, non-string model_id, non-string task_family, carried-forward, carried-forward without subject_model, carried-forward with non-string subject_model). The N1 check `the drift import of render.py lies under SKILL_HARNESS_ROOT` printed `ok`.

One-word mutant: `SCOPE_LINE_TEMPLATE` changed from `... real-world incidence.` to `... real-world incidents.`. Under that mutant `case_scope_line_drift_vs_harness_render` failed seven standard-form comparisons (ours printed `incidents`, harness printed `incidence`) and `case_evidence_scope_constants_are_the_closed_set` failed `SCOPE_LINE_TEMPLATE is the harness standard KEEP scope line`. The tree was restored; clean head re-ran green.

Without `SKILL_HARNESS_ROOT` the case prints `NOT VERIFIED: scope-line drift skipped: SKILL_HARNESS_ROOT is not set...` and does not claim a comparison.

### 4. Full validator suite and release_gate pass at head and on a CRLF checkout

Commands at head `7f4dbf9` (LF working tree):

- `PYTHONUTF8=1 python scripts/test_validate_card_files.py` → `PASS: card-file conformance suite, all cases correct`
- `PYTHONUTF8=1 SKILL_HARNESS_ROOT=<checkout> python scripts/test_validate_conformance.py` → `PASS: conformance v4 suite, all cases correct`
- `PYTHONUTF8=1 python scripts/validate_card_files.py` → `PASS: 14 published card(s) ... every EVIDENCE.md states ... Evidence scope`
- `PYTHONUTF8=1 python scripts/validate_conformance.py` → `PASS: conformance v4: 14 card(s) x 4 card obligation(s) + 4 repo obligation(s) = 60 cells: 46 PASS, 0 FAIL, 14 CANNOT-CHECK`
- `PYTHONUTF8=1 python scripts/validate_scoreboard.py` → `PASS: ruled banner line pinned at 5 sites; records derive 14 admitted, 1 measured, 2 retired, 4 solutions looking for a problem`
- `PYTHONUTF8=1 python scripts/release_gate.py` → `RELEASE GATE: PASS - surfaces healthy at version 3.0.1`
- `PYTHONUTF8=1 python scripts/test_release_gate.py` → `PASS: release gate verified across 69 contract case(s)`
- `PYTHONUTF8=1 python scripts/validate_skill_formats.py`, `validate_voice_provenance.py`, `validate_brand_kit.py`, `validate_spec_conformance.py`, `validate_conformance.py --root .` → all PASS

CRLF checkout: a copy of the working tree with every text file converted LF→CRLF (the `core.autocrlf=true` Windows working-tree shape). Same commands:

- `validate_card_files.py` → PASS
- `validate_scoreboard.py` → PASS
- `validate_conformance.py` → PASS (60 cells, 0 FAIL)
- `release_gate.py` → PASS
- `test_validate_card_files.py` → PASS
- `SKILL_HARNESS_ROOT=... python scripts/test_validate_conformance.py` → `PASS: conformance v4 suite, all cases correct`

`scripts/validate_conformance.py` is CRLF in the committed tree (1163 CRLF lines, 0 LF-only at head `7f4dbf9`). R5 is satisfied: this round's edits preserved that, so the diff shows only the real change rather than a whole-file EOL rewrite.

### 5. Changeset declares major, citing ADR 0002

File: `.changeset/issue-354-evidence-scope.md`. Frontmatter: `"mrbinnacle-skills": major`. Body quotes ADR 0002: "Changing the install path, or the on-disk shape of a card, is a major change." `scripts/release_gate.py` and `scripts/test_release_gate.py` both pass with this changeset present.

### 6. PR body lists only files in the diff, and every count matches a command run at the final head

This body's file list is exactly `git diff --name-only origin/main...HEAD` at head `7f4dbf9c6dd3bdb374e7b33ea08b791449c0cfbc`. The shortstat `22 files changed, 1606 insertions(+), 49 deletions(-)` is `git diff --shortstat origin/main...HEAD` at that head. The per-file table is `git diff --stat origin/main...HEAD` at that head. No runner note from an earlier round remains in this body.

## R3 round checklist

| Requirement | Status | Evidence |
|---|---|---|
| R3-1: non-object `verdict_scope` fixture asserts UNSCOPED; M16 turns it red | Done | `case_evidence_scope_keep_non_object_verdict_scope_is_unscoped`; mutant run above |
| R3-2: bold/backtick-wrapped correct row accepted; M31 turns it red | Done | `case_evidence_scope_bold_wrapped_row_is_accepted`; mutant run above |
| R3-3: multi-receipt NOT DEMONSTRATED names every distinct verdict; `receipts[0]` and `receipts[-1]` each turn it red | Done | `case_evidence_scope_multi_receipt_names_every_verdict`; both mutants red |
| R3-4: PR body regenerated from the final head; no stale runner note | Done | This body; counts from `7f4dbf9` |

## Prior-round guarantees kept

R1 (harness wording, SERS fixtures, carried-forward from `currentness.state`), R2 (SERS receipt shape including missing-field fixtures), R3/R3-drift (templates as constants, harness-render comparison, CI step), R4 (empty-row message), R5 (CRLF preserved), F1(a) (M11–M15 field defaults), F1(b) (M26 harness-root no-receipt refusal), F1(c) (M23–M24 history unresolvable), F2 (body counts from final head), N1 (import-path check). Each has a named assertion in `scripts/test_validate_conformance.py` that was green at head `515a557` and remains green at `7f4dbf9`.

## Revisit note from the ticket

The ticket's revisit clause asks: if O5's receipt resolution cannot serve the no-receipt case, put the evidence-scope check in its own validator function and say so here. O5's resolution does serve it. `evidence_scope_breaches` derives `UNMEASURED — no receipt.` from the empty receipt list and is called from `check_receipt_agreement` in both harness-root modes. No separate validator function is needed.

## Next action

Merge when CI is green at this head. The changeset rolls a major version on merge per ADR 0002.
