# Evidence body — #177: repair DESIGN.md enforcement claim

## What changed

DESIGN.md carried an active instruction telling readers to treat the token set as unenforced and
to discount a green CI run. The token set has been enforced by `validate_brand_kit.py` since
2026-08-24. The stale passage was replaced with the truth: the check exists, runs in CI as a
required status check, and a green run is compliance. The two open gaps are stated with the
live asset paths from `known_gaps` (`lockup-horizontal.svg`, `lockup-stacked.svg`,
`social-preview.png`).

## Acceptance criteria

### Criterion 1: Stale enforcement claim removed

**Built:** The phrase "Treat the token set as unenforced" and its citation of
`known_gaps.not_enforced` are gone from DESIGN.md.

**Test:** `scripts/test_design_enforcement_claim.py` — `case_stale_enforcement_claim_removed`
and `case_stale_citation_removed`.

### Criterion 2: Truth stated

**Built:** DESIGN.md now names `validate_brand_kit.py`, describes its three checks, states it
runs in the `validator` job on both OS cells, and is a required status check on the protected
branch. The closing line reads: "A green CI run is compliance, not silence."

**Test:** `case_enforcement_named`, `case_enforcement_described`, `case_ci_gate_mentioned`
(pins the phrase `required status check`).

### Criterion 3: Two remaining gaps quoted from known_gaps

**Built:** The section states both open gaps with the live paths `known_gaps` records:
`assets/social-preview.png`, `assets/lockup-horizontal.svg`, `assets/lockup-stacked.svg`.

**Test:** `case_social_preview_gap_mentioned` and `case_compact_mark_gap_mentioned`. The
compact-mark case cross-reads `tokens.json > known_gaps` and refuses a DESIGN.md that names
any other lockup path (a `lockup-staged.svg` typo fails).

### Criterion 4: Green-run instruction removed

**Built:** "Read a green CI run as silence on this file, not as compliance with it" is gone.

**Test:** `case_green_run_instruction_removed`.

### Criterion 5: Adjacent statements preserved

**Built:** "Author new marks with `currentColor`" and the `<img>` warning remain.

**Test:** `case_currentcolor_rule_preserved` and `case_img_fallback_preserved`.

### Criterion 6: Open decisions updated

**Built:** The "two colour gaps" open-decision entry is removed.

**Test:** `case_open_decisions_no_longer_stale`.

## Review correction

The first implement pass wrote `assets/lockup-staged.svg` (no such file). The real path is
`assets/lockup-stacked.svg`, as `known_gaps.compact_mark_still_in_the_lockups` records. The
suite that shipped with that pass accepted the typo via a loose `"compact mark" and "lockup"`
substring match, and the suite was not wired into `.github/workflows/tests.yml`, so CI could
not have caught it. Both defects are corrected here: paths are pinned against `known_gaps`,
and the suite runs as step "DESIGN.md enforcement-claim suite" beside the brand-kit check.

## Mutation

Replacing `lockup-stacked` with `lockup-staged` in DESIGN.md turns the suite red on
`compact mark gap stated with live lockup paths`. Restoring the real path greens it again.
