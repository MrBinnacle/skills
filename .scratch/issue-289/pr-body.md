# #289 — G10: a changeset's declared bump must match what its diff changed

`release_gate.py` gains check **G10**. A changeset declares its own `major` / `minor` / `patch` line; nothing used to check that declaration against the files the changeset's diff actually touched. A wrong bump spends the wrong version number permanently (ADR 0002), so the check blocks in the release gate rather than advising.

Classification is **read from the repository on every run**, not hardcoded. `derive_bump_prices()` parses ADR 0003 (`docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md`) and ADR 0002 (`docs/adr/0002-a-release-is-a-delivery-event.md`) for the decision sentences. A missing ADR fails closed when classification is needed. A constant in the script would go stale the same way a line-number citation of `README.md:66` did.

## Files on this branch (the whole diff vs `origin/main`)

| File | Role |
|---|---|
| `.changeset/g10-bump-classification-289.md` | Empty changeset (scripts-only; no card, no package bump) |
| `.github/workflows/tests.yml` | Seven G10 poison controls under the blocking `Release gate (fit to release)` job, plus the bump-classification suite step |
| `scripts/release_gate.py` | G10 implementation |
| `scripts/test_bump_classification.py` | 34 controls that plant each refusable shape and drive the shipped gate as a subprocess |

## What G10 checks

**Cases 1–3** judge only the changesets **this branch adds** (new `.changeset/*.md` in `merge-base..HEAD`), never every pending file on disk. After an admission with a correct minor changeset merges to main, that file sits on main; a later scripts-only PR must not be refused for it.

**Case 4** (`--release`) compares the release's version bump with the changesets **the release consumes** — read at the merge-base, because `changeset version` deletes those files at HEAD. A release PR that runs `npm run version` touches no card; the plan is the consumed changesets, not the card diff.

| Case | Diff shape | Declared | Verdict | ADR price |
|---|---|---|---|---|
| 1 | Renames a `skills/*/*/` card directory | anything below `major` | REFUSED | ADR 0003: rename is major |
| 2 | Adds or removes a `skills/*/*/` card directory | `patch` | REFUSED | ADR 0003: admit/retire remains minor |
| 3 | Touches no file under `skills/*/*/` | `minor` or `major` | REFUSED | Nothing outside cards changes the declared surface |
| 4 | Release version delta | disagrees with the consumed plan's price | REFUSED | Exact SemVer result `changeset version` would write |

A rename and an addition in one changeset resolve to `major` (higher classification governs). The control for that mutant declares `minor`.

When git is absent from PATH, G10 catches `GitUnavailableError` and refuses in its own words when a declared bump is pending — no traceback. Without a pending bump G10 is silent; other git-dependent checks still refuse.

An explicit `--release` run on a released, clean main (origin/main == HEAD, no plan consumed, version unchanged) is **silent**: there is no delta to price. Refusing that tree was the round-3 regression N1.

## Acceptance criteria

### 1. A check refuses a changeset whose declared bump contradicts its own diff, for each of the four cases

**Satisfied by** G10 in `scripts/release_gate.py` (`gate_bump_classification` / `_gate_bump_classification_inner` / `_refuse_delta_mismatch`).

**Pinned by** `scripts/test_bump_classification.py`:
- Case 1: `case_case1_rename_declared_patch_is_refused`, `case_case1_rename_declared_minor_is_refused`
- Case 2: `case_case2_add_declared_patch_is_refused`, `case_case2_add_declared_quoted_patch_is_refused`, `case_case2_remove_declared_patch_is_refused`
- Case 3: `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused`
- Case 4 refuse half: `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_no_delta_is_refused`, `case_case4_requires_the_exact_changesets_version`, `case_case4_no_consumed_plan_with_delta_is_refused`
- Case 4 pass half (built, not advice): `case_case4_consumed_major_with_major_delta_passes`, `case_b3_v300_shaped_release_passes`

**Observed:** at this head every case above prints `ok` under `python scripts/test_bump_classification.py`. The case-4 refuse controls were built in rework round 1/2 (commit `06fa0b3`, `dfd1e45`); before that build the gate had no bump-classification logic at all (`grep -n "major\|minor\|patch" scripts/release_gate.py` on origin/main returned no classification). The pass half was added when case 4 was re-priced from the consumed plan rather than the card diff.

### 2. It runs in the blocking gate, not as advice

**Satisfied by** `main()` in `scripts/release_gate.py` calling `gate_bump_classification(...)` on every run (ordinary and `--release`). The workflow job `Release gate (fit to release)` is blocking (`continue-on-error` absent) and publishes that status context.

**Pinned by** the release-gate suite that runs from `origin/main` (not changed by this branch): `case_ci_job_is_blocking_and_on_every_pull_request` asserts no `continue-on-error`, the exact `name: Release gate (fit to release)` context, and both `pull_request` and `push` triggers. The G10 call itself is pinned by the bump-classification suite and by the live `RELEASE GATE: PASS` line that names bump types.

**Observed:** `python scripts/release_gate.py` on the live tree prints `RELEASE GATE: PASS ... changeset bump types match the declared surface.` A planted G10 defect exits non-zero with `RELEASE GATE: BLOCKED` and a `G10:` line.

### 3. Controls plant each refusable defect and prove the check goes red; they run in CI

**Satisfied by** seven poison-control `run:` blocks under `Release gate (fit to release)` in `.github/workflows/tests.yml`, plus the `Bump-classification suite` step that runs `scripts/test_bump_classification.py` and requires its `^PASS:` line.

**Pinned by** the seven controls themselves (each runs the **shipped** gate against a planted tree, greps for `G10:` and the specific reason, and where relevant asserts a single-reason refusal):

1. `Poison control - a card rename must be refused unless declared major` (inversion)
2. `Poison control - a rename declared below major must be rejected` (case 1)
3. `Poison control - a card admission declared patch must be rejected` (case 2)
4. `Poison control - no surface change declaring minor or major must be rejected` (case 3)
5. `Poison control - a release version delta that disagrees with the consumed plan` (case 4)
6. `Poison control - a push to main must not re-judge main's pending changesets` (B2 a–c)
7. `Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused` (B3)

**Observed:** all seven extracted `run:` blocks executed locally against the shipped gate at this head: **7/7 PASS**. Control 1 previously failed in CI at `53a5b3a` because half two wrote `$tree/.changeset/zzz-rename.md` without recreating the directory after `git checkout main` removed it; `9de6c07` added `mkdir -p "$tree/.changeset"` and the step now runs to its `echo` line. The static control `case_ci_carries_the_inversion_poison_control` passes whether or not the shell step runs; the live CI run is what proves the step.

### 4. A control proves the check stays silent on a correctly classified changeset

**Satisfied by** positive halves in the suite and in CI:
- `case_positive_correct_classification_is_silent` (scripts-only change declared `patch`)
- `case_positive_rename_major_passes`
- `case_positive_add_minor_passes`
- CI control 1 half two (rename + `major` must print `RELEASE GATE: PASS`)
- CI control 5 positive half (v3.0.0-shaped release with major delta must pass)
- CI control 6 (push to main after minor admission, next scripts-only PR, #316 major replay)

**Observed:** all of the above print `ok` / `RELEASE GATE: PASS` at this head.

### 5. The inversion is pinned: rename + major PASSES; the same rename + minor is REFUSED

**Satisfied by** ADR 0003's decision (rename is major) and the two directions in both the suite and CI control 1.

**Pinned by** `case_positive_rename_major_passes` and `case_case1_rename_declared_minor_is_refused`; CI control 1 asserts both halves in one `run:` block.

**Observed:** at this head both directions hold. A control that only tested the refusing direction would also pass under the superseded rule that required `minor`; the passing half is what kills that mutant. The rename+add mutant control (`case_higher_classification_governs_rename_plus_add`) declares **`minor`**, so a gate that priced only the addition would accept it.

### 6. Classification is derived from ADR 0003 by reading the repository, not a hardcoded bump word

**Satisfied by** `derive_bump_prices()` in `scripts/release_gate.py`, which regex-reads the decision sentences from the ADR files on disk every run.

**Pinned by** `case_ard_text_is_read_not_hardcoded` (plants an ADR that prices rename as `patch`; the gate follows the ADR) and `case_missing_ard_fails_closed_when_classification_needed`.

**Observed:** both print `ok` at this head. A hardcoded `rename → major` constant would fail the first control.

## Rework requirements

### B1 — merge `origin/main`; G10 catches `GitUnavailableError`

**Satisfied by** the merge at `e9e1eb6` and `gate_bump_classification`'s `except GitUnavailableError` clause (refuses under G10 in its own words when a declared bump is pending on disk).

**Pinned by** `case_g10_refuses_in_its_own_words_when_git_is_absent` and `case_g10_is_silent_when_git_absent_and_no_declared_bump` in `scripts/test_bump_classification.py`, plus the eight git-absent cases in the release-gate suite on `origin/main` (#342).

**Observed:** at this head both bump-classification git-absent cases and all 69 release-gate cases print `ok`. Before the merge, G10 could raise out of `_is_git_work_tree` / `_git_ok` when git was missing; after `#347` those helpers raise `GitUnavailableError` and G10 must catch it — which it does.

### B2 — cases 1–3 judge only branch-added changesets

**Satisfied by** `_branch_declared_bumps()` reading only names present at HEAD and absent at merge-base.

**Pinned by** `case_b2a_push_to_main_after_admission_passes`, `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes`, and CI control 6.

**Observed:** all three unit cases and the CI control print PASS / `ok` at this head. Before `06fa0b3` the gate classified every pending changeset on disk, so a push to main after a correct minor admission was refused as case 3.

### B3 — case 4 compares the release version bump with the consumed changesets

**Satisfied by** `_consumed_declared_bumps()` (files present at merge-base, gone at HEAD) and `_refuse_delta_mismatch()` computing `next_version_for_bump(base, required)`.

**Pinned by** `case_b3_v300_shaped_release_passes`, `case_b3_v300_shaped_release_minor_delta_refused`, `case_case4_consumed_major_with_major_delta_passes`, and CI controls 5 and 7.

**Observed:** the v3.0.0-shaped tree (consumed major + patches, delta major) prints `RELEASE GATE: PASS` with `--release`; the same tree with a minor bump is refused naming `G10:`, `2.0.0`, `2.1.0`, and `major`. Before this rework case 4 did not exist as a consumed-plan comparison.

### N1 (round 3) — `--release` on an unchanged version must pass

**Satisfied by** the `required_bump is None` branch of `_refuse_delta_mismatch` returning when `current_version == base_version`.

**Pinned by** `case_case4_unchanged_version_with_no_consumed_plan_passes` in `scripts/test_bump_classification.py` (committed in `1a60ef2`).

**Observed fail-before:** with the pre-fix gate, a tree shaped like released main (origin/main == HEAD, version unchanged, nothing consumed) was refused:

```
RELEASE GATE: BLOCKED - 1 stale surface(s) at version 3.0.1:
  FAIL  G10: release version changed from 3.0.1 to 3.0.1, but no changeset consumed by this release declares a bump...
```

Reproduced at commit `3dca050` plus the head gate with `origin/main` set to HEAD, and in a fixture with version `1.2.0`. The new control failed with that message before the fix.

**Observed pass-after:** the same `3dca050` tree now prints `RELEASE GATE: PASS - releasable at version 3.0.1`. The new control prints `ok`. A consumed plan that leaves the version unchanged is still refused (`case_case4_consumed_patch_with_no_delta_is_refused` prints `ok`), so the fix does not open that hole.

## What runs green at this head

Counts and commands were run at the head that carries this body's code (`1a60ef2` and the four-file branch diff against `origin/main`).

| Command | Result |
|---|---|
| `python scripts/release_gate.py` | `RELEASE GATE: PASS` (live tree) |
| `python scripts/release_gate.py --release` on `3dca050` + head gate, `origin/main` = HEAD | `RELEASE GATE: PASS - releasable at version 3.0.1` |
| `python scripts/test_bump_classification.py` | **PASS: 34 controls** |
| release-gate suite on `origin/main` (`python scripts/test_release_gate.py`) | **PASS: 69 contract case(s)** |
| `python scripts/test_release_model_disclosure.py` | **PASS** |
| Seven G10 poison-control `run:` blocks, `bash -e -o pipefail`, `RUNNER_TEMP` set | **7/7 PASS** |
| bump-classification suite and release-gate suite on a CRLF checkout of HEAD | **PASS** (33 controls, 69 cases) |

The bump-classification suite's 34 controls include the seven static CI-wiring assertions; the shell poison controls are executed separately as above. Both are required: the static assertions say the workflow still names the steps; the live runs say those steps still fire against the shipped gate.

## Revisit if

ADR 0003 is amended or superseded (its rename-is-major call is marked revisable on renames inflating the major number). A check whose prices are read from the ADRs survives that; one with a hardcoded bump word does not. If the changesets tool stops carrying the declared type straight through to the version computation, case 4's place in the gate should be re-examined.
