# #354 — Evidence scope on every published card

## What landed

Every published card's `EVIDENCE.md` now carries an `| **Evidence scope** | ... |` row. The card-files validator requires the row. Conformance O5 derives the row's value from the receipt the card's `Receipt:` clause names (under `--harness-root`), and refuses a row that disagrees — including the no-receipt case O5 previously skipped by returning `CANNOT-CHECK`.

Closed set from skills#353:

| Receipt state | Row value |
|---|---|
| No `Receipt:` clause in any controlled field | `UNMEASURED — no receipt.` |
| Receipt verdict other than KEEP | `NOT DEMONSTRATED — receipt verdict <VERDICT>; no effect is shown.` |
| KEEP receipt, no `verdict_scope` | `UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).` |
| KEEP receipt with `verdict_scope` | skill-harness's scope line, standard (`DEMONSTRATED — {scope}.`) or carried-forward (`DEMONSTRATED — {scope} (carried forward).`) |

Live tree at head: 13 cards read `UNMEASURED — no receipt.`; `pull-rebase` reads `NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.` Quarantine cards and `scripts/fixtures/` are exempt (find_cards walks `skills/<bucket>/<card>` only).

The scope-line templates are constants in `scripts/validate_conformance.py` with a comment naming their source in skill-harness (SERS >= 1.6.0 evidence-scope render, quoted in skills#353). The drift test compares them with the harness render when `SKILL_HARNESS_ROOT` is set and skips with a named reason when it is not.

**Parent #353 Implementation/Testing Decisions:** this container holds no GitHub token and the ticket forbade network reads of the tracker, so #353's quoted KEEP scope-line sentences could not be fetched. The three fixed sentences are quoted in this ticket and are pinned by `case_evidence_scope_constants_are_the_closed_set`. The two KEEP templates follow the closed-set naming and are pinned by that same case plus the exact-match / carried-forward acceptance fixtures; if #353's quoted forms differ, the drift test against a skill-harness checkout is the instrument that will say so.

## Acceptance criteria

### 1. Fixture suite — each red without its clause, green with it, refusal names card and row

| Fixture | Entry point | Named assertion |
|---|---|---|
| Published card missing `Evidence scope` | `scripts/validate_card_files.py` | `case_missing_evidence_scope_row_is_rejected` — red without the row (`no Evidence scope row`, names `skills/engineering/scopeless-card`); green with it (`case_evidence_scope_row_present_clears_it`) |
| No-receipt card with a wrong `UNMEASURED` sentence | `scripts/validate_conformance.py` (no harness needed) | `case_evidence_scope_no_receipt_wrong_sentence_is_fail` — `Shown here: nothing measured.` refused; names card + `Evidence scope`; green half is `case_evidence_scope_no_receipt_correct_sentence_is_cant` |
| CANT_TELL_YET receipt with row `Shown here: ...` | conformance `--harness-root` | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` — refusal names card, `Evidence scope`, both sentences |
| KEEP + `verdict_scope`, exact vs one-word | conformance `--harness-root` | `case_evidence_scope_keep_with_scope_exact_passes` (green) and `case_evidence_scope_keep_one_word_change_is_fail` (one-word `pre-flight`→`preflight` refused) |
| Carried-forward KEEP vs standard sentence | conformance `--harness-root` | `case_evidence_scope_carried_forward_beats_standard` — carried-forward sentence passes; standard sentence refused |
| Quarantine card with no row | card-files and conformance | `case_quarantine_card_with_no_row_is_exempt` / `case_evidence_scope_quarantine_card_with_no_row_passes` — green |
| Scoreboard still passes a card carrying the new row | `scripts/validate_scoreboard.py` | `case_scoreboard_passes_a_card_carrying_evidence_scope` — live tree PASS; `records derive` still present |

**Red-before / green-after:** before this change the live tree had zero `Evidence scope` rows and `validate_card_files.py` was green on that state. After adding the contract row, a fixture without the row is refused (`REJECTED: ... no Evidence scope row`); the same fixture with the row is green. Conformance value fixtures fail with the mismatch sentence when the row is wrong and pass when it matches the derived value.

### 2. Mutation campaign

Every clause this ticket adds has a mutant that a named assertion kills. Applied in a throwaway worktree, run, reverted; post-campaign named cases re-verified green.

| Mutant | Named assertion that turns red |
|---|---|
| Drop `EVIDENCE_SCOPE_ROW` from `REQUIRED_EVIDENCE_ROWS` | `case_missing_evidence_scope_row_is_rejected` |
| `SCOPE_NO_RECEIPT` one word (`UNMEASURED`→`MEASURED`) | `case_evidence_scope_constants_are_the_closed_set` |
| `SCOPE_NOT_DEMONSTRATED_FMT` drop `no effect is shown` | `case_evidence_scope_constants_are_the_closed_set` |
| `SCOPE_UNSCOPED` drop `(SERS before 1.6.0)` | `case_evidence_scope_constants_are_the_closed_set` |
| `SCOPE_LINE_TEMPLATE` `DEMONSTRATED`→`SHOWN` | `case_evidence_scope_keep_with_scope_exact_passes` |
| `SCOPE_LINE_CARRIED_TEMPLATE` drop `(carried forward)` | `case_evidence_scope_carried_forward_beats_standard` |
| `expected_evidence_scope([])` returns `''` | `case_evidence_scope_constants_are_the_closed_set` |
| `evidence_scope_breaches` always returns `[]` | `case_evidence_scope_no_receipt_wrong_sentence_is_fail` |
| KEEP branch never reads `verdict_scope` | `case_evidence_scope_keep_with_scope_exact_passes` |
| Carried-forward branch removed | `case_evidence_scope_carried_forward_beats_standard` |
| Refusal messages drop `card.name` | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` |

No test monkeypatches the function it claims to mutate; each mutant is a real edit to the shipped validator file.

### 3. Drift test

`case_scope_line_drift_vs_harness_render` compares `SCOPE_LINE_TEMPLATE` / `SCOPE_LINE_CARRIED_TEMPLATE` / `SCOPE_NO_RECEIPT` / `SCOPE_UNSCOPED` against templates found in a skill-harness checkout when `SKILL_HARNESS_ROOT` names one. Without a checkout it skips with a named reason: `scope-line drift skipped: no skill-harness checkout (set SKILL_HARNESS_ROOT ...)`. This container has no skill-harness clone, so the skip path is what ran here; the one-word-constant red is pinned by `case_evidence_scope_constants_are_the_closed_set`, which does not need a checkout.

### 4. Full suite and release gate, LF and CRLF

At code head `d0f5b8e` (the last commit that changes the PR diff; `cfde1f1` adds only this evidence body under `.scratch/`, which the runner drops before the push), `PYTHONUTF8=1`:

| Command | LF | CRLF (`git archive` + `sed` to CRLF) |
|---|---|---|
| `python scripts/validate_card_files.py` | PASS (14 cards, all four rows) | PASS |
| `python scripts/validate_conformance.py` | PASS (60 cells, 0 FAIL) | PASS |
| `python scripts/validate_scoreboard.py` | PASS | PASS |
| `python scripts/release_gate.py` | PASS | PASS |
| `python scripts/test_validate_card_files.py` | PASS | PASS |
| `python scripts/test_readme_admission_lead.py` | PASS | — |

CRLF required one repair inside this ticket's scope: `size_breaches` measured raw on-disk bytes, so a CRLF checkout red two published cards that sit under the ceiling on LF (`vacuous-check` 7108 B, `dead-predicate` 7141 B) purely for line endings. `size_breaches` now collapses CRLF to LF before measuring; both checkouts are green.

### 5. Changeset

`.changeset/issue-354-evidence-scope.md` declares `"mrbinnacle-skills": major` and cites ADR 0002: *"Changing the install path, or the on-disk shape of a card, is a major change."* Adding a row to every published card's on-disk `EVIDENCE.md` is that change. `python scripts/release_gate.py` reports `RELEASE GATE: PASS`.

### 6. PR body files and counts

Files in the diff (21; `.scratch/issue-354/pr-body.md` is the runner's hand-off and is not part of the final diff):

- `.changeset/issue-354-evidence-scope.md`
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

Counts at final head, from commands run on this tree:

- Published cards: **14** (`git ls-files 'skills/*/*/SKILL.md' | wc -l`)
- `EVIDENCE.md` files carrying the `Evidence scope` row: **14**
- Rows reading `UNMEASURED — no receipt.`: **13**
- Rows reading `NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.`: **1** (`pull-rebase`)
- Conformance cells: **60** (14 cards x 4 card obligations + 4 repo obligations), **0 FAIL**
- Card-files allowlisted breaches: **14**, recorded 2026-09-06 (pre-existing, unchanged)

## Criterion → test map

| Criterion | Test |
|---|---|
| Missing `Evidence scope` red/green | `test_validate_card_files.py::case_missing_evidence_scope_row_is_rejected` / `case_evidence_scope_row_present_clears_it` |
| No-receipt wrong sentence | `test_validate_conformance.py::case_evidence_scope_no_receipt_wrong_sentence_is_fail` |
| CANT_TELL_YET `Shown here:` | `test_validate_conformance.py::case_evidence_scope_cant_tell_yet_shown_here_is_fail` |
| KEEP exact vs one-word | `test_validate_conformance.py::case_evidence_scope_keep_with_scope_exact_passes` / `case_evidence_scope_keep_one_word_change_is_fail` |
| Carried-forward vs standard | `test_validate_conformance.py::case_evidence_scope_carried_forward_beats_standard` |
| Quarantine exempt | `test_validate_card_files.py::case_quarantine_card_with_no_row_is_exempt`; `test_validate_conformance.py::case_evidence_scope_quarantine_card_with_no_row_passes` |
| Scoreboard still green | `test_validate_card_files.py::case_scoreboard_passes_a_card_carrying_evidence_scope` |
| Constants pin / one-word drift | `test_validate_conformance.py::case_evidence_scope_constants_are_the_closed_set` |
| Harness render drift | `test_validate_conformance.py::case_scope_line_drift_vs_harness_render` |
| Live tree closed set | `test_validate_conformance.py::case_evidence_scope_live_tree_rows_match_the_closed_set` |
