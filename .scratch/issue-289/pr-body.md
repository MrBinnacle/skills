# Evidence body — issue #289 (G10 bump classification)

Branch: `agent/issue-289`. Ticket: refuse a changeset whose declared bump type contradicts its own diff, as ADR 0003 requires, in the blocking release gate.

## Acceptance criteria

### 1. A check refuses each of the four refusable classes

**What was built.** `scripts/release_gate.py` gains **G10**. It parses the surface prices from the ADRs on disk:

- `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` — `Renaming a card is a (\w+) change` and `Admitting or retiring one remains a (\w+) change`
- `docs/adr/0002-a-release-is-a-delivery-event.md` — `Corrections within a card are a (\w+)`

If an ADR is missing, unreadable, or no longer carries those sentences, and classification is needed, the run **fails closed** with a `G10:` line naming the ADR. The bump words `major` / `minor` / `patch` appear only as the ranking vocabulary (`BUMP_RANK`); the rule *rename → major* is never written in the checker.

The check derives the branch diff with `git diff --name-status -M <merge-base> HEAD`, classifies paths under `skills/*/*/` that actually carry a `SKILL.md` (so `skills/*/*/.claude-plugin/` and `evals/` do not masquerade as cards), and compares each pending changeset's declared level to the price the diff reaches. A rename and an addition in one diff resolve to **major** — the higher classification governs — and that sentence is stated in the module docstring and in the refusal path.

Case 4 runs in release mode: the version delta (`merge-base` package.json → HEAD package.json) must match what the release diff requires under the same prices. Both under-classification and over-classification are refused, because a botched release spends a version number permanently (ADR 0002).

**Tests that pin it.** `scripts/test_bump_classification.py`, 19 controls, each driving the shipped gate as a subprocess against a seeded git tree.

| Criterion | Control | Observed before G10 | Observed after G10 |
|---|---|---|---|
| Case 1: rename declared `patch` | `case_case1_rename_declared_patch_is_refused` | `RELEASE GATE: PASS` (defect accepted) | `G10: … renames a card directory … prices as major` |
| Case 1 / inversion: rename declared `minor` | `case_case1_rename_declared_minor_is_refused` | `RELEASE GATE: PASS` | `G10: … prices as major` — refused |
| Case 2: admission declared `patch` | `case_case2_add_declared_patch_is_refused` | `RELEASE GATE: PASS` | `G10: … adds or retires a card directory … prices as minor` |
| Case 2: retirement declared `patch` | `case_case2_remove_declared_patch_is_refused` | `RELEASE GATE: PASS` | `G10: … removed skills/engineering/old-card` |
| Case 3: no surface change, declared `minor` | `case_case3_no_surface_declared_minor_is_refused` | `RELEASE GATE: PASS` | `G10: … touches no file under skills/*/*/` |
| Case 3: no surface change, declared `major` | `case_case3_no_surface_declared_major_is_refused` | `RELEASE GATE: PASS` | same refusal, `major` named |
| Case 4: release delta `1.2.0 → 1.3.0` over a scripts-only diff | `case_case4_release_delta_under_required_is_refused` | `RELEASE GATE: PASS` at `1.3.0` | `G10: release version delta 1.2.0 -> 1.3.0 is minor, but the release diff touches no file under skills/*/*/` |
| Rename + add in one changeset | `case_higher_classification_governs_rename_plus_add` | `RELEASE GATE: PASS` | `G10: … prices as major` (patch refused; higher class governs) |

Every refusal asserts `G10:` and the specific reason, not merely a non-zero exit — the house rule from `test_check_prose_claims.py`.

### 2. It runs in the blocking gate, not as advice

**What was built.** `gate_bump_classification` is called from `main()` after the release-only block, in **both** ordinary and release mode. Failures land in the same `errors` list every other check uses, so they print under `RELEASE GATE: BLOCKED` and set exit code 1. CI's `Run release gate` step already treats a non-zero exit as a failed check (no `continue-on-error`).

**Test.** `case_live_tree_gate_stays_green` runs `python scripts/release_gate.py` with no arguments on this repository and requires `RELEASE GATE: PASS`. The refusal half is every control above: the shipped script exits 1.

### 3. Controls plant each refusable defect and run in CI

**What was built.**

- `scripts/test_bump_classification.py` — 16 behaviour controls + 3 CI-wiring controls (19 total).
- `.github/workflows/tests.yml`, release-gate job:
  - `Bump-classification suite` runs `python scripts/test_bump_classification.py` and requires its `^PASS:` line.
  - `Poison control - a card rename must be refused unless declared major` — plants a rename, requires minor REFUSED under G10 and major PASS.
  - `Poison control - a rename declared below major must be rejected`
  - `Poison control - a card admission declared patch must be rejected`
  - `Poison control - no surface change declaring minor or major must be rejected`
  - `Poison control - a release version delta that overstates the surface must be rejected`

**Tests that pin the wiring.** `case_ci_runs_the_bump_classification_suite`, `case_ci_carries_the_inversion_poison_control`, `case_ci_carries_case1_to_case4_poison_controls` read `tests.yml` and assert each step exists, runs the shipped gate, and greps the G10-specific message. Before this branch those cases failed (`no 'Bump-classification suite' step under the release-gate job`); after the workflow edit they pass.

The shell poison controls were executed locally against the shipped gate (same fixtures the YAML plants): case3 and case4 refused under G10 with single-reason output; the inversion control refused rename+minor under G10 and accepted rename+major.

### 4. A control proves the check stays silent on a correctly classified changeset

**What was built.** `case_positive_correct_classification_is_silent` — a scripts-only branch with a changeset declaring `patch`. Nothing under `skills/*/*/` moves, so patch is the ADR 0002 price for work that reaches no card. The gate must PASS.

Also positive: `case_positive_rename_major_passes`, `case_positive_add_minor_passes`, `case_case4_release_delta_matches_rename_is_silent` (major delta over a rename release), `case_empty_changeset_is_not_a_classification_fault`.

Observed: these PASS both before and after G10 — they are the half of the contract that must not become red.

### 5. Inversion pin: rename + `major` PASSES; the same rename + `minor` is REFUSED

**What was built.** `case_positive_rename_major_passes` and `case_case1_rename_declared_minor_is_refused` share one fixture recipe (`make_tree(..., branch_change="rename")`) and differ only in the declared level. CI carries the same pin in shell (`Poison control - a card rename must be refused unless declared major`), which requires both halves.

Observed before G10: rename + minor was **accepted** (`RELEASE GATE: PASS`) — the superseded rule's failure mode. After G10: rename + minor is **refused** under G10 naming the major price; rename + major still **passes**. A control that only tested the refusing direction would also pass under the superseded "require minor" rule; this pair is what distinguishes the two.

### 6. Classification is derived from ADR 0003 by reading the repository

**What was built.** `derive_bump_prices(root)` reads `root/docs/adr/0003-…` and `root/docs/adr/0002-…` on every classified run. There is no `RENAME_IS_MAJOR = "major"` constant. `BUMP_RANK` ranks words the ADRs supply; it does not supply the rules.

**Tests that pin it.**

- `case_ard_text_is_read_not_hardcoded` — plants an ADR 0003 rewritten so a rename prices as **patch**, then plants a rename declared `patch`. Under a hardcoded major rule this would be refused. Observed: **PASS**, because the checker followed the file on disk.
- `case_missing_ard_fails_closed_when_classification_needed` — deletes the ADRs from a fixture that needs classification (rename + major). Observed: `G10: cannot derive bump classification from the ADRs: …` — fail-closed, not a silent skip.

## Mutation campaign

The ticket does not name a `mutation_receipt.py` obligation. No mutation receipt was run. The controls above are the contract tests; each refusal assertion is external behaviour (exit code + printed `G10:` message), not an internal branch probe.

## Companion artifacts

- Issue: #289 (ticket text supplied in the worktree; no network read).
- ADRs cited and read at source in this worktree: `docs/adr/0002-a-release-is-a-delivery-event.md`, `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md`.
- Prior art named by the ticket: `scripts/check_prose_claims.py` and its controls in `scripts/test_check_prose_claims.py` (derive-from-disk, refuse-by-name, UNINTERPRETABLE / fail-closed shape).
- Changeset: `.changeset/g10-bump-classification-289.md` (empty — gate tooling only; no card or package behaviour change).
- This file: `.scratch/issue-289/pr-body.md`, committed on the branch before finish.

## Gate run before finish

| Command | Result |
|---|---|
| `python scripts/test_bump_classification.py` | PASS, 19 controls |
| `python scripts/test_release_gate.py` | PASS, 66 contract cases (unchanged; no existing test edited) |
| `python scripts/release_gate.py` | PASS at 3.0.1, including G10 |
| `python scripts/test_release_model_disclosure.py` | PASS |
| `python scripts/validate_scoreboard.py` | PASS |
| `python scripts/validate_card_files.py` | PASS (pre-existing allowlisted breaches unchanged) |
| `python scripts/validate_conformance.py --root .` | PASS, 60 cells |
| `python scripts/validate_skill_formats.py` | PASS |
| `python scripts/validate_path_residue.py` | PASS |

## Disposition

Every acceptance checkbox above is satisfied. The check is in the blocking gate, derives its prices from the ADRs on disk, pins the ADR 0003 inversion in both directions, and ships controls in CI that plant each refusable class.
