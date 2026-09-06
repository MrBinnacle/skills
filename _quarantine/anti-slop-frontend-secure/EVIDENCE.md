# EVIDENCE — anti-slop-frontend-secure

Provenance record per the collection's evidence convention (see top-level README ->
"The receipts, explained"). Fields are honest by construction: UNMEASURED means exactly
that, and ABSENT means the record does not exist.

## NOT ADMISSIBLE — the origin occurrence is ABSENT

`ADMISSION.md` criterion 1 requires an unaided failure that was **observed, not
predicted**. Criterion 2 requires occasions that were **counted, not predicted**. This
card has neither. A search of this repository's `dispositions/`, this card's own
provenance comment, the linked review record, the issue history of `skills#214`, and the
sibling measurement repository's evidence store returned no dated occurrence in which a
current frontier model, given this situation and without this card, produced a frontend
artifact that failed one of the six gates.

The oracle in this folder is built, tested and parser-backed. That changes nothing about
admission. The ticket says so in its own words: *without a dated origin occurrence the
candidate cannot clear `ADMISSION.md` criteria 1 and 2 no matter how good the oracle is.*

**This file is deliberately left in a state that fails
`scripts/validate_card_files.py`.** The `Occasions counted` row states `0` and carries no
`RECURRENCE-THIN` label. That label is required below two counted occasions and would
make this file pass the row checks, because the arithmetic in that script cannot tell
`0` from `1` once the label is present — it tests thinness, not existence, and criterion
1 is not among the rows it checks. Adding the label to make a promotion green would use a
gate's blind spot to defeat the policy the gate exists to serve. **Do not add the label.
Count an occasion, or leave the card in `_quarantine/`.**

### What a reader must not do with this file

An earlier build of this candidate, on the held branch for `skills#230`, stated an
origin: `OBSERVED 2026-08-09`, a dashboard artifact using `innerHTML`, an unapproved
analytics host, and an embedded key. That date is the date this card was transcribed from
a Notion page, recorded in the session note for that day as a card-intake sweep and not
as an incident. No file in any of the three repositories corroborates the dashboard, the
host or the key, and the two independent reviews commissioned against that branch never
examined the claim. It is an asserted occurrence on an unmerged branch and it is not
carried forward here.

An `EVIDENCE.md` with an invented or undated occurrence is worse than no card, because it
defeats the check that exists to catch exactly that.

## Fields

| Field | Value |
|---|---|
| **Origin** | **ABSENT.** No dated, observed occurrence has been recorded for this card. What is dated is the card's materialisation: 2026-08-09, transcribed from the operator's Notion Skills Library page as a faithful copy of its Core Execution Flow, with the page's scanner scripts listed in an attachment that was never attached. A materialisation date is a record of when a description was copied, never a record of a failure happening. The two are not interchangeable and this row does not trade one for the other. |
| **Occasions counted** | 0. Nothing to cite, so nothing is cited. The search that produced this zero covered `dispositions/`, `RETIRED.md`, this card's provenance comment, the `skills#214` issue history, and the sibling measurement repository's evidence store and receipts. A zero here is a finding about the record, not a claim that the failure never happens; a threat model is not an occurrence and is not counted as one. |
| **Dispatches recorded** | No recorded dispatch, measured 2026-09-06. The figure is a tautology and is stated only so the row is not blank: the card has sat in `_quarantine/` since it was written, so it was never installed and the platform counter had nothing it could have counted. It is not evidence about demand, recurrence or worth. |
| **Validated against** | The oracle, not the card's necessity. `test_oracle.py` runs 25 assertions over 21 fixtures and 5 ablation arms, and every gate carries a fixture whose verdict a byte scan settles wrongly, asserted on each run against both the fixture's declared verdict and the oracle's observed one. Five hand-run mutations were each killed by a named assertion (`gotchas.md`, second entry). This establishes that the instrument works. It establishes nothing about whether the instrument is needed. |
| **Screen result** | UNMEASURED. This card has the shape a screen can measure — a frozen empirical contract with fixtures and counterfixtures, which `AGENTS.md` step 4 names as the only shape the measurement harness returns a real verdict on. The fixture pair exists here, in `fixtures.json`. What does not exist is an admissible run: no with-skill and without-skill screen has been commissioned, so there is no result to report and none is invented. The refusal is availability, not applicability. |
| **Paired verdict** | UNMEASURED (see Screen result — screenable in principle, no admissible run in the store). Methodology reference: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md). |
| **Standing cost** | Description 195 characters, paid on every turn while the card is model-invocable. Folder 120,015 B across the seven files other than this one (measured 2026-09-06), of which the three scripts are 78,010 B and the two fixture files 28,479 B; all of it is loaded only on retrieval. This file is excluded from its own figure on purpose: writing the total into the file changes the total, and a self-referencing byte count is stale the moment it is recorded. The cost is stated for completeness and does not bear on admission, which fails earlier. |
| **Re-screen trigger** | Two events, either of which changes the answer. First, a dated occurrence is recorded: a frontier model, without this card, ships a frontend artifact that one of the six gates would have caught. Record it in `gotchas.md` where it happened, then count it here. Second, the platform or the host makes the failure undetectable-by-need — a runtime that refuses a blocked sink outright, or a deployment that enforces a policy the artifact cannot opt out of. That retires the card against this criterion rather than promoting it. |

## What would settle this

The ticket's own triage comment set the cheap test before the expensive one: search the
session corpus for dated instances where a current frontier model, given this situation
and without this card, failed the job the card claims to fix. That count was requested and
its result was never posted to the ticket. This file is that result: zero.

Two outcomes follow, and the ticket named both. One or more occasions found, and the
oracle already built here becomes live work with the occasion count as its evidence base.
Zero occasions found, and the candidate is in the position this repository retired a card
for on 2026-08-31, when `skill-necessity-gate` was removed because its own evidence record
counted zero occurrences while `ADMISSION.md` required one.

The disposition on a zero is to leave the candidate in `_quarantine/`. That is where it
is, and this build does not move it.
