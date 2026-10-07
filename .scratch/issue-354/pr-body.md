# #354 — Evidence scope row on every published card, checked against the linked receipt

**Head:** `33a66eb3fe2b1b2be056cdabade590cacfa2e19b` (`agent/issue-354`)
**Base:** `origin/main` @ `4ebc0dfafcfc18609fcab6a8eec6b0b35ebcc6e9` (merge-base of the branch)

This body describes the branch as it now stands, after the round-2 rework (S518 F1a–F1c, N1) and the post-merge head. Counts and file lists below come from commands run at head `33a66eb`.

## Diff at this head

```text
$ git rev-parse HEAD
33a66eb3fe2b1b2be056cdabade590cacfa2e19b

$ git diff --shortstat origin/main...HEAD
 22 files changed, 1407 insertions(+), 49 deletions(-)

$ git diff --numstat origin/main...HEAD -- scripts/validate_conformance.py scripts/test_validate_conformance.py
204	3	scripts/validate_conformance.py
1001	44	scripts/test_validate_conformance.py
```

Files in `git diff --name-only origin/main...HEAD` (22):

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

Live-tree census at this head (read from the cards, not from prose):

```text
published cards 14
13x 'UNMEASURED — no receipt.'
1x 'NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.'
pull-rebase: NOT DEMONSTRATED — receipt verdict CANT_TELL_YET; no effect is shown.
```

`scripts/validate_conformance.py` is CRLF in the index (1143 CRLF lines), as on `origin/main`. The +204/−3 on that file is content, not an EOL rewrite. `scripts/test_validate_conformance.py` is LF.

## What the branch ships

Every published card's `EVIDENCE.md` field table carries an `| **Evidence scope** | … |` row. CI refuses a published card whose row is missing or disagrees with what the card's linked receipt shows. Quarantine cards and `scripts/fixtures/` are exempt (they are not published cards under `find_cards`).

**Closed set (skills#353, R1).**

- `UNMEASURED — no receipt.`
- `NOT DEMONSTRATED — receipt verdict <VERDICT>; no effect is shown.`
- `UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).`
- For a KEEP receipt with a `verdict_scope` object, skill-harness's own scope line from `skill_harness/sitegen/render.py::_scope_line`, filled field by field, with the HTML wrapper `<p class="scope-line">…</p>` removed and without HTML escaping:
  - standard: `Shown here: effect on {task_family}, {model}, {delivery}, measured {tested_at}. Not shown: other task families, models, environments, or real-world incidence.`
  - carried-forward (`currentness.state == "CARRIED_FORWARD"` only): `demonstrated on {model}; carried forward to {current_model} under the sentinel rule; not re-validated on {current_model}.`

**Derivation.** `expected_evidence_scope()` in `scripts/validate_conformance.py` derives the row from the receipt O5 already resolves from the card's `Receipt:` clause under `--harness-root`. Carried-forward is decided from `currentness.state` only. SERS receipts carry no `scope_carried_forward` key. The `verdict_scope` object is never printed. Missing or non-string fields read the harness defaults (`unknown task family`, `unknown model`, `unknown delivery`, `unknown date`, `current model`) through `_string_field`, which mirrors `skill_harness/sitegen/render.py::_string_field`.

**KEEP wording source.** `SCOPE_LINE_TEMPLATE` and `SCOPE_LINE_CARRIED_TEMPLATE` are constants in `scripts/validate_conformance.py`, commented as coming from `skill_harness/sitegen/render.py::_scope_line` (inline f-strings there; no named constant in the harness).

**Card-files contract.** `scripts/validate_card_files.py` adds `Evidence scope` to `REQUIRED_EVIDENCE_ROWS`. Presence is this script's contract; the value is conformance O5's.

**Conformance O5.** Checks the value, including the no-receipt case O5 used to skip by returning CANNOT-CHECK, and refuses an empty row with its own message. Unresolvable receipt files (missing or unreadable JSON) keep `unresolvable = True` so a history link this run cannot load does not invent `UNMEASURED` and refuse a correct `NOT DEMONSTRATED` row.

**Drift test.** `case_scope_line_drift_vs_harness_render` imports `_scope_line` from `<SKILL_HARNESS_ROOT>/src`, renders the KEEP fixtures through it, strips the HTML wrapper, unescapes, and asserts equality with the skills derivation. Without a harness root it skips with a named reason. **N1:** it asserts `harness_render.__file__` lies under `SKILL_HARNESS_ROOT`, so an editable install of another checkout cannot silently answer the drift question.

**CI.** `.github/workflows/tests.yml` step `Evidence scope drift against skill-harness` clones `MrBinnacle/skill-harness` at its default branch, `pip install -e` that checkout in that step only, runs the conformance suite with `SKILL_HARNESS_ROOT` on ubuntu-latest, and refuses a skip.

**Changeset.** `.changeset/issue-354-evidence-scope.md` declares **major**, citing ADR 0002: "Changing the install path, or the on-disk shape of a card, is a major change."

## Acceptance criteria

### 1. Fixture matrix through the validator entry point

Each case runs `scripts/validate_conformance.py` (or the card-files validator) as a subprocess on a real temp tree, or reads the live tree. Refusals name the card and the `Evidence scope` row.

| Fixture | What satisfies it | Test that pins it | Observed before / after |
|---|---|---|---|
| Published card missing `Evidence scope` | `REQUIRED_EVIDENCE_ROWS` includes `EVIDENCE_SCOPE_ROW` in `scripts/validate_card_files.py` | `case_missing_evidence_scope_row_is_rejected`, `case_evidence_scope_row_present_clears_it` in `scripts/test_validate_card_files.py` | Before: dropping the row from `REQUIRED_EVIDENCE_ROWS` left the suite green and the card accepted. After: the case is red without the row and green with it; the refusal names `skills/engineering/scopeless-card` and `Evidence scope`. |
| No-receipt card whose row is anything but the `UNMEASURED` sentence | `evidence_scope_breaches` compares the stated row to `expected_evidence_scope([])`; O5 returns FAIL on a breach | `case_evidence_scope_no_receipt_wrong_sentence_is_fail`; harness-root half: `case_evidence_scope_no_receipt_wrong_sentence_with_harness_root_is_fail` | Before: a wrong row on a no-receipt card was O5 CANNOT-CHECK without `--harness-root`, and CANNOT-CHECK with it when the scope branch was disabled. After: O5 is FAIL in both modes; detail names the card, `Evidence scope`, and both sentences. |
| CANT_TELL_YET receipt with a row reading `Shown here: ...` | Scope check runs after receipt resolution and before a CANT verdict when the comparison itself is fine | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` | Before: O5 never compared the scope sentence. After: FAIL; refusal names the card, the row, `Shown here` and `NOT DEMONSTRATED`. |
| KEEP + `verdict_scope`, exact scope line passes | Row equals the derivation from the SERS-shaped receipt; drift also compares that derivation to harness `_scope_line` | `case_evidence_scope_keep_with_scope_exact_passes`; drift case | Before: the branch had rendered `DEMONSTRATED — {scope}.`, which is not skill-harness's wording. After: the exact R2 fixture sentence passes O5. |
| KEEP + `verdict_scope`, one-word change refused | `evidence_scope_breaches` returns FAIL on any mismatch | `case_evidence_scope_keep_one_word_change_is_fail` | After: replacing `trap-discipline` with `trap discipline` is FAIL; refusal names `Evidence scope` and both sentences. |
| Carried-forward KEEP | Carried-forward decided from `currentness.state == "CARRIED_FORWARD"` only | `case_evidence_scope_carried_forward_beats_standard` | Before: the branch used `scope_carried_forward` / wrong DEMONSTRATED sentences. After: the sentinel-rule sentence passes; writing the standard `Shown here: …` sentence on the same receipt is FAIL. |
| Quarantine card with no row passes | Published-card walk excludes `_quarantine/` | `case_evidence_scope_quarantine_card_with_no_row_passes` (conformance); `case_quarantine_card_with_no_row_is_exempt` (card-files) | Quarantine owes no row; O5 stays CANNOT-CHECK on the published fixture card and the live gate stays green. |
| Scoreboard still passes a card carrying the new row | `Evidence scope` is not a scoreboard controlled field | `case_scoreboard_passes_a_card_carrying_evidence_scope`; live `scripts/validate_scoreboard.py` | After: `validate_scoreboard.py` PASS still reports `records derive 14 admitted, 1 measured…`. |

R2 extras that also run through the entry point:

- `case_evidence_scope_keep_without_delivery_is_unknown_delivery` — `delivery_mechanism` absent yields `unknown delivery`.
- `case_evidence_scope_keep_missing_model_id_reads_unknown_model`
- `case_evidence_scope_keep_missing_task_family_reads_unknown_task_family`
- `case_evidence_scope_keep_missing_tested_at_reads_unknown_date`
- `case_evidence_scope_keep_non_string_scope_field_reads_default`
- `case_evidence_scope_carried_forward_missing_subject_model_reads_current_model`
- `case_evidence_scope_empty_row_is_refused_with_its_own_message` — empty row uses the empty-row message (R4).
- `case_evidence_scope_history_link_to_missing_file_passes` and `case_evidence_scope_history_link_to_invalid_json_passes` (F1c).
- `case_evidence_scope_live_tree_rows_match_the_closed_set` — live tree: 13 UNMEASURED + pull-rebase NOT DEMONSTRATED, no fourth shape.

### 2. Mutants killed by named assertions

Each mutant was applied to `scripts/validate_conformance.py` (or `scripts/validate_card_files.py` for the card-files contract), the named case was re-run, and the named assertion went red. The unmutated tree stayed green on the same case.

| Mutant | Change | Assertion that turns red | Test name |
|---|---|---|---|
| M11 | `unknown task family` → `unknown family` (code default) | a KEEP receipt without task_family reads unknown task family; drift equality for missing/non-string task_family | `case_evidence_scope_keep_missing_task_family_reads_unknown_task_family`; `case_scope_line_drift_vs_harness_render` |
| M12 | `unknown date` → `unknown` | a KEEP receipt without tested_at reads unknown date; drift equality | `case_evidence_scope_keep_missing_tested_at_reads_unknown_date`; drift |
| M13 | `unknown model` → `unknown` | a KEEP receipt without model_id reads unknown model; drift equality | `case_evidence_scope_keep_missing_model_id_reads_unknown_model`; drift |
| M14 | `current model` → `the current model` (code default, not the comment) | a carried-forward KEEP without subject_model reads current model; drift equality | `case_evidence_scope_carried_forward_missing_subject_model_reads_current_model`; drift |
| M15 | `_string_field` accepts any non-`None` value | a non-string model_id / task_family reads the default; O5 accepts the default sentences | `case_evidence_scope_keep_non_string_scope_field_reads_default`; drift |
| M26 | `if scope_breaches:` under `if not linked_receipts:` → `if False:` | a no-receipt card with a wrong Evidence scope sentence is FAIL under `--harness-root`; refusal names card and row | `case_evidence_scope_no_receipt_wrong_sentence_with_harness_root_is_fail` |
| M23 | remove `unresolvable = True` for a missing receipt file | O5 is PASS when a history link names a missing file and the row is correct | `case_evidence_scope_history_link_to_missing_file_passes` |
| M24 | remove `unresolvable = True` for unreadable JSON | O5 is PASS when a history link names invalid JSON and the row is correct | `case_evidence_scope_history_link_to_invalid_json_passes` |
| N1 | import `skill_harness` from a decoy checkout while `SKILL_HARNESS_ROOT` names another | the drift import of render.py lies under SKILL_HARNESS_ROOT | `case_scope_line_drift_vs_harness_render` |
| R4 | delete the `if not stated:` empty-row branch | the empty-row refusal names the card and uses the empty-row message | `case_evidence_scope_empty_row_is_refused_with_its_own_message` |
| Drift standard word | `real-world incidence` → `real world incidence` in `SCOPE_LINE_TEMPLATE` | skills derivation equals harness `_scope_line` for standard KEEP fixtures | `case_scope_line_drift_vs_harness_render` |
| Drift carried word | extra period after `sentinel rule` in `SCOPE_LINE_CARRIED_TEMPLATE` | skills derivation equals harness `_scope_line` for carried-forward fixtures | `case_scope_line_drift_vs_harness_render` |
| Drift default word | `unknown task family` → `unknown family` in the `_string_field` default | drift equality for missing/non-string task_family | `case_scope_line_drift_vs_harness_render` |
| Cant-tell-yet sentence | `return SCOPE_NOT_DEMONSTRATED_FMT…` → `return SCOPE_NO_RECEIPT` | the refusal names the card, the row, `Shown here` and `NOT DEMONSTRATED` | `case_evidence_scope_cant_tell_yet_shown_here_is_fail` |
| Carried-beats-standard | carried derivation returns the standard template | carried-forward derivation is the harness sentinel-rule sentence | `case_evidence_scope_carried_forward_beats_standard` |
| No-receipt-no-harness | O5 skips the scope check when `harness_root is None` | a no-receipt card with a wrong Evidence scope sentence is FAIL | `case_evidence_scope_no_receipt_wrong_sentence_is_fail` |
| Keep-one-word-row | `evidence_scope_breaches` always returns `[]` | KEEP + one-word scope-line change is FAIL | `case_evidence_scope_keep_one_word_change_is_fail` |
| Missing-row-card-files | drop `EVIDENCE_SCOPE_ROW` from `REQUIRED_EVIDENCE_ROWS` | a card without the Evidence scope row is rejected | `case_missing_evidence_scope_row_is_rejected` |

Every clause this ticket adds has a mutant above that its named assertion kills. Base (unmutated) runs of the same cases stay green.

### 3. Drift test vs skill-harness

- Passes against the skill-harness checkout CI uses (`MrBinnacle/skill-harness` default branch), installed editable: `SKILL_HARNESS_ROOT=/home/agent/skill-harness-checkout python scripts/test_validate_conformance.py` → `PASS: conformance v4 suite, all cases correct`, with `skills derivation equals harness _scope_line` for all ten fixtures (standard with/without `delivery_mechanism`, without `model_id`/`task_family`/`tested_at`, non-string `model_id`/`task_family`, carried-forward with/without `subject_model`, non-string `subject_model`) and `the drift import of render.py lies under SKILL_HARNESS_ROOT`.
- Without a harness root the suite still passes and prints a named skip: `scope-line drift skipped: SKILL_HARNESS_ROOT is not set to a skill-harness checkout…`.
- Fails when one word of a skills template constant changes (M11–M15 and the three Drift-* mutants above).
- CI step in `.github/workflows/tests.yml` (`Evidence scope drift against skill-harness`) clones the harness, installs it editable in that step only, runs the suite with `SKILL_HARNESS_ROOT`, and refuses a skip.

### 4. Full validator suite and release gate, LF and CRLF

At head `33a66eb` (LF working tree):

| Command | Result |
|---|---|
| `python scripts/test_validate_conformance.py` | PASS (drift skipped without `SKILL_HARNESS_ROOT`, named reason printed) |
| `SKILL_HARNESS_ROOT=… python scripts/test_validate_conformance.py` | PASS (drift ran, N1 held) |
| `python scripts/test_validate_card_files.py` | PASS |
| `python scripts/validate_card_files.py` | PASS — 14 published cards; every EVIDENCE.md states … and Evidence scope |
| `python scripts/validate_scoreboard.py` | PASS — `records derive 14 admitted, 1 measured, 2 retired, 4 solutions looking for a problem` |
| `python scripts/release_gate.py` | `RELEASE GATE: PASS - surfaces healthy at version 3.0.1` |
| `python scripts/validate_conformance.py --root .` | PASS — 46 PASS, 0 FAIL, 14 CANNOT-CHECK |
| `python scripts/validate_conformance.py --root . --harness-root …` | PASS — 47 PASS, 0 FAIL, 13 CANNOT-CHECK |
| `python scripts/test_validate_skill_formats.py` | PASS |
| `python scripts/validate_skill_formats.py` | PASS — 47 skill folder(s), 153 file(s) |
| `python scripts/test_validate_eval_corpora.py` + `validate_eval_corpora.py` | PASS |
| `python scripts/test_validate_brand_kit.py` + `validate_brand_kit.py` | PASS |
| `python scripts/test_validate_voice_provenance.py` + `validate_voice_provenance.py` | PASS |
| `python scripts/test_readme_admission_lead.py` | PASS |

CRLF checkout (text files converted to CRLF; `styles/**` and `scripts/vendor/**` left LF per `.gitattributes`; `scripts/validate_conformance.py` stays CRLF as on main):

| Command | Result |
|---|---|
| `python scripts/test_validate_card_files.py` | PASS |
| `SKILL_HARNESS_ROOT=… python scripts/test_validate_conformance.py` | PASS |
| `python scripts/validate_scoreboard.py` | PASS |
| `python scripts/release_gate.py` | `RELEASE GATE: PASS` |
| `python scripts/validate_conformance.py --root .` | PASS — 46 PASS, 0 FAIL, 14 CANNOT-CHECK |

`scripts/validate_conformance.py` stays CRLF in the index (as on main). The diff on that file is content (+204/−3), not a whole-file EOL rewrite.

### 5. Changeset

`.changeset/issue-354-evidence-scope.md` (in the diff) declares `"mrbinnacle-skills": major` and quotes ADR 0002 (`docs/adr/0002-a-release-is-a-delivery-event.md`): "Changing the install path, or the on-disk shape of a card, is a major change."

### 6. PR body counts from the final head

Every count, SHA, and file list above was taken from `git diff --shortstat origin/main...HEAD`, `git diff --name-only origin/main...HEAD`, `git diff --numstat`, and a live census of `skills/*/*/EVIDENCE.md` at head `33a66eb3fe2b1b2be056cdabade590cacfa2e19b`. No runner open-time note from an earlier round is carried here.

## Revisit note (ticket)

O5's receipt resolution does serve the no-receipt case: with no `Receipt:` clause, `_linked_receipt_dicts` returns an empty list and `expected_evidence_scope([])` is `UNMEASURED — no receipt.`, which `evidence_scope_breaches` checks in both harness-root and no-harness-root modes. The check lives in `evidence_scope_breaches` (called from `check_receipt_agreement`), not a separate validator.

## Round-2 findings closed

- **F1(a).** Field defaults and the non-string rule are pinned by the missing-field and non-string fixtures (M11–M15 above) and by the expanded drift set. The drift lines still equal harness `_scope_line` on those shapes.
- **F1(b).** The no-receipt wrong-row case runs under `--harness-root` and is FAIL, not CANNOT-CHECK (M26).
- **F1(c).** History links to a missing file and to invalid JSON keep a correct `NOT DEMONSTRATED` row PASS on O5 (M23, M24).
- **F2.** Counts, SHAs, and the file list in this body come from commands at head `33a66eb`. No stale runner note remains.
- **N1.** The drift test asserts `harness_render.__file__` lies under `SKILL_HARNESS_ROOT`.
- **R6 / existing guarantees.** Every mutant listed as killed above stays killed; the validators and `release_gate.py` pass at head on LF and on a CRLF checkout.

## Files named in this body

Only files present in `git diff --name-only origin/main...HEAD` at head `33a66eb` are named as changed. This scratch body is a runner hand-off; it is removed before the push and is not part of the published diff.
