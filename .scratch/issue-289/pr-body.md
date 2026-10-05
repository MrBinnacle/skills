# #289 — G10: a changeset's declared bump type must match its diff

`release_gate.py` gains **G10**. It reads the declared-surface prices from ADR 0003 and ADR 0002 on disk — never from a constant in the gate — and refuses a changeset whose `major` / `minor` / `patch` line disagrees with what its diff does under `skills/*/*/`. A wrong bump spends the wrong version number permanently (ADR 0002), so the check blocks rather than reports.

## Files on this branch (the whole diff vs `origin/main`)

- `.changeset/g10-bump-classification-289.md` — empty changeset describing the gate change; no card and no package behaviour changes, so the release is not bumped by it.
- `.github/workflows/tests.yml` — the `release-gate` job (`Release gate (fit to release)`) gains a `Bump-classification suite` step and seven G10 poison controls that re-run the **shipped** gate against planted trees.
- `scripts/release_gate.py` — G10: classification derived from the ADRs on disk; cases 1–3 judge only branch-added changesets; case 4 prices the version delta against the changesets the release consumes; `GitUnavailableError` is caught and refused in G10's own words.
- `scripts/test_bump_classification.py` — 30 controls covering the four cases, the ADR 0003 inversion, B2(a–c), B3, ADR-text-not-hardcoded, missing-ADR fail-closed, empty-changeset silence, live-tree green, G10 git-absent, and static pins on the CI wiring.

## What the check does

Classification is read from the ADRs on every run:

- ADR 0003 decision sentence: renaming a card is a **major** change; admitting or retiring one remains a **minor** change.
- ADR 0002: corrections within a card are a **patch**; the card set is outside the declared surface.

Cases, each a listed failure:

1. A branch-added changeset whose diff renames a card directory under `skills/*/*/` and declares anything less than the rename price (major).
2. A branch-added changeset whose diff adds or removes a directory under `skills/*/*/` and declares the patch price.
3. A branch-added changeset whose diff touches no file under `skills/*/*/` and declares minor or major.
4. (`--release` only) A version delta that disagrees with the bump the changesets this release **consumed** declare — read at the merge-base, because `changeset version` deletes those files at HEAD.

A rename and an addition in one changeset resolve to major: the higher classification governs. Classification is skipped only when the tree publishes no card, when no branch-added changeset declares a bump, or when the git diff cannot be established. When classification is needed and an ADR cannot be read, the run fails closed. When git itself cannot run, G10 refuses under G10 in its own words rather than dying with a traceback.

## Acceptance criteria

### Case 1 — rename declared below major is refused

**Satisfied by** G10 in `scripts/release_gate.py` (`gate_bump_classification` / `required_price_for_diff` / the rename branch of the case-1 error).
**Pinned by** `case_case1_rename_declared_patch_is_refused` and `case_case1_rename_declared_minor_is_refused` in `scripts/test_bump_classification.py`; CI poison control `Poison control - a rename declared below major must be rejected`.
**Observed** Before G10 existed the gate was green on a rename declared `patch` (#286's incident). On this branch the planted rename+patch fixture exits non-zero, names `G10:`, and the refusal names `rename` and `major`. The inversion half — rename+major — must PASS; both directions are pinned.

### Case 2 — admission or retirement declared patch is refused

**Satisfied by** G10's admit/retire branch, priced from ADR 0003 (`Admitting or retiring one remains a minor change`).
**Pinned by** `case_case2_add_declared_patch_is_refused` and `case_case2_remove_declared_patch_is_refused`; CI poison control `Poison control - a card admission declared patch must be rejected`; positive control `case_positive_add_minor_passes`.
**Observed** The planted add-card/patch fixture is refused under G10 naming `add` and `minor`. The correctly declared minor admission PASSES — the check is not refusing everything.

### Case 3 — no surface change declared minor or major is refused

**Satisfied by** G10's case-3 branch when `diff["touched"]` is false.
**Pinned by** `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused`; CI poison control `Poison control - no surface change declaring minor or major must be rejected`; positive control `case_positive_correct_classification_is_silent`.
**Observed** A scripts-only change declared patch PASSES. The same shape declared minor or major is refused, naming `skills/*/*/`. A directory under a bucket that carries no `SKILL.md` is not a card and does not justify minor.

### Case 4 — release version delta vs the consumed plan (built)

**Satisfied by** G10's release-mode branch: `_consumed_declared_bumps` reads the changesets the release consumed at the merge-base; `_refuse_delta_mismatch` compares the SemVer field that moved against the highest bump that plan declares.
**Pinned by** `case_case4_consumed_major_with_major_delta_passes`, `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_no_consumed_plan_with_delta_is_refused`; `case_b3_v300_shaped_release_passes`, `case_b3_v300_shaped_release_minor_delta_refused`; CI poison controls `Poison control - a release version delta that disagrees with the consumed plan` and `Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused`.
**Observed** A v3.0.0-shaped tree (consumed major + patches, delta 2.0.0 → 3.0.0) run with `--release` PASSES. The same tree with a minor bump (2.0.0 → 2.1.0) is REFUSED under G10, naming both versions and `major`. A delta with no consumed plan behind it is also refused. This is built, not sketched: the controls plant the tree and run the shipped gate.

### Blocking gate, not advice

**Satisfied by** G10 listed in the gate's own check roster; every refusal is a listed `FAIL` under `RELEASE GATE: BLOCKED`.
**Pinned by** every `expect_g10_refusal` / `expect_g10_refusal` path in `scripts/test_bump_classification.py` requiring non-zero exit **and** the `G10:` token **and** the specific fault — a non-zero exit alone is not enough.

### Controls that plant each refusable defect and run in CI

**Satisfied by** eight new steps under the `release-gate` job in `.github/workflows/tests.yml`: the `Bump-classification suite` step plus seven poison controls. All eight were executed locally against the shipped gate at this head; all passed.

| # | Step | What it plants |
|---|------|----------------|
| 1 | Bump-classification suite | Runs `scripts/test_bump_classification.py`; requires its `PASS:` line |
| 2 | Poison control — a card rename must be refused unless declared major | Inversion: rename+minor REFUSED, rename+major PASSES |
| 3 | Poison control — a rename declared below major must be rejected | Case 1: rename+patch REFUSED, single-reason |
| 4 | Poison control — a card admission declared patch must be rejected | Case 2: add-card+patch REFUSED, single-reason |
| 5 | Poison control — no surface change declaring minor or major must be rejected | Case 3: scripts-only+minor REFUSED, single-reason |
| 6 | Poison control — a release version delta that disagrees with the consumed plan | Case 4: major plan + minor delta REFUSED; major plan + major delta PASSES |
| 7 | Poison control — a push to main must not re-judge main's pending changesets | B2(a) push-to-main after minor admission PASSES; B2(b) next scripts-only PR PASSES; B2(c) #316 major replay PASSES |
| 8 | Poison control — a v3.0.0-shaped release must pass and a minor delta must be refused | B3: v3.0.0-shaped release PASSES; same plan with minor delta REFUSED |

Local run of the whole `release-gate` job at this head: **16/16 steps PASS** (8 pre-existing poison controls from main + the 8 new steps above).

### Control proves the check stays silent on a correctly classified changeset

**Satisfied by** `case_positive_correct_classification_is_silent` (scripts-only + patch → PASS), `case_positive_rename_major_passes` (rename + major → PASS), `case_positive_add_minor_passes` (admission + minor → PASS), `case_empty_changeset_is_not_a_classification_fault`, `case_live_tree_gate_stays_green`, and the positive halves of the inversion, case-4 and B3 CI controls. The gate is not merely refusing everything.

### Inversion pin — rename+major PASSES, rename+minor REFUSED

**Satisfied by** ADR 0003's decision sentence, read from disk.
**Pinned by** `case_positive_rename_major_passes` (passes) and `case_case1_rename_declared_minor_is_refused` (refused); CI step `Poison control - a card rename must be refused unless declared major`, which runs **both** halves against the shipped gate.
**Observed** Before ADR 0003 the superseded rule required `minor` for a rename; a control that only tested the refusing direction would have passed under that rule too. Both directions are now pinned. A static control additionally requires that half two of the CI step recreates `.changeset/` before writing the major changeset — the F1 defect that killed this step in CI.

### Classification derived from ADR 0003 by reading the repository

**Satisfied by** `derive_bump_prices` in `scripts/release_gate.py`, which parses the decision sentences from `docs/adr/0003-…` and `docs/adr/0002-…` on every run. The only constant in the checker is `BUMP_RANK`, which ranks the words the ADRs supply; the rule "rename → major" is never written into the script.
**Pinned by** `case_ard_text_is_read_not_hardcoded` (an ADR rewritten so rename prices as patch accepts rename+patch) and `case_missing_ard_fails_closed_when_classification_needed` (missing ADR → fail closed under G10 naming ADR).

### B1 — merge of `origin/main`; G10 catches `GitUnavailableError`

**Satisfied by** merge commit `1c6ec99` (main at `fd168ba`, which carries #347: `_is_git_work_tree` / `_git_ok` raise `GitUnavailableError` when git is absent) plus G10's `except GitUnavailableError` handler, which refuses under G10 in its own words when a declared bump is pending on disk, with no traceback.
**Pinned by** `scripts/test_release_gate.py` — all 69 contract cases pass on the merge result, including the #342 git-absent cases (`case_missing_git_refuses_in_its_own_words`, `case_missing_git_also_refuses_the_mode_detection_path`, `case_missing_git_refuses_spec_conformance_in_its_own_words`); and by two new controls in `scripts/test_bump_classification.py`: `case_g10_refuses_in_its_own_words_when_git_is_absent` (pending declared bump → G10 names git and the changeset, no traceback) and `case_g10_is_silent_when_git_absent_and_no_declared_bump` (no pending bump → G10 silent, other checks still refuse).
**Observed** At `53a5b3a` merged with main, the #342 cases failed because git-absent runs died with a traceback instead of a named refusal. After the merge they pass. The G10-specific git-absent controls were added this run; they pin the handler that #347's `GitUnavailableError` made necessary.

### B2 — cases 1–3 judge only branch-added changesets

**Satisfied by** `_branch_added_changeset_names`: new `.changeset/*.md` present at HEAD and absent at the merge-base. Pending files main already holds are not re-judged.
**Pinned by** `case_b2a_push_to_main_after_admission_passes`, `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes`; CI poison control `Poison control - a push to main must not re-judge main's pending changesets`, which now runs all three halves.
**Observed** Before this rework G10 judged every pending file on disk, so a push to main after a correctly declared minor admission would have been refused as case 3. All three B2 controls now PASS.

### B3 — case 4 prices the consumed plan, not the card diff

**Satisfied by** `_consumed_changeset_names` + `_consumed_declared_bumps` reading the plan at the merge-base; the release PR's card diff is irrelevant to case 4 because this repository releases through a separate PR that runs `npm run version` and touches no card.
**Pinned by** the B3 suite cases and CI control listed under case 4 above.
**Observed** A tree shaped like the real v3.0.0 release (4c00b0e): consumed major + patches at the base, files deleted at HEAD, version 2.0.0 → 3.0.0, run with `--release` PASSES. The same tree with 2.0.0 → 2.1.0 is REFUSED.

### Higher classification governs a changeset that contains both

**Satisfied by** `required_price_for_diff`, which takes the higher of the ADR prices the diff reaches.
**Pinned by** `case_higher_classification_governs_rename_plus_add`: a fixture that renames a card and adds another in one changeset, with the changeset declaring **minor** (the price an addition alone would cost), is REFUSED because the rename prices major. Declaring minor is what kills a mutant that took the lower price.

## Local verification at this head

| Command | Result |
|---------|--------|
| `python scripts/test_bump_classification.py` | PASS: 30 controls |
| `python scripts/test_release_gate.py` | PASS: 69 contract cases |
| `python scripts/release_gate.py --root .` | RELEASE GATE: PASS (live tree, version 3.0.1) |
| `release-gate` job steps, extracted and run locally with `bash -e -o pipefail` and `RUNNER_TEMP` set | 16/16 PASS |

The required check `Release gate (fit to release)` is the `release-gate` job; every step of that job was executed locally against this head.

## Revisit if

ADR 0003 is amended or superseded. The check reads classification from the ADR text on disk, so a rewrite of the decision sentences changes what the gate asserts without editing the checker. ADR 0003's own Decision marks the rename-is-major call revisable with new evidence; that evidence would land in the ADR, not in `release_gate.py`.

The changesets tool's own classification behaviour changes such that the declared type is no longer carried straight through to the version computation, which would move where this check belongs.
