# #289 — G10: a changeset's declared bump must agree with its diff

## What this branch ships

`scripts/release_gate.py` gains **G10**, a blocking check that refuses a release (and an ordinary PR) whose changeset declares a `major` / `minor` / `patch` line that contradicts what the branch actually changed. Prices come from the ADRs on disk — `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` for rename = major and admit/retire = minor, `docs/adr/0002-a-release-is-a-delivery-event.md` for corrections within a card = patch. The checker never hardcodes a bump word; a constant would go stale the same way the `README.md:66` citation did.

Files on this branch (the whole diff vs `origin/main`):

- `.changeset/g10-bump-classification-289.md` — empty changeset (gate tooling only; no card or package behaviour change)
- `.github/workflows/tests.yml` — CI: the bump-classification suite step plus five poison controls under the release-gate job
- `scripts/release_gate.py` — G10 implementation
- `scripts/test_bump_classification.py` — 28 controls that plant each refusable class and pin the passing halves
- `.scratch/issue-289/pr-body.md` — this evidence body (committed on the branch; the runner publishes it as the PR body)

This is a rework of PR #348 after a FAIL verdict at `53a5b3a`. What that build already had and this branch keeps: the G10 skeleton, prices derived from the ADR text, cases 1 and 2, and the ADR 0003 inversion control (rename + `major` passes; the same rename + `minor` is refused).

## Acceptance criteria, and what pins each

### 1. A check refuses a changeset whose declared bump contradicts its own diff, for each of the four cases

**Satisfied by** G10 in `scripts/release_gate.py`, cases 1–4 as amended 2026-09-13.

| Case | Rule | Control |
|---|---|---|
| 1. Rename under `skills/*/*/`, declared less than `major` | ADR 0003 line 19 | `case_case1_rename_declared_patch_is_refused`, `case_case1_rename_declared_minor_is_refused` |
| 2. Add/remove a card directory, declared `patch` | ADR 0003 line 19 | `case_case2_add_declared_patch_is_refused`, `case_case2_remove_declared_patch_is_refused` |
| 3. No file under `skills/*/*/`, declared `minor` or `major` | ADR 0002 | `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused` |
| 4. Release version delta disagrees with the changesets the release **consumes** | Ticket + B3 | `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_no_consumed_plan_with_delta_is_refused`; positive half `case_case4_consumed_major_with_major_delta_passes` |

**Observed before this rework:** the FAIL verdict at `53a5b3a` recorded cases 1–3 as already working; case 4 was built against the card diff, not the consumed plan. A v3.0.0-shaped release (consumed plan prices major, version 2.0.0 → 3.0.0) was **refused** under the old rule, because the release PR touches no card directory and the old code priced the surface diff instead of the plan. **After:** that tree passes; the same tree with a minor bump is refused naming `2.0.0`, `2.1.0`, and `major`.

### 2. It runs in the blocking gate, not as advice

**Satisfied by** `gate_bump_classification(...)` called from `main()` in `scripts/release_gate.py` on every run (ordinary and release mode). A G10 finding lands in `errors` and the gate prints `RELEASE GATE: BLOCKED` with exit 1. The CI job `Release gate (fit to release)` carries no `continue-on-error`.

**Pinned by** every refusal control in `scripts/test_bump_classification.py` (non-zero exit + `G10:` in the output) and by the five CI poison controls in `.github/workflows/tests.yml`, which re-run the shipped gate against planted trees.

### 3. Controls that plant each refusable defect and prove the check goes red, running in CI

**Satisfied by** `scripts/test_bump_classification.py` (28 controls, all green) and the CI wiring under the release-gate job in `.github/workflows/tests.yml`:

- Step `Bump-classification suite` runs this file and requires its `PASS:` line.
- Poison controls (shell, against the shipped gate): rename declared below major; card admission declared patch; no-surface change declaring minor/major; release delta disagreeing with the consumed plan; push-to-main must not re-judge main's pending changesets; v3.0.0-shaped release must pass and a minor delta must be refused.

**Observed before:** at `53a5b3a` the suite ran and CI carried an earlier set of controls; after the merge with `origin/main` (`#347`), `python scripts/test_release_gate.py` failed 8 cases — G10 died with a `GitUnavailableError` traceback where the #342 cases expected a refusal naming git. **After B1:** all 69 release-gate cases pass, including the eight git-absent cases.

### 4. A control proves the check stays silent on a correctly classified changeset

**Satisfied by** `case_positive_correct_classification_is_silent` (scripts-only change declared `patch`), `case_positive_rename_major_passes`, `case_positive_add_minor_passes`, `case_case4_consumed_major_with_major_delta_passes`, `case_b2a_push_to_main_after_admission_passes`, `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes`, `case_b3_v300_shaped_release_passes`, `case_empty_changeset_is_not_a_classification_fault`, and `case_live_tree_gate_stays_green` (this repository as a maintainer runs it).

### 5. Inversion pin: rename + `major` PASSES; the same rename + `minor` is REFUSED

**Satisfied by** `case_positive_rename_major_passes` and `case_case1_rename_declared_minor_is_refused`, plus CI control `Poison control - a card rename must be refused unless declared major`, which runs both halves in shell.

**Observed before:** this control existed at `53a5b3a` and is kept. A control that only tested the refusing direction would also pass under the superseded rule that required `minor`.

### 6. Classification is read from ADR 0003 by reading the repository, not from a hardcoded bump word

**Satisfied by** `derive_bump_prices()` in `scripts/release_gate.py`, which parses the decision sentences from `docs/adr/0003-...md` and `docs/adr/0002-...md` on every run and fails closed when a sentence is missing or unparseable.

**Pinned by** `case_ard_text_is_read_not_hardcoded` (rewrites ADR 0003 so a rename prices as `patch`, then plants rename + `patch`; the gate stays silent) and `case_missing_ard_fails_closed_when_classification_needed` (no ADR text → G10 refuses when classification is needed).

### B1 — merge `origin/main`; G10 catches `GitUnavailableError` and refuses in its own words

**Satisfied by** the merge commit already on this branch (`1c6ec99`, merging `fd168ba` = `#347`) plus the G10 handler: `gate_bump_classification` wraps its git work and, when git cannot run, appends `G10: git could not be run - ...` only if the tree still carries a pending changeset that declares a bump. A tree with nothing to classify stays silent so G6/G9 report the missing dependency on their own checks.

**Pinned by** `scripts/test_release_gate.py` cases `case_missing_git_refuses_in_its_own_words`, `case_missing_git_also_refuses_the_mode_detection_path`, and `case_missing_git_refuses_spec_conformance_in_its_own_words` — the eight git-absent checks among them.

**Observed before:** at the merge of `#347` into this branch, `python scripts/test_release_gate.py` failed 8 cases; the refusal text never reached the reader because G10 raised `GitUnavailableError` out of `main()`. **After:** `PASS: release gate verified across 69 contract case(s)`.

### B2 — cases 1–3 judge only the changesets this branch adds

**Satisfied by** `_branch_added_changeset_names()` in `scripts/release_gate.py`: new `.changeset/*.md` in `merge-base..HEAD`, read with `git ls-tree` at both revisions. Pending files that `main` already holds are never judged again.

**Pinned by** three suite controls and one CI control:

| Control | Shape | Result |
|---|---|---|
| `case_b2a_push_to_main_after_admission_passes` | Admission merged to main with a correct `minor` changeset; `origin/main == HEAD`; branch diff empty | PASS |
| `case_b2b_next_scripts_only_pr_passes` | Next scripts-only PR on top of that main; main still holds the pending `minor` | PASS |
| `case_b2c_replay_push_to_main_at_316_passes` | Replay of the push to main at `3f2aeae` (#316, correct `major`) | PASS |
| CI `Poison control - a push to main must not re-judge main's pending changesets` | Both halves of (a) and (b) in shell | PASS |

**Observed before:** under the pre-rework rule, every pending file on disk was judged against the branch diff. After an admission with a correct `minor` merged to main, the next run saw an empty diff and refused that `minor` as case 3. The same defect refused the #316 replay (`major` on an empty post-push diff). **After:** all three controls pass.

### B3 — case 4 compares the version bump with the changesets the release consumes

**Satisfied by** `_consumed_changeset_names()` / `_consumed_declared_bumps()` in `scripts/release_gate.py`: files present at `merge-base` and gone at HEAD are the plan `changeset version` consumed; their declared bumps are read with `git show merge-base:.changeset/<name>` and priced under the same ADR rules. The version delta must equal the highest consumed bump. A delta with no consumed plan behind it is also refused. This is what a real release PR looks like (`4c00b0e` touched only `.changeset` deletions, `package.json`, `CHANGELOG.md`, and plugin versions — no card directory moved).

**Pinned by** `case_b3_v300_shaped_release_passes` (consumed `major` + patches, version 2.0.0 → 3.0.0, PASS) and `case_b3_v300_shaped_release_minor_delta_refused` (same plan, version 2.1.0, REFUSED naming `major`), plus CI control `Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused`.

**Observed before:** the old case 4 priced the card surface diff. A correct v3.0.0-shaped release was refused because the release PR moves no card directory. **After:** that tree passes; a minor mis-bump over the same major plan is refused for the right reason.

### B4 — the rename + add control declares `minor`

**Satisfied by** `case_higher_classification_governs_rename_plus_add`, which plants a rename and an addition on one branch with a changeset declaring `minor` (the price an addition alone would cost) and requires G10 to refuse it, because the higher class (`major`, from the rename) governs. A mutant that took the lower price, or that priced only the addition, would accept this fixture.

**Observed before:** the control declared `patch`. Under a "lower price wins" or "admit only" mutant, `patch` would still be refused, so the mutant survived. **After:** declaring `minor` kills both mutants.

### B5 — PR body states only what is true at the pushed head

This file is the evidence body. At the head that carries it:

- Control count: **28** in `scripts/test_bump_classification.py`, all green; **69** contract cases in `scripts/test_release_gate.py`, all green.
- `.scratch/issue-289/pr-body.md` is committed on this branch (it is part of the diff named above). Nothing else under `.scratch/` is claimed.
- Case 4 is described as **built** — implemented in `scripts/release_gate.py` and pinned by the controls named above.
- No claim that "every acceptance checkbox is satisfied" beyond the criteria listed here, each with its pinning test.

### B6 — required checks green

Locally, with `PYTHONUTF8=1`:

- `python scripts/release_gate.py` → `RELEASE GATE: PASS` (ordinary mode; the branch's own changeset is empty and declares no bump).
- `python scripts/release_gate.py --release` → `BLOCKED` on G3 (7 unconsumed changesets — expected on a non-release PR) and G9 (this working tree is dirty until the rework commits land). G10 does not fire spuriously on this branch.
- `python scripts/test_release_gate.py` → PASS, 69 cases.
- `python scripts/test_bump_classification.py` → PASS, 28 controls.
- The five CI poison controls under the release-gate job were executed locally against the shipped gate and all passed.

GitHub-side checks (`Release gate (fit to release)` and the rest of the workflows) are expected to run on the pushed head; this container holds no GitHub token, so they are not reported as observed here.

## Control-to-criterion map

| Criterion | Pinning test(s) |
|---|---|
| Case 1 refuse | `case_case1_rename_declared_patch_is_refused`, `case_case1_rename_declared_minor_is_refused`; CI `Poison control - a rename declared below major must be rejected` |
| Case 2 refuse | `case_case2_add_declared_patch_is_refused`, `case_case2_remove_declared_patch_is_refused`; CI admission control |
| Case 3 refuse | `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused`; CI no-surface control |
| Case 4 built (consumed plan) | `case_case4_consumed_major_with_major_delta_passes`, `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_no_consumed_plan_with_delta_is_refused`, `case_b3_v300_shaped_release_passes`, `case_b3_v300_shaped_release_minor_delta_refused`; CI consumed-plan control; CI v3.0.0 control |
| Blocking gate | every refusal control asserts non-zero exit + `G10:`; CI job has no `continue-on-error` |
| Silent when correct | positive controls listed in criterion 4 |
| Inversion pin | `case_positive_rename_major_passes`, `case_case1_rename_declared_minor_is_refused`; CI rename/inversion control |
| ADR text on disk | `case_ard_text_is_read_not_hardcoded`, `case_missing_ard_fails_closed_when_classification_needed` |
| B1 git-absent | `scripts/test_release_gate.py` #342 cases (8), all green after the merge + G10 handler |
| B2 branch-added only | `case_b2a_*`, `case_b2b_*`, `case_b2c_*`; CI push-to-main control |
| B3 consumed plan | B3 cases above; CI v3.0.0 control |
| B4 higher governs | `case_higher_classification_governs_rename_plus_add` (declares `minor`) |
| CI wiring | `case_ci_runs_the_bump_classification_suite`, `case_ci_carries_the_inversion_poison_control`, `case_ci_carries_case1_to_case4_poison_controls`, `case_ci_carries_b2_and_b3_controls` |

## How it was found (historical, one claim superseded)

The changeset for #286 declared `patch` for a change that renamed eleven published cards' directories. Under ADR 0002 as it then stood that was a `minor` change; under ADR 0003 it is `major`. All six unconsumed changesets declared `patch`, so the next `changeset version` would have cut a patch release that moves eleven install paths. Every gate was green. The same changeset was classified wrongly twice by two careful human readings of the governing document — that is the argument for a check, not against one. This body's historical classification of that rename as `minor` is superseded; do not build from it.

## Revisit if

ADR 0003 is amended or superseded, which changes what the check is allowed to assert. Classification is read from the repository, so a price change in the ADR text moves the check with it; a hardcoded bump word would not.

The changesets tool's own classification behaviour changes such that the declared type is no longer carried straight through to the version computation, which would move where this check belongs.
