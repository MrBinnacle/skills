# #183: Receipt-based disposition workflow in AGENTS.md

## What changed

Added seven procedural elements to the rotation and harvest pass in AGENTS.md, implementing the receipt-based disposition workflow specified in the resolution documents referenced by the ticket.

## Acceptance criteria

### AC1: Each of the seven items present as a step inside the ritual it names

| Item | Where it lives | Line(s) |
|---|---|---|
| Two triggers | Paragraph before "Harvest first" in rotation pass intro | 335-340 |
| Inputs row | Harness release row in Inputs table | 356 |
| Currency step | Step 3 in pass sequence | 442-464 |
| Record step | Step 4 in pass sequence | 465-471 |
| Dispose step | Step 5 in pass sequence | 472-477 |
| Retirement record | Receipt link added to retirement execution paragraph | 278-283 |
| O5 step and Done-when bar | Step 10 in pass sequence | 625-628 |

**Test:** Manual inspection of AGENTS.md structure. Each item is present at the named location. The validators (`validate_card_files.py`, `validate_scoreboard.py`, `validate_conformance.py`) all pass, confirming no structural drift was introduced.

**Before/after:** Before the change, the rotation pass had 7 steps (1-7) with no currency gate, no record step, no dispose step, and no O5 step. After: 11 steps (1-11) with all seven items integrated. Validators were green before and remain green after.

### AC2: Retirement section names exactly two routes

**Test:** `grep -n -A2 'leaves two ways' AGENTS.md` confirms the Retirement section lists exactly:
- **Harness cut** — widened from the former "Screen null"
- **Pre-registered platform-fix** — unchanged

**Before/after:** The old first route was "Screen null". Replaced with "Harness cut" per the ticket's widening. The section now reads "A skill leaves two ways:" with exactly two bullet points. No third route added.

### AC3: card-files validator, scoreboard validator and linkcheck CI are green

**Test results (all PASS):**

```
validate_card_files.py: PASS: 15 published card(s), all carry SKILL.md, gotchas.md, EVIDENCE.md; every EVIDENCE.md states Occasions counted and Dispatches recorded and Re-screen trigger; every description is stated and within 200 characters

validate_scoreboard.py: PASS: ruled banner line pinned at 5 sites; records derive 15 admitted, 1 measured, 1 retired, 4 solutions looking for a problem; admission policy version agrees; origin tiers 12 OBSERVED, 2 DESIGNED, 1 DISTILLED agree

validate_conformance.py: PASS: conformance v2: 15 card(s) x 4 card obligation(s) + 3 repo obligation(s) = 63 cells: 48 PASS, 0 FAIL, 15 CANNOT-CHECK.
```

Additional validators also pass: `validate_eval_corpora.py` (15 corpora), `validate_skill_formats.py` (129 files), `validate_voice_provenance.py` (6 specimens), `validate_brand_kit.py` (brand kit 0.1.0 enforced).

Linkcheck runs in CI on PRs; the de-personalization gate (pre-commit) also passes on every commit.

**Before/after:** All validators were green on main before this branch. All remain green after. No regressions.

### AC4: PR diff touches AGENTS.md only

**Test:** `git diff main...HEAD --stat` shows:

```
 AGENTS.md | 79 ++++++++++++++++++++++++++++++++++++++++++++++++++++-----------
 1 file changed, 65 insertions(+), 14 deletions(-)
```

No other files modified. No test files, no validator scripts, no card files changed.

## Mutation campaign

No mutants were applied. This is a documentation-only change to AGENTS.md — there is no executable code to mutate. The validators that verify repository conformance are the test harness, and they all pass against the edited file.

## Commits

1. `68c29f6` — docs(agents): add two triggers for receipt-based disposition (#183)
2. `ce113d0` — docs(agents): add harness release row to Inputs table (#183)
3. `cb6ab9e` — docs(agents): add currency gate step with typed receipt-staleness reasons (#183)
4. `8e2745e` — docs(agents): add record and dispose steps for receipt-based disposition (#183)
5. `5b40696` — docs(agents): rename Screen null to Harness cut; add receipt link to retirement record (#183)
6. `1b40aec` — docs(agents): add O5 step with --harness-root and update Done-when bar (#183)
