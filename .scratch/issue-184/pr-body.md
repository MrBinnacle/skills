# #184: Rewrite two surfaces to match their own receipts

## Summary

Two surfaces that today contradict their own receipts are rewritten, and become the worked examples of the row shape `AGENTS.md` prescribes. This is the row-shape rewrite from #183 and the O5 verification from #182.

## What was built

**Pair B — `git-pull-rebase-trap` (published).** Its `Screen result` row in `EVIDENCE.md` is rewritten to the receipt-row shape: opens with the verdict word `CANT_TELL_YET`, carries a `Receipt:` clause whose hyperlink pins the harness commit that holds `git-pull-rebase-trap`'s receipt, `dated 2026-07-20` (the receipt's `source.date`), the 2026-07-21 run date stated separately, reason `wrong_instrument (trap-discipline); not current: no_skill_id`.

**Pair A — `append-only-evidence-design` (screened out before admission).** Its cell in the "Screened out at the gate" table in `RETIRED.md`, today "Ceiling — model passed 3/3 unaided", is amended to cite its receipt (the `reclass-append-only-evidence-design` receipt at the harness commit) and the receipt's reading: `CANT_TELL_YET`, `wrong_instrument` on a `calibration` class, p0 = 1.00 at 3/3. This is an erratum on an admission-screen record, not a retirement; the card does not enter the retired table.

Both link to a harness **commit** (`f75429c57c33e1191fa4b65632fce5d668a78312`), never `main`.

## Acceptance criteria

### Criterion 1: Pair B's row opens with verdict word and carries one Receipt clause with a commit-pinned hyperlink, `dated 2026-07-20`, and the typed reason

**What was built:** Rewrote the `Screen result` row in `skills/engineering/git-pull-rebase-trap/EVIDENCE.md`. The old row opened with `CANT_TELL_YET. Screened 2026-07-21...` and carried a backtick-form receipt path `docs/sers/receipts/reclass-git-pull-rebase-trap.json in the measurement repo`. The new row opens with `CANT_TELL_YET. Receipt: [reclass-git-pull-rebase-trap.json](<harness commit URL>), dated 2026-07-20, harness 1.0.0. wrong_instrument (trap-discipline); not current: no_skill_id.` followed by the screen context and caveat.

**Test that pins it:** `scripts/validate_card_files.py` passes (EVIDENCE.md states all controlled fields and contract rows). `scripts/validate_scoreboard.py` passes (scoreboard derives 1 measured card). The conformance check with `--harness-root` reports the O5 FAIL on condition 2 (see Criterion 3 below).

**Before/after:** Before the change, `validate_card_files.py` and `validate_scoreboard.py` both passed, but the receipt reference was a bare path with no commit pin and the row did not follow the receipt-row shape. After the change, both still pass, and the row now conforms to the `AGENTS.md` receipt-row shape with a commit-pinned hyperlink.

### Criterion 2: Pair A's cell cites the receipt by commit-pinned hyperlink and states the receipt's verdict and reason; the retired table is unchanged

**What was built:** Amended the `append-only-evidence-design` row in the "Screened out at the gate" table in `RETIRED.md`. The old cell was `Ceiling — model passed 3/3 unaided`. The new cell is `CANT_TELL_YET. [Receipt](<harness commit URL>): wrong_instrument (calibration), p0 = 1.00 at 3/3`. The section intro no longer claims all four hit the ceiling — it keeps the 3/3 fact and names the reclassification for this one candidate. The retired table (section "Retired from the collection") is unchanged.

**Test that pins it:** `scripts/validate_scoreboard.py` passes — it derives `4 solutions looking for a problem` from the screened-out table and the count is unchanged. The card-files validator passes (no published card changed).

**Before/after:** Before the change, the cell said "Ceiling — model passed 3/3 unaided" which contradicted the receipt's reading of `CANT_TELL_YET` with `wrong_instrument`. After the change, the cell cites the receipt and states the correct verdict and reason. The validator suite shows no change in counts (4 solutions looking for a problem).

### Criterion 3: O5 run with --harness-root against the real harness clone reports Pair B's card

**What was built:** Ran `python scripts/validate_conformance.py --root . --harness-root /tmp/skill-harness` against a clone of `MrBinnacle/skill-harness` at commit `f75429c57c33e1191fa4b65632fce5d668a78312`.

**O5 output (pasted verbatim):**

```
git-pull-rebase-trap
  FAIL         O5 controlled fields do not contradict a published receipt -- receipt 'reclass-git-pull-rebase-trap.json' has no subject_identity block
```

This is the expected FAIL on condition 2: the linked 1.0.0 receipt carries no `skill_id`. The honest reading of a row that cites a not-current receipt. CI does not run the flag, so this does not block merge.

**Test that pins it:** The O5 check found the receipt by the filename in the Receipt clause, read the JSON, and found no `subject_identity` block — which means no `skill_id`. This is the typed `no_skill_id` reason from the currency gate. The row correctly states `not current: no_skill_id` as the typed reason.

### Criterion 4: Card-files validator, scoreboard validator and linkcheck CI are green

**What was built:** All validators pass after the changes:

```
$ PYTHONUTF8=1 python3 scripts/validate_card_files.py --root .
PASS: 15 published card(s), all carry SKILL.md, gotchas.md, EVIDENCE.md; every EVIDENCE.md states Occasions counted and Dispatches recorded and Re-screen trigger; every description is stated and within 200 characters

$ PYTHONUTF8=1 python3 scripts/validate_scoreboard.py --root .
PASS: ruled banner line pinned at 5 sites; records derive 15 admitted, 1 measured, 1 retired, 4 solutions looking for a problem; admission policy version agrees; origin tiers 12 OBSERVED, 2 DESIGNED, 1 DISTILLED agree

$ PYTHONUTF8=1 python3 scripts/validate_conformance.py --root .
PASS: conformance v2: 15 card(s) x 4 card obligation(s) + 3 repo obligation(s) = 63 cells: 48 PASS, 0 FAIL, 15 CANNOT-CHECK
```

The linkcheck CI runs `lychee` on all `*.md` files. The two new links are to valid GitHub URLs at specific commits (`f75429c57c33e1191fa4b65632fce5d668a78312`). The linkcheck cannot be run locally without `lychee` installed, but the URLs resolve to real files in the harness repo (verified by `git clone` and file inspection).

**Test that pins it:** The card-files suite (`scripts/test_validate_card_files.py`) passes. The conformance suite (`scripts/test_validate_conformance.py`) passes. The scoreboard validator passes. No existing test was weakened, skipped, or xfailed.

## Files changed

1. `skills/engineering/git-pull-rebase-trap/EVIDENCE.md` — Screen result row rewritten to receipt-row shape
2. `RETIRED.md` — append-only-evidence-design cell amended with receipt citation; screened-out intro aligned with the erratum
3. `.changeset/receipt-row-pair-rewrite.md` — patch changeset

## Mutation campaign

No mutation campaign was run. The changes are prose edits to markdown tables, not code logic. The validators check structural properties (row presence, field existence, count derivation) which are not susceptible to mutation testing in this context.