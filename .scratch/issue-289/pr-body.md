# G10: a changeset's declared bump type must agree with its diff (#289)

Branch: `agent/issue-289`. Code head: `cafa6fb` (R6). Base: `origin/main` at `4ebc0df`.

At `cafa6fb` the branch diff vs `origin/main` is exactly the four files listed below. This hand-off (`.scratch/issue-289/pr-body.md`) is a factory file the runner reads and removes before the push; it is not part of the published diff and is not listed as a branch file. Counts in this body were run at `cafa6fb`; nothing after that commit changed gate code or tests.

## What this branch ships

`scripts/release_gate.py` gains check **G10**. A changeset declares its own `major` / `minor` / `patch` line, and nothing used to check that declaration against what the changeset changed. G10 reads the declared-surface prices from the ADRs on disk — never from a constant in the gate — and refuses a changeset whose declared bump contradicts its own diff. At release, the version must match the exact SemVer result of the changesets it consumes.

The branch also carries the CI wiring (poison controls under the `release-gate` job) and the control suite in `scripts/test_bump_classification.py`. A R5-1 code change closed a bypass: under the old frontmatter regex, `major # comment` passed G10 because the trailing YAML comment was not stripped before classification. The regex at `changeset_declared_bumps` now accepts a trailing `#` comment on a bump line, and the control `case 3: a commented major declaration is refused` pins it.

A R5-2 code change closed the root cause behind that bypass: `changeset_declared_bumps` must refuse, not skip, a frontmatter line it cannot parse. Any bump line the parser does not recognise (a `!!str` tag, an unquoted multi-word value, or another YAML form) makes G10 report the changeset and the line, single-reason. This round (R6) extends that refusal to the two paths the R5-2 controls did not cover: the release path (a consumed plan holding `!!str major`) and the git-absent path (an unparseable pending changeset when git is not on PATH).

A R6-4 code change corrects the git-absent message. It used to say the unreadable line "cannot be refused"; the gate does refuse it. The message now says the line cannot be checked against the branch diff — which is what git's absence actually prevents.

## Files on this branch (the whole published diff vs `origin/main`)

| File | Role |
|---|---|
| `.changeset/g10-bump-classification-289.md` | Empty changeset (no bump): scripts and CI only, no card and no package behaviour change |
| `.github/workflows/tests.yml` | CI poison controls under the `release-gate` job, plus the `Bump-classification suite` step |
| `scripts/release_gate.py` | G10 itself: ADR-derived prices, cases 1–4, R5-1 regex, R5-2 refuse-not-skip, R6-4 git-absent message |
| `scripts/test_bump_classification.py` | 43 named controls, each planting one shape of defect or one silent pass |

## Counts at `cafa6fb` (commands run at that head)

- `scripts/test_bump_classification.py`: **43 controls**, **83 ok lines**, **0 FAIL**. PASS line names cases 1–4, B2(a–c), B3, R4-F3, R5-2, R6-1, R6-2, R6-3, the ADR-on-disk derivation, and the git-absent refusal.
- `scripts/test_release_gate.py`: **69 contract cases**, **205 ok lines**, **0 FAIL**. Includes the eight #342 git-absent cases that fail at `53a5b3a` merged with main.
- `python scripts/release_gate.py` (live tree): **RELEASE GATE: PASS** at version 3.0.1.
- `git diff --name-only origin/main...HEAD` at `cafa6fb`: **4 files**, listed above. No path under `.scratch/`.
- Mutant receipts (each mutant applied, named control observed red, mutant removed, control green again): **M4**, **M4b**, **M5**, **M2**, **minor-reset at `release_gate.py:1090`**, **major-reset at `release_gate.py:1088`**. All six killed.

CI G10 steps under the `release-gate` job: **10** — the `Bump-classification suite` step plus nine poison controls (inversion, cases 1–4, B2 push-to-main, B3 v3.0.0 shape, R5-2 `!!str` form, R5-2 multi-word form). R6-1, R6-2 and R6-3 run through the suite step; there is no dedicated CI poison step for them. This body does not claim one.

## Acceptance criteria

Each row states what satisfies the criterion, the test that pins it, and what was observed when the test was watched fail before the change and pass after.

### 1. A check refuses a changeset whose declared bump type contradicts its own diff, for each of the four cases

Satisfied by G10 in `scripts/release_gate.py` (`gate_bump_classification`, `_branch_declared_bumps`, `_consumed_declared_bumps`, `classify_surface_diff`, `required_price_for_diff`, `_refuse_delta_mismatch`).

| Case | Control that pins it | Before / after |
|---|---|---|
| 1. Rename declared below major | `case_case1_rename_declared_patch_is_refused`, `case_case1_rename_declared_minor_is_refused` | Before G10 the #286 changeset (eleven card-directory renames declared `patch`) was accepted: every gate was green and `release_gate.py --release` reported only G3, a tree-hygiene fact. After, both controls plant a rename and require G10 to name the rename and the ADR price. Watching each fail before the change is not applicable to this branch's controls — they were written against the shipped gate — but the historical finding is the observation: the same defect slipped past a green gate twice, under two careful human readings of the governing document. |
| 2. Admission or retirement declared patch | `case_case2_add_declared_patch_is_refused`, `case_case2_add_declared_quoted_patch_is_refused`, `case_case2_remove_declared_patch_is_refused` | Same shape: the planted `patch` admission is refused under G10 naming add/retire and the minor price from ADR 0003. |
| 3. No file under `skills/*/*/`, declared minor or major | `case_case3_no_surface_declared_minor_is_refused`, `case_case3_no_surface_declared_major_is_refused`, `case_case3_commented_major_is_refused`, `case_case3_non_card_directory_declared_minor_is_refused` | Scripts-only work declared `minor` or `major` is refused. The commented-declaration control is the R5-1 pin: before the regex fix, `major # comment` was read as no bump at all and the gate stayed green; after, it is refused. |
| 4. Release version disagrees with the consumed changesets | `case_case4_consumed_major_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_minor_delta_is_refused`, `case_case4_consumed_patch_with_no_delta_is_refused`, `case_case4_requires_the_exact_changesets_version`, `case_case4_no_consumed_plan_with_delta_is_refused`, `case_b3_v300_shaped_release_minor_delta_refused` | **Case 4 is built**, not sketched. `_consumed_declared_bumps` reads the plan at the merge-base (because `changeset version` deletes those files at HEAD); `_refuse_delta_mismatch` requires the release version to equal the exact SemVer result of that plan. The B3 control shapes a tree like the real v3.0.0 release (consumed major plus patches, delta major) and requires PASS; the same tree with a minor bump is REFUSED. |

### 2. It runs in the blocking gate, not as advice

Satisfied by G10 being called from `release_gate.py`'s `main()` on every run, ordinary and release. Errors land on the same `errors` list every other check uses; a non-empty list prints `RELEASE GATE: BLOCKED - N stale surface(s)` and exits 1. Pinned by every refusal control above (each requires non-zero exit and `G10:` in the output) and by `case_live_tree_gate_stays_green` / the live run at this head (PASS). Observation: before G10, the #286 defect produced a green gate; after, the same shape of tree exits non-zero under G10.

### 3. Controls that plant each refusable defect and prove the check goes red, run in CI

Satisfied by the 43 controls in `scripts/test_bump_classification.py` and by CI:

- `Bump-classification suite` runs that file and requires its `^PASS:` line.
- Nine poison controls under the `release-gate` job plant each refusable class in shell against the shipped gate and assert `G10:` (and, where the ticket requires it, `1 stale surface(s)` for single-reason).
- Static controls in the suite (`case_ci_runs_the_bump_classification_suite`, `case_ci_carries_the_inversion_poison_control`, `case_ci_carries_case1_to_case4_poison_controls`, `case_ci_carries_unparseable_bump_controls`, `case_ci_carries_b2_and_b3_controls`) read `.github/workflows/tests.yml` and refuse a CI that drops a step.

Observation: before this work, CI had no G10 controls at all; the #286 defect merged under a fully green CI. The inversion control failed in CI at `2cbdbce` (not `53a5b3a`): half two wrote `.changeset/zzz-rename.md` after `git checkout main` had removed the empty directory, `set -e` killed the step, and steps 18–23 never ran. The fix is `mkdir -p "$tree/.changeset"` before half two's write; the static control `case_ci_carries_the_inversion_poison_control` now checks for that line. The other six G10 poison controls already exited 0 at that head.

### 4. A control proves the check stays silent on a correctly classified changeset

Satisfied by the positive controls:

- `case_positive_correct_classification_is_silent` — scripts-only change declared `patch`.
- `case_positive_rename_major_passes` — rename declared `major` (ADR 0003).
- `case_positive_add_minor_passes` — admission declared `minor`.
- `case_frontmatter_comment_and_blank_line_passes` (R6-3) — correctly declared `patch` with a full-line `#` comment and a blank line in frontmatter.
- `case_case4_consumed_major_with_major_delta_passes`, `case_b3_v300_shaped_release_passes` — release deltas that match their consumed plan.
- `case_case4_unchanged_version_with_no_consumed_plan_passes` (N1) — explicit `--release` on a released, clean main.
- `case_b2a_push_to_main_after_admission_passes`, `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes` — post-merge trees that must not be re-judged.
- `case_empty_changeset_is_not_a_classification_fault` — `changeset add --empty` declares no bump; G10 must not invent one.
- `case_ard_text_is_read_not_hardcoded` — a fixture that rewrites ADR 0003 so a rename prices as patch accepts rename+patch.

Observation: before N1, an explicit `--release` run on a released, clean main failed G10 with the false message `release version changed from 3.0.1 to 3.0.1`; the control now requires PASS on that tree and was watched fail at `dfd1e45` before the fix at `1a60ef2`. Before R6-3, no control planted a full-line comment plus blank line; deleting the parser's skip makes a correctly classified changeset refuse, and the control goes red.

### 5. A control specifically pins the inversion: rename+major PASSES, rename+minor REFUSED

Satisfied by the pair:

- Pass half: `case_positive_rename_major_passes`.
- Refuse half: `case_case1_rename_declared_minor_is_refused`.
- CI: `Poison control - a card rename must be refused unless declared major` runs both halves in shell against the shipped gate.

ADR 0003 (`docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md`, lines 18–19) settled the rule: *Renaming a card is a major change. Admitting or retiring one remains a minor change.* A control that only tested the refusing direction would also pass under the superseded rule that required `minor`; both halves are required. Observation: the #286 changeset was classified `patch`, then corrected to `minor` under ADR 0002 as it then stood, then corrected again to `major` under ADR 0003 — two careful human readings, both wrong on the day they were made. That is the argument for the check.

### 6. Classification is derived from ADR 0003 by reading the repository, not from a hardcoded bump word

Satisfied by `derive_bump_prices` in `scripts/release_gate.py`. It reads `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` and `docs/adr/0002-a-release-is-a-delivery-event.md` on every run, extracts the decision sentences, and fails closed when an ADR is missing, unreadable, or no longer carries the sentence. The only constant in the file is `BUMP_RANK`, used solely to order words the ADRs supply. Pinned by:

- `case_ard_text_is_read_not_hardcoded` — rewrite the fixture ADR so a rename prices as `patch`; a rename declared `patch` then PASSES.
- `case_missing_ard_fails_closed_when_classification_needed` — delete the ADRs; classification is needed, so the gate refuses naming ADR.

Observation: a constant written into the script would be a cache of ADR 0003 and would go stale the same way `README.md:66` did — that line once supported the minor reading and now says the opposite. Reading the repository is what keeps the check alive when the ADR is amended.

## Rework items, as the branch stands

### B1 — merge main; git-absent G10 refuses in its own words

`origin/main` was merged at `a07c55d`. Since #347, `_is_git_work_tree` and `_git_ok` raise `GitUnavailableError` when git is missing; G10 catches it in `gate_bump_classification` and refuses under its own check ID with no traceback. Pinned by `case_g10_refuses_in_its_own_words_when_git_is_absent` and by the eight #342 git-absent cases in `scripts/test_release_gate.py`. Observation: at `53a5b3a` merged with main those eight cases fail (G10 died with a traceback); at this head all 69 release-gate cases pass, including those eight.

### B2 — cases 1–3 judge only the changesets this branch adds

`_branch_added_changeset_names` is `names_at(HEAD) - names_at(merge_base)`. Pending changesets that main already holds were classified when their own branch ran this gate. Pinned by `case_b2a_push_to_main_after_admission_passes`, `case_b2b_next_scripts_only_pr_passes`, `case_b2c_replay_push_to_main_at_316_passes`, and the CI control `Poison control - a push to main must not re-judge main's pending changesets`. Observation: before this, a push to main after an admission merged with a correctly declared `minor` changeset was refused as case 3 — the pending file sat on main against an empty branch diff. All three controls require PASS.

### B3 — case 4 compares the release version with the consumed changesets

Built as specified, not with the card diff. A release PR runs `npm run version`, which deletes the consumed `.changeset/*.md` files and writes the new number; the gate reads those files at the merge-base. Pinned by `case_b3_v300_shaped_release_passes` (v3.0.0-shaped tree, consumed major, delta major, PASS) and `case_b3_v300_shaped_release_minor_delta_refused` (same tree, minor bump, REFUSED), plus the CI control with both halves. Observation: before this, nothing in the gate read a changeset's bump line at all; a release could cut the wrong number and spend it permanently (ADR 0002).

### N1 — explicit `--release` on an unchanged version stays silent

`_refuse_delta_mismatch` returns when `required_bump is None` and `current_version == base_version`. Pinned by `case_case4_unchanged_version_with_no_consumed_plan_passes`. Observation: at `dfd1e45` this run failed with `release version changed from 3.0.1 to 3.0.1`; the control was watched fail before the fix and pass after (`1a60ef2`).

### R4-F3 — case-4 SemVer field resets on bases 1.2.1 and 2.1.1

Controls `case_case4_minor_plan_resets_patch_field` and `case_case4_major_plan_resets_minor_and_patch`. A minor plan over base 1.2.1 produces 1.3.0, not 1.3.1; a major plan over base 2.1.1 produces 3.0.0, not 3.1.1 or 3.0.1. The minor-reset mutant at `release_gate.py:1090` and the major-reset mutant at `release_gate.py:1088` are each killed by a named assertion (verified this round: mutant applied, control red, mutant removed, control green). This round corrected the control names, which still cited `:1063` and `:1065` — those lines moved when earlier G10 code landed; `:1088` and `:1090` are the current SemVer-reset lines.

### R5-1 — the regex fix stays, and is disclosed as a code change

The fix is in `changeset_declared_bumps`: the bump regex now accepts a trailing `#` comment (`(?:\s+#.*)?`). Under the old regex `major # comment` passed G10. Pinned by `case_case3_commented_major_is_refused`. Disclosed here because it is a code change on this branch, not only a test addition.

### R5-2 — the parser refuses unparseable lines, never skips them

`changeset_declared_bumps` raises `ChangesetBumpParseError` on any frontmatter line the bump regex does not recognise. Callers refuse, never skip. Pinned by `case_unparseable_yaml_tag_bump_is_refused` and `case_unparseable_multiword_bump_is_refused`, each asserting single-reason, and by the two CI poison controls. Observation: before R5-2 either form parsed to `{}`, so G10 had nothing to classify and the gate stayed green over a changeset whose declared bump was unreadable. This round's R6-1 and R6-2 close the same bypass on the release path and the git-absent path — the blind spot that let M4, M4b and M5 survive every R5-2 control, because those controls all planted the unreadable line in a branch-added changeset.

### R5-4 — no `.scratch/` path in the published branch diff

At `cafa6fb`, `git diff --name-only origin/main...HEAD` lists the four files above and nothing under `.scratch/`. The PR body is written to `.scratch/issue-289/pr-body.md` as a factory hand-off; the runner reads it and removes it before the push, so it never reaches the public skills tree. It is not listed as a published branch file.

### R6-1 — a `--release` control whose consumed plan holds `!!str major`

`case_case4_consumed_unparseable_plan_is_refused`. Base 2.0.0, head 2.0.1, consumed plan `!!str major` at the base commit, files deleted at HEAD (the shape a real release PR leaves). The control requires refusal under G10, naming `zzz-consumed-0.md` and the `!!str major` line, single-reason. Mutants: **M4** (delete the `errors.append` / `unparseable = True` in `_consumed_declared_bumps`) and **M4b** (delete `if consumed_unparseable: return`, which would add a second G10 fault on the version delta). Each was applied this round; each turned this control red by name; each was removed; the control passed again. Without the consumed-plan refusal, a release at 2.0.1 passes G10 over that line — the R5-2 bypass on the release path.

### R6-2 — a git-absent control whose only pending changeset is unparseable

`case_g10_refuses_unparseable_when_git_absent`. Tree carries only `.changeset/zzz-classify.md` with `!!str major`; `PATH` is emptied so git cannot run. The control requires non-zero exit, `G10:` naming the file and the line, no `Traceback`, and — pinning R6-4 — the message must **not** claim the unreadable line "cannot be refused". Mutant **M5** (delete the git-absent `if unparseable:` branch in `gate_bump_classification`) was applied this round; G10 went silent (neither `unparseable` nor `pending` is non-empty after a skip) and this control went red by name. The mutant was removed; the control passed again. Observation on R6-4: before the message fix, this control's "does not claim cannot be refused" assertion failed against the live output; after the fix it passes. The gate does refuse the line — git's absence only prevents checking it against the branch diff.

### R6-3 — a control whose frontmatter carries a full-line comment and a blank line, and passes

`case_frontmatter_comment_and_blank_line_passes`. The changeset declares `patch` for a scripts-only change — correctly classified — and its frontmatter carries a full-line `#` comment and a blank line above the bump. The control requires the gate to stay silent. Mutant **M2** (delete the `if not stripped or stripped.startswith("#"): continue` skip in `changeset_declared_bumps`) was applied this round; the parser raised on those lines, G10 refused a correctly classified changeset, and this control went red by name. The mutant was removed; the control passed again.

### R6-4 — the git-absent message and the R4-F3 line-number citations

Message corrected in `scripts/release_gate.py` as described above. R4-F3 control names now cite `release_gate.py:1088` (major reset) and `release_gate.py:1090` (minor reset). Both were verified this round by applying each reset mutant and watching the named control go red.

### Higher-classification control (rename + add in one changeset)

`case_higher_classification_governs_rename_plus_add` declares **minor** on a branch that both renames a card and adds one. The higher classification (major, from the rename) governs; minor is refused. Declaring minor is what kills a mutant that took the lower price or priced only the addition.

## What is not claimed

- This body does not claim that every acceptance checkbox is satisfied by a single test; each row names its own control.
- This body does not list `.scratch/issue-289/pr-body.md` as a published branch file. The runner removes it before the push; at `cafa6fb` the published diff is the four files above.
- This body does not claim dedicated CI poison steps for R6-1, R6-2 or R6-3. Those three run through the `Bump-classification suite` step.
- CI status on GitHub is not asserted from this container. Local suites are green at `cafa6fb`: 43 bump-classification controls, 69 release-gate cases, live gate PASS.
