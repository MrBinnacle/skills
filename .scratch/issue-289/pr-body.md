# #289 — G10: a changeset's declared bump type must match its diff

Branch `agent/issue-289`. Head recorded in this body: `ad23d43`.

## What this branch ships

`scripts/release_gate.py` gains check **G10**. On every run the gate reads the declared-surface prices from the ADRs on disk (`docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` and `docs/adr/0002-a-release-is-a-delivery-event.md`) and refuses a changeset whose `major` / `minor` / `patch` line disagrees with what its diff does under `skills/*/*/`. The price words are never hardcoded in the checker; `derive_bump_prices` parses the decision sentences from the repository on every run.

Cases 1–3 judge only the changesets **this branch adds** (new `.changeset/*.md` in `merge-base..HEAD`), never every pending file on disk. Case 4, at `--release`, compares the version delta against the changesets the release **consumes** — read at the merge-base, because `changeset version` deletes those files at HEAD. An explicit `--release` run on a released, clean main (version unchanged, no plan consumed) stays silent: there is no delta to price (N1).

When git is not on PATH, G10 catches `GitUnavailableError` and refuses in its own words, naming the pending changeset, with no traceback (#342 / #347 / B1).

**Code change disclosed in this round (R5-1, still on the branch):** `scripts/release_gate.py` carries a bump-line regex that accepts a trailing YAML comment (`major # comment`). Under the pre-fix regex that line did not match, the parser skipped it, and G10 stayed green over a declared major. The fix is pinned by `case_case3_commented_major_is_refused` in `scripts/test_bump_classification.py`.

**Code change this round (R5-2, commit `ad23d43`):** `changeset_declared_bumps` used to skip any frontmatter line its regex missed. A `!!str`-tagged or unquoted multi-word bump value parsed to `{}`, so G10 had nothing to classify and the gate printed `RELEASE GATE: PASS` over a changeset whose declared bump was unreadable. That was the root cause behind the R5-1 regex fix. Any non-comment frontmatter line the parser cannot read now raises `ChangesetBumpParseError`. Callers report G10 naming the changeset file and the line, single-reason, and never price a delta against a plan they cannot read.

## Files on this branch (the whole diff vs `origin/main`)

Exactly these four paths, from `git diff --name-only origin/main...HEAD`:

- `.changeset/g10-bump-classification-289.md`
- `.github/workflows/tests.yml`
- `scripts/release_gate.py`
- `scripts/test_bump_classification.py`

No path under `.scratch/` appears in that diff (`git ls-tree -r HEAD --name-only | grep -c '^.scratch'` = 0). This body file is a factory hand-off the runner reads and removes before the push; it is never a changed or committed file in the PR.

## Counts at the pushed head (`ad23d43`)

| Surface | Count | Command |
|---|---|---|
| `scripts/test_bump_classification.py` controls | **40** | PASS line of that suite |
| `ok` lines, bump-classification suite | **74** | `grep -c '^ok '` on the suite output |
| `scripts/test_release_gate.py` contract cases | **69** | PASS line of that suite |
| `ok` lines, release-gate suite | **205** | `grep -c '^ok '` on the suite output |
| G10-related CI steps under `Release gate (fit to release)` | **10** (1 suite step + 9 poison controls) | step names under the release-gate job |
| G10 CI steps executed locally against the shipped gate | **10 / 10 rc=0** | extracted `run:` blocks, `bash -e -o pipefail`, `RUNNER_TEMP` set |
| Live ordinary gate | **PASS** | `python scripts/release_gate.py` |

Nine named G10 poison controls under the release-gate job:

1. `Poison control - a card rename must be refused unless declared major` (inversion, both halves)
2. `Poison control - a rename declared below major must be rejected` (case 1)
3. `Poison control - a card admission declared patch must be rejected` (case 2)
4. `Poison control - no surface change declaring minor or major must be rejected` (case 3)
5. `Poison control - a release version delta that disagrees with the consumed plan` (case 4)
6. `Poison control - a push to main must not re-judge main's pending changesets` (B2 a–c)
7. `Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused` (B3)
8. `Poison control - a !!str-tagged bump line must be refused` (R5-2)
9. `Poison control - an unquoted multi-word bump line must be refused` (R5-2)

Plus step `Bump-classification suite`, which runs `scripts/test_bump_classification.py` and requires its PASS line.

## Acceptance criteria

### Done-when, original ticket

**1. A check refuses a changeset whose declared bump type contradicts its own diff, for each of the four cases.**

- Case 1 (rename, price from ADR 0003 = major): pinned by `case_case1_rename_declared_patch_is_refused`, `case_case1_rename_declared_minor_is_refused`, and CI control 2. At the final head the suite reports both `ok` and the CI step prints `control: rename declared patch rejected under G10, single-reason`.
- Case 2 (admit/retire, price = minor): pinned by `case_case2_add_declared_patch_is_refused`, `case_case2_remove_declared_patch_is_refused`, `case_case2_add_declared_quoted_patch_is_refused`, and CI control 3.
- Case 3 (no file under `skills/*/*/`, only patch may stand): pinned by `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_commented_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused`, and CI control 4.
- Case 4 (release version vs consumed plan): pinned by `case_case4_consumed_major_with_major_delta_passes`, `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_no_delta_is_refused`, `case_case4_requires_the_exact_changesets_version`, `case_case4_no_consumed_plan_with_delta_is_refused`, and CI controls 5 and 7. Case 4 is **built**: the gate prices the consumed changesets at the merge-base and requires the exact SemVer result those bumps produce, including field resets.
- Higher classification: a rename and an addition in one changeset resolve to major. Pinned by `case_higher_classification_governs_rename_plus_add`, whose fixture declares **minor** — a mutant that took the lower price would accept it.

**2. It runs in the blocking gate, not as advice.**

`main()` calls `gate_bump_classification` in both ordinary and release mode. Failures are listed under `G10:` and force `RELEASE GATE: BLOCKED` (exit 1). Pinned by the live ordinary run (`RELEASE GATE: PASS` at version 3.0.1 with no G10 fault) and by every refusal control asserting the message, never only a non-zero exit.

**3. Controls plant each refusable defect and prove the check goes red; those controls run in CI.**

Suite: 40 controls in `scripts/test_bump_classification.py`. CI: the suite step plus the nine poison controls above, under `Release gate (fit to release)`. Local execution of all ten G10-related CI steps at this head: every one rc=0, each printing its `control:` line.

**4. A control proves the check stays silent on a correctly classified changeset.**

`case_positive_correct_classification_is_silent`: a scripts-only change declared `patch` passes. `case_positive_rename_major_passes` and `case_positive_add_minor_passes` cover the other two correct prices. Empty changesets declare nothing and are not refused (`case_empty_changeset_is_not_a_classification_fault`).

**5. Inversion pin: rename + `major` PASSES, rename + `minor` is REFUSED.**

Pinned by `case_positive_rename_major_passes` (pass half) and `case_case1_rename_declared_minor_is_refused` (refuse half), and by CI control 1, which plants the rename twice — minor refused, major PASS. Historical: that CI step failed at `2cbdbce` (S512 F1) because half two wrote `.changeset/zzz-rename.md` into an empty `.changeset/` that `git checkout main` had removed, so the major half never ran and `-e` skipped the remaining G10 controls. The fix is `mkdir -p "$tree/.changeset"` before half two's write; the static control `case_ci_carries_the_inversion_poison_control` pins that mkdir. At the final head the inversion step is green locally and in the suite.

**6. Classification is derived from ADR 0003 by reading the repository, not from a hardcoded bump word.**

`derive_bump_prices` opens the two ADRs on disk and regexes the decision sentences. Pinned by `case_ard_text_is_read_not_hardcoded` (an ADR rewritten to price rename as `patch` accepts rename+`patch`) and `case_missing_ard_fails_closed_when_classification_needed` (no ADR text → refuse, never guess).

### Rework requirements

**B1 — merge `origin/main`; G10 catches `GitUnavailableError`.**

Merged at `a07c55d` (and the branch carries that merge through `ad23d43`). Since #347, `_is_git_work_tree` and `_git_ok` raise `GitUnavailableError` when git is missing. G10 catches it in `gate_bump_classification` and refuses under G10, naming git and the pending changeset, with no traceback. Pinned by `case_g10_refuses_in_its_own_words_when_git_is_absent` and `case_g10_is_silent_when_git_absent_and_no_declared_bump`. `python scripts/test_release_gate.py` passes all **69** cases at the final head, including the eight #342 git-absent cases.

**B2 — cases 1–3 judge only branch-added changesets.**

`_branch_declared_bumps` diffs `merge-base..HEAD` file sets. Controls: `case_b2a_push_to_main_after_admission_passes` (push to main after a correct minor admission PASSES), `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes`, and CI control 6.

**B3 — case 4 prices the consumed plan, not the card diff.**

`_consumed_declared_bumps` reads the deleted `.changeset/*.md` files at the merge-base via `git show`. Controls: `case_b3_v300_shaped_release_passes` and `case_b3_v300_shaped_release_minor_delta_refused`, and CI control 7, which replays the real v3.0.0 shape (4c00b0e).

**Rename+add control declares minor** so the "higher classification governs" mutant is killed: `case_higher_classification_governs_rename_plus_add`.

**R4-F3 — SemVer field resets on bases 1.2.1 and 2.1.1.**

`case_case4_minor_plan_resets_patch_field` (minor over 1.2.1 → 1.3.0; refuses unreset 1.3.1) and `case_case4_major_plan_resets_minor_and_patch` (major over 2.1.1 → 3.0.0; refuses unreset 3.1.1 and 3.0.1). Each half names the mutant it kills (`release_gate.py:1065` minor-reset, `:1063` major-reset).

**N1 — explicit `--release` on an unchanged version stays silent.**

`case_case4_unchanged_version_with_no_consumed_plan_passes`. In `_refuse_delta_mismatch`, when `required_bump is None` and `current_version == base_version`, return without a fault. Without that return the run reported a false `release version changed from X to X`.

**R5-1 — the regex fix at the bump-line parser stays.**

Present on the branch (commit `c09fe3f`) and still present at `ad23d43`. Disclosed above as a code change: under the old regex, `major # comment` passed G10. Pinned by `case_case3_commented_major_is_refused`.

**R5-2 — `changeset_declared_bumps` refuses, not skips, an unparseable bump line.** (This round.)

Implementation at `ad23d43`:

- New `ChangesetBumpParseError(ValueError)` in `scripts/release_gate.py`.
- `changeset_declared_bumps` ignores blank lines and full-line `#` comments; any other frontmatter line the bump regex cannot read raises, naming the line.
- `_read_declared_bumps` and `_consumed_declared_bumps` report `G10: <file> has a frontmatter line the bump parser cannot read: '<line>'` and return no bump for that file. A consumed plan carrying such a line refuses without pricing a delta (single-reason).
- The git-absent path reports unparseable pending lines under G10 as well.

Named controls per unparseable form:

| Control | Form planted | Result at `ad23d43` | Skip-mutant kill |
|---|---|---|---|
| `case_unparseable_yaml_tag_bump_is_refused` | `"mrbinnacle-skills": !!str major` | REFUSED under G10, single-reason (`1 stale surface(s)`, names `zzz-classify.md` and `!!str major`) | Restoring `if match: ...` with no else made this control fail with `ACCEPTED the planted defect` |
| `case_unparseable_multiword_bump_is_refused` | `"mrbinnacle-skills": major release` | REFUSED under G10, single-reason (names `major release`) | Same mutant, same failure |
| CI `Poison control - a !!str-tagged bump line must be refused` | same `!!str` form | rc=0 locally; asserts G10, file name, line, single-reason | — |
| CI `Poison control - an unquoted multi-word bump line must be refused` | same multi-word form | rc=0 locally; same assertions | — |

Before the change, both suite fixtures printed `RELEASE GATE: PASS` (the parser skipped the line, returned `{}`, and G10 had nothing to classify). After the change both refuse. The mutant that restores the skip is killed by those two control names.

### Body honesty (R5-3 / F2 / round-2 F2)

- Every file listed above exists in `git diff --name-only origin/main...HEAD`.
- Every count in the table comes from a command run at `ad23d43`.
- No `.scratch/` path is claimed as committed or as part of the PR diff.
- No `HEAD DISAGREEMENT` text and no runner note from an earlier round remains.
- No sentence says the code is unchanged when it changed. R5-1 and R5-2 are both disclosed as code changes, with the reason each fix exists.
- The inversion control's historical CI failure is recorded at `2cbdbce`, not `53a5b3a`.

### Required check `Release gate (fit to release)`

This container holds no GitHub token, so the GitHub check itself cannot be observed from here. What was executed locally against the shipped head:

- `Release-gate suite` step: **PASS**, 69 contract cases.
- `Run release gate` step (ordinary mode on the live tree): **PASS**.
- All ten G10-related steps (suite + nine poison controls): **rc=0**, each printing its `control:` line.
- Legacy non-npx release-gate controls also re-run here and passed: drifted manifest, unrolled changelog, mutable workflow ref, ordinary-vs-release ref set, and the live ordinary gate.

Steps that call `npx` (changesets `status`, skills-ref) were not fully re-exercised in this container; each `npx` invocation is multi-second and the harness runs its own fail-closed compound gate.

## Suite PASS lines at `ad23d43`

```
PASS: 40 controls verified; each planted defect is refused by G10, the inversion is pinned, cases 1-3 judge only branch-added changesets, case 4 prices the consumed plan and the SemVer reset fields (R4-F3: minor over 1.2.1 -> 1.3.0, major over 2.1.1 -> 3.0.0), the ADR text on disk drives classification, G10 refuses in its own words when git is absent and a declared bump is pending, an unchanged version at explicit --release stays silent when no plan was consumed, and the CI poison controls carry the inversion, cases 1-4, B2(a-c), B3, and the R5-2 unparseable-bump refusals
```

```
PASS: release gate verified across 69 contract case(s) - seeded trees, the live tree, and the CI wiring - every refusal asserting its own message, never only a non-zero exit.
```

## Which test covers which criterion

| Criterion | Pinning test / CI control |
|---|---|
| Case 1 refuse | `case_case1_rename_declared_{patch,minor}_is_refused`; CI control 2 |
| Case 2 refuse | `case_case2_add/remove/quoted_declared_patch_is_refused`; CI control 3 |
| Case 3 refuse | `case_case3_no_surface_declared_{minor,major}_is_refused`, `case_case3_commented_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused`; CI control 4 |
| Case 4 built | `case_case4_*` (seven cases); CI controls 5 and 7 |
| Higher classification | `case_higher_classification_governs_rename_plus_add` (declares minor) |
| Blocking gate | live `python scripts/release_gate.py`; every control asserting the refusal message |
| Silent on correct | `case_positive_correct_classification_is_silent`, `case_positive_rename_major_passes`, `case_positive_add_minor_passes` |
| Inversion | `case_positive_rename_major_passes` + `case_case1_rename_declared_minor_is_refused`; CI control 1 (both halves + mkdir pin) |
| ADR from disk | `case_ard_text_is_read_not_hardcoded`, `case_missing_ard_fails_closed_when_classification_needed` |
| B1 git-absent | `case_g10_refuses_in_its_own_words_when_git_is_absent`; `test_release_gate.py` 69 cases |
| B2 branch-added only | `case_b2a/b2c`; CI control 6 |
| B3 consumed plan | `case_b3_*`; CI control 7 |
| N1 unchanged `--release` | `case_case4_unchanged_version_with_no_consumed_plan_passes` |
| R4-F3 resets | `case_case4_minor_plan_resets_patch_field`, `case_case4_major_plan_resets_minor_and_patch` |
| R5-1 comment regex | `case_case3_commented_major_is_refused` |
| R5-2 unparseable refuse | `case_unparseable_yaml_tag_bump_is_refused`, `case_unparseable_multiword_bump_is_refused`; CI controls 8 and 9 |
| CI wiring | `case_ci_runs_the_bump_classification_suite`, `case_ci_carries_the_inversion_poison_control`, `case_ci_carries_case1_to_case4_poison_controls`, `case_ci_carries_unparseable_bump_controls`, `case_ci_carries_b2_and_b3_controls` |
