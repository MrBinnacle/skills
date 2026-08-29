# Evidence body — #177: repair DESIGN.md enforcement claim

## What changed

DESIGN.md carried an active instruction telling readers to treat the token set as unenforced and
to discount a green CI run. The token set has been enforced by `validate_brand_kit.py` since
2026-08-24. The stale passage was replaced with the truth: the check exists, runs in CI as a
required status check, and a green run is compliance.

## Acceptance criteria

### Criterion 1: Stale enforcement claim removed

**Built:** The phrase "Treat the token set as unenforced" and its citation of
`known_gaps.not_enforced` at the former line 115 are gone from DESIGN.md.

**Test:** `scripts/test_design_enforcement_claim.py` — `case_stale_enforcement_claim_removed`
and `case_stale_citation_removed`.

**Observed:** Before the fix, both assertions FAIL — the phrase and the citation are present in
the live file. After the fix, both PASS — neither string appears.

### Criterion 2: Truth stated

**Built:** DESIGN.md now names `validate_brand_kit.py`, describes its three checks, states it
runs in the `validator` job on both OS cells, and is a required status check on the protected
branch. The closing line reads: "A green CI run is compliance, not silence."

**Test:** `scripts/test_design_enforcement_claim.py` — `case_enforcement_named`,
`case_enforcement_described`, `case_ci_gate_mentioned`.

**Observed:** Before the fix, all three FAIL — `validate_brand_kit.py` is not mentioned, no
enforcement statement exists, no CI gate reference exists. After the fix, all three PASS.

### Criterion 3: Two remaining gaps quoted

**Built:** The section now names the two open gaps from `known_gaps`:
`social_preview_raster_is_unreadable` (raster has no text layer, closing via #62) and
`compact_mark_still_in_the_lockups` (retired MB mark still drawn, replacement is a design
decision).

**Test:** `scripts/test_design_enforcement_claim.py` — `case_social_preview_gap_mentioned` and
`case_compact_mark_gap_mentioned`.

**Observed:** Before the fix, both FAIL — neither gap is referenced. After the fix, both PASS.

### Criterion 4: Green-run instruction removed

**Built:** The sentence "Read a green CI run as silence on this file, not as compliance with it"
is gone.

**Test:** `scripts/test_design_enforcement_claim.py` — `case_green_run_instruction_removed`.

**Observed:** Before the fix, this assertion actually PASSES — the exact phrasing was already
absent from the file (the passage had been partially edited at some point). The test still pins
the negative: after the fix, it continues to PASS, confirming the instruction does not
re-appear.

### Criterion 5: Adjacent statements preserved

**Built:** The two `currentColor` rules remain intact: "Author new marks with `currentColor`"
and the warning that `currentColor` does not survive `<img src="...">`.

**Test:** `scripts/test_design_enforcement_claim.py` — `case_currentcolor_rule_preserved` and
`case_img_fallback_preserved`.

**Observed:** Both PASS before and after the fix, confirming no accidental deletion.

### Criterion 6: Open decisions updated

**Built:** The "two colour gaps" entry in the Open decisions section (which referenced the
closed `not_enforced` gap) is removed. The two remaining open decisions (primary line, block
count) remain.

**Test:** `scripts/test_design_enforcement_claim.py` — `case_open_decisions_no_longer_stale`.

**Observed:** Before the fix, FAIL — the open decisions section still referenced
`not_enforced`. After the fix, PASS.

## Gate results

All validators and suites pass after the change:

| Validator | Result |
|---|---|
| `test_validate_brand_kit.py` (41 cases) | PASS |
| `validate_brand_kit.py` | PASS: brand kit 0.1.0 enforced |
| `test_validate_card_files.py` | PASS |
| `validate_card_files.py` | PASS: 15 published cards |
| `validate_scoreboard.py` | PASS: banner line pinned, counts derived |
| `test_validate_skill_formats.py` | PASS |
| `validate_skill_formats.py` | PASS: 41 folders, 129 files |
| `test_validate_voice_provenance.py` | PASS |
| `validate_voice_provenance.py` | PASS: 6 specimens |
| `test_validate_eval_corpora.py` | PASS |
| `validate_eval_corpora.py` | PASS: 15 corpora, 48 cases |
| `test_validate_conformance.py` | PASS |
| `validate_conformance.py` | PASS: 63 cells, 48 PASS, 0 FAIL |
| `test_validate_spec_conformance.py` | PASS |
| `test_readme_admission_lead.py` | PASS |
| `test_validate_disposition_counts.py` | PASS |
| `test_design_enforcement_claim.py` (11 cases) | PASS |

## Mutation campaign

No mutations applied. This is a factual repair to documentation, not a code change. The test
suite pins the content assertions with no internal branching to mutate. The validator suite
(`test_validate_brand_kit.py`) already covers the enforcement mechanism with 41 cases including
poison controls for each of the three checks.
