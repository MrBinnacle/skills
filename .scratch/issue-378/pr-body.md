# #378 — halt-as-deliverable: broken Example pointer, S415 occasion, jargon, description routing

**Status: INCOMPLETE.** Fourth cold session on the same branch. Both hard prerequisites named by the ticket remain missing on this host. No card-text edit was made. No occurrence was recorded without its source. No Skill-tool success is claimed.

## Session re-verification (fourth cold session, 2026-10-06)

This body is the durable review record. A fourth unattended session re-ran every prerequisite check before any card-text edit. Results match the three prior sessions; nothing new unblocked them.

| Check | Command / observation | Result |
|---|---|---|
| Private research checkout | sibling path the dispatch-count script assumes (`../` from the repository root), and parent-of-parent | `No such file or directory` at both path interpretations. Filesystem search for the directory name and both cited filenames (`checkpoint-archive*`, `evaluation-chain*`, `tlc-*`, `*S523*`, `*S415*`, `*S414*`) under `/` returned nothing outside this worktree's own PR-body text. |
| Skill tool `mattpocock-skills:writing-for-agents` | Skill tool call this session | `Skill "mattpocock-skills:writing-for-agents" not found. Available skills: customize-opencode` |
| Skill tool `productivity/writing-for-agents` | Skill tool call (AGENTS.md name form, prior sessions) | not found |
| Skill tool `writing-for-agents` | Skill tool call (bare form, prior sessions) | not found |
| Example heading absent | headings in `SKILL.md` | Problem, Use when, Solution, Verification, Notes — **no Example heading**. Defect real at head. |
| Broken pointer | `gotchas.md:3-5` | Points to `` `SKILL.md` → Example ``. Text left unchanged, as the ticket requires. |
| Jargon present | `grep -nE 'PHASE B\|\bT3\b' case-study.md` | Hits at lines 6 (`T3`), 12 (`PHASE B`), 28 (`PHASE B'`) — none define the term. |
| Description routing gap | frontmatter parse | Neither `stale-handoff` nor `fix-and-re-run` appears in the description. Body table at SKILL.md:35 already contrasts the two paths; the description names neither. Length 193 chars (under the 200 bar). |
| SKILL.md size | `wc -c` | 5638 bytes — inside 400–7,168. |
| Occasions row | `EVIDENCE.md` | Opens `3 —` with three dated references. No S415 date added. |
| Dispatches row | `EVIDENCE.md` | Already carries `2 dispatches ... measured 2026-10-06`. Issue #374 has landed; this ticket does not edit that row. |
| Platform claim undated | `case-study.md:29-30` | `uses subscription auth` — undated, present. |
| GitHub auth | `gh auth status`; `GITHUB_TOKEN` | Not logged in; token unset. Issue-comment substitute is this body. |

Ticket instruction, verbatim: *"If the checkout is not readable, stop and comment on this issue; do not record an occurrence you have not read."* That fail-closed instruction fires. Criterion 9 additionally forbids every card-text edit this ticket needs until the Skill call succeeds; the call was attempted under the required name form this session and failed. The container holds no GitHub token, so this body is the comment.

## Acceptance-criteria checklist (build target)

1. `SKILL.md` has a heading containing `Example` with a filled, concrete example; the pointer at `gotchas.md:3-5` resolves to it (pointer text not rewritten).
2. The S415 occasion is a dated entry in a card `.md` file, cited in `Occasions counted`, with its evidentiary role named.
3. `grep -nE 'PHASE B|\bT3\b' skills/engineering/halt-as-deliverable/case-study.md` returns nothing, or each hit sits in a sentence that defines the term.
4. The `description` names the stale-handoff branch and the fix-and-re-run branch.
5. This ticket fixes no code defect. If the build changes a script or validator, a test is committed and seen failing on the pre-change code first.
6. Every validator and suite listed by `grep -rnE 'python3? +[^ ]*(validate_|test_)' .github/workflows/` (at the PR head) passes with `PYTHONUTF8=1`; this body lists each command with its final output line.
7. A changeset file under `.changeset/` for `mrbinnacle-skills` states what changes for a user who has the plugin installed.
8. Every platform, library or API claim this change adds or edits is re-checked through Context7 (or the vendor's live docs) and carries the check date beside it in the card text; this body lists each claim, the source and the date.
9. Card text is edited only after the implementer calls the Skill tool with `mattpocock-skills:writing-for-agents`; this body says that call was made.
10. Every touched `SKILL.md` is 400 to 7,168 bytes and its `description` is at most 200 characters (`scripts/validate_card_files.py` passes).
11. `pre-commit run --all-files` (the de-personalization gate) passes.

## Blocker 1 — private research checkout not present

The ticket requires reading two source records before any occasion may be recorded:

- `.claude/state/checkpoint-archive-S415.md:17` — the S415 two-arm halt (the occasion this ticket must record)
- `docs/research/evaluation-chain-batch-2-S414.md:216` — an evaluation noting that the card's counted occasions record the discipline holding, not the failure the card names

Those paths sit in the maintainer's private research repository, which the ticket says must be beside this worktree at the sibling path the dispatch-count script assumes. That checkout is not on this host. Searched: parent of the worktree, the worktree parent's parent, `/tmp`, `/opt`, `/var`, `/usr/local`, and the whole filesystem for the directory name and for both cited filenames. Nothing found.

The ticket quotes the repair instruction from the S523 audit note, but it does **not** quote the content of the checkpoint archive or the evaluation note. The occasion's date, its evidentiary role (originating failure vs later application vs catch attributable to this card), and its de-personalized story are all in the unread source. Naming them without the source would be fabricated provenance.

What I did **not** do, because the source was unread:

- No dated entry for the S415 two-arm halt in `gotchas.md`, `case-study.md`, or any other card `.md` file.
- No increment of `Occasions counted` (still `3 —`).
- No inventing of an evidentiary role. The ticket requires the role be named from the source.

A build that records an occurrence it has not read is the failure this evidence-first collection exists to refuse. The honest incomplete stands.

## Blocker 2 — writing-for-agents Skill not available

Acceptance criterion 9, verbatim: *"Card text (`SKILL.md`, `EVIDENCE.md`, `gotchas.md`, aux files, descriptions) is edited only after the implementer calls the Skill tool with `mattpocock-skills:writing-for-agents`; the PR body says that call was made."*

This environment's Skill tool loads only `customize-opencode`. There is no mattpocock plugin, no `installed_plugins.json`, and no local skill under any path on the host. The required name form was attempted in this session; it returned not-found. Writing "that call was made" in this body without making it would be false.

That criterion gates every card-text edit this ticket needs:

- Example section in `SKILL.md` (criterion 1)
- S415 occasion record (criterion 2)
- Jargon definition in `case-study.md` (criterion 3)
- Description rewrite for stale-handoff and fix-and-re-run branches (criterion 4)
- Platform-claim dating in card text (criterion 8)

Without the Skill call, none of those edits may be made. No card file was edited.

## Read-before-write observations at head

Branch: `agent/issue-378`. Head is clean at session start. Worktree is one git checkout; nothing outside it is used as a source of truth for card text.

| Check | Command / observation | Result |
|---|---|---|
| Broken pointer present | `gotchas.md` lines 3-5 name `` `SKILL.md` → Example `` | Present |
| Example heading absent | Headings in `SKILL.md`: Problem, Use when, Solution, Verification, Notes | **No Example heading** — defect is real at head, not absent |
| Jargon present, undefined | `grep -nE 'PHASE B\|\bT3\b' case-study.md` | Hits at lines 6 (T3), 12 (PHASE B), 28 (PHASE B') — none define the term |
| Description length today | frontmatter `description` | 193 characters — under the 200 bar; no rewrite made |
| SKILL.md size today | `wc -c` | 5638 bytes — inside 400–7,168 |
| Card validator baseline | `PYTHONUTF8=1 python scripts/validate_card_files.py` | PASS (pre-existing allowlisted reachability note for this card's EVIDENCE.md; recorded 2026-09-06, not introduced here) |
| Dispatches row | `EVIDENCE.md` | Already carries `2 dispatches ... measured 2026-10-06` — issue #374 has landed on this branch's base; this ticket still does not edit that row |
| Occasions row | `EVIDENCE.md` | Opens `3 —` with three dated references; no S415 date added |

## Validator roster (this session, incomplete tree)

Roster source, verbatim: `grep -rnE 'python3? +[^ ]*(validate_|test_)' .github/workflows/`. Every command below was run at the PR head with `PYTHONUTF8=1`. Final output lines are quoted.

This ticket changes no card text and no script, so this roster is a baseline of the incomplete tree, not a post-change gate. On a complete build the same roster must be re-run and each final line updated here.

| Command | Final output line (truncated where the line is long) | Exit |
|---|---|---|
| `python scripts/validate_card_files.py` | `PASS: 14 published card(s), all carry SKILL.md, gotchas.md and EVIDENCE.md; ... every SKILL.md carries a when-to-open pointer to gotchas.md -- EXCEPT the 14 allowlisted breach(es) listed above, recorded 2026-09-06 and not repaired by this gate` | 0 |
| `python scripts/test_validate_card_files.py` | `PASS: card-file conformance suite, all cases correct` | 0 |
| `python scripts/validate_scoreboard.py` | `PASS: ruled banner line pinned at 5 sites; records derive 14 admitted, 1 measured, 2 retired, 4 solutions looking for a problem; ... origin tiers 12 OBSERVED, 2 DESIGNED, 0 DISTILLED agree` | 0 |
| `python scripts/test_validate_scoreboard.py` | `PASS: every control fired` | 0 |
| `python scripts/test_captured_exit_handling.py` | `PASS: captured-exit handling, all assignments carry a failure branch` | 0 |
| `python scripts/test_validate_path_residue.py` | `PASS: path-residue checker verified across 8 temporary repositories plus the live tree; ...` | 0 |
| `python scripts/validate_path_residue.py` | `PASS: path residue - 343 tracked path(s), no residue term in any name` | 0 |
| `python scripts/test_vale_scope.py` | `PASS: vale scope - hook regex ... and CI paths ... partition 18 edge cases and 343 live tracked paths identically; ...` | 0 |
| `python scripts/test_link_skills_guard.py` | `FAIL no pwsh or powershell on PATH; this suite cannot verify the guard` | 1 |
| `python scripts/test_validate_quarantine_landing.py` | `PASS: quarantine-landing guard verified across 9 temporary repositories; ...` | 0 |
| `python scripts/test_validate_vale_style.py` | `PASS: vale-style checker verified across 12 temporary tree(s) plus the live tree; ...` | 0 |
| `python scripts/validate_vale_style.py` | `PASS: 8 vendored rules match ...; the generated marketing rule agrees with assets/tokens.json (15 words) and is bound to 4 declared surfaces.` | 0 |
| `python scripts/test_pretooluse_prose_snippets.py` | `PASS: tab_indented_heredoc_keeps_next_command, plain_heredoc_still_split, ...` | 0 |
| `cd skills/engineering/im-down && python test_validate_packet.py` | `PASS: clean, stale, incomplete, ... no-drift` | 0 |
| `cd skills/engineering/im-up && python test_validate_packet.py` | `PASS: clean, stale, incomplete, ... no-drift` | 0 |
| `cd skills/engineering/im-down && python validate_packet.py fixture-stale.md --mode produce --repo-root <repo root>` | `{ "verdict": "REJECTED", "packet_id": "stale-1", ... }` | 2 (non-zero; poison control holds) |
| `python scripts/test_validate_disposition_counts.py` | `PASS: disposition-count check recomputes every stated count from the record` | 0 |
| `python scripts/validate_disposition_counts.py` | `PASS: CATALOG states no disposition count; record dispositions/2026-08-15-S295-admission-triage.md derives 9 triaged, 2 stand, 6 thin, 1 ceiling-likely` | 0 |
| `python scripts/test_check_prose_claims.py` | `PASS: 7 controls verified; the live tree passes and every planted defect is refused by name` | 0 |
| `python scripts/test_readme_admission_lead.py` | `PASS: README admission lead matches the card ledger` | 0 |
| `python scripts/test_validate_standing_costs.py` | `All cases passed (no failures)` | 0 |
| `python scripts/validate_standing_costs.py` | `PASS: 14 published card(s), all standing cost figures match the audit (via standing-costs.json; skill-harness not available)` | 0 |
| `python scripts/test_validate_site_links.py` | `PASS: site link suite, 8 checks` | 0 |
| `python scripts/validate_site_links.py` | `PASS: every site link resolves, anchors included` | 0 |
| `python scripts/test_release_model_disclosure.py` | `PASS: release-model disclosure matches ADR 0002 on every surface that states the model` | 0 |
| `python scripts/test_validate_skill_formats.py` | `PASS: skill-format gate suite, all cases correct` | 0 |
| `python scripts/validate_skill_formats.py` | `PASS: 47 skill folder(s), 153 file(s), all declared readable formats (.md, .txt, .py, .json), 2 git-ignored file(s) skipped` | 0 |
| `python scripts/test_validate_voice_provenance.py` | `PASS: voice-provenance suite, all cases correct` | 0 |
| `python scripts/validate_voice_provenance.py` | `PASS: 6 voice specimen(s), each equal to a recorded line in VERBATIM.md and cited to the section and date that holds it` | 0 |
| `python scripts/test_validate_brand_kit.py` | `PASS: brand-kit checker verified across 45 temporary tree(s) plus the live tree; ...` | 0 |
| `python scripts/validate_brand_kit.py` | `PASS: brand kit 0.1.0 enforced - 176 public copy surface(s) scanned against 15 banned word(s), 1 asset pair(s) hash-verified, ...` | 0 |
| `python scripts/test_design_enforcement_claim.py` | `PASS: DESIGN.md enforcement-claim accuracy verified; ...` | 0 |
| `python scripts/test_validate_conformance.py` | `PASS: conformance v4 suite, all cases correct` | 0 |
| `python scripts/validate_conformance.py --root .` | `PASS: conformance v4: 14 card(s) x 4 card obligation(s) + 4 repo obligation(s) = 60 cells: 46 PASS, 0 FAIL, 14 CANNOT-CHECK. CANNOT-CHECK is not a pass -- 14 cell(s) were not verified by this run.` | 0 |
| `python scripts/test_validate_eval_corpora.py` | `PASS: eval-corpus checker verified across 17 temporary tree(s) plus the live tree; ...` | 0 |
| `python scripts/validate_eval_corpora.py` | `PASS: 14 eval corpus/corpora for 14 published card(s), 44 case(s) total; every corpus names its card and states at least 3 cases with 2 assertions each. ...` | 0 |
| `python scripts/test_release_gate.py` | `PASS: release gate verified across 69 contract case(s) - seeded trees, the live tree, and the CI wiring - ...` | 0 |
| `python scripts/test_install_form.py` | `FAIL claude CLI available for the live cold-install check: no claude on PATH; criterion 2 cannot be exercised here` / `1 FAILED` | 1 |
| `PYTHONUTF8=1 python scripts/test_validate_spec_conformance.py` | `PASS: spec-conformance allowance suite, all cases correct` (live npx run is CI's) | 0 |
| `PYTHONUTF8=1 python scripts/validate_spec_conformance.py --root .` | `PASS: 38 card(s) checked against skills-ref@0.1.5; 21 declared divergence(s) tolerated and reported; 0 breach(es). A tolerated divergence is not a silent pass.` | 0 |
| `pre-commit run --all-files` | `Taste prose (error level) on staged markdown under README.md, CATALOG.md, skills/, docs/.......................Passed` | 0 |

Two suites fail for **environmental** reasons on this host, not because of this branch:

1. `scripts/test_link_skills_guard.py` — no `pwsh` or `powershell` on PATH. The suite refuses to print a pass line for a check that never ran. Not installable from this container's tooling without leaving the worktree.
2. `scripts/test_install_form.py` — no `claude` CLI on PATH. The suite deliberately FAILS rather than skips when the CLI is absent. Not installable from this container without network plugin install outside the worktree.

Both failures are pre-existing host gaps. This branch changes no script, no validator, and no card text that either suite reads. On a host with `pwsh` and `claude` available, both must be re-run and their final lines updated here.

Host git configuration note carried from a prior session: `git config --global --add safe.directory '*'` was required so `scripts/test_check_prose_claims.py` controls that copy the live tree into `/tmp` can run `git ls-files`. Without it that suite fails on `dubious ownership`. After the fix the suite is green. This is host git configuration, not a repository change.

## Acceptance criteria — status

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Example heading + filled example; pointer resolves | **Not met** | No Example heading at head; no edit made (Skill-call gate) |
| 2 | S415 occasion dated, counted, role named | **Not met** | Research checkout absent; no occurrence invented |
| 3 | PHASE B / T3 defined or removed in case-study.md | **Not met** | Hits still at lines 6, 12, 28; no edit made (Skill-call gate) |
| 4 | Description routes stale-handoff and fix-and-re-run | **Not met** | Description unchanged (193 chars, pre-existing text) |
| 5 | No code defect; red-then-green for any script change | **N/A — satisfied by inaction** | No script or validator changed |
| 6 | Validators and suites green at PR head | **Baseline run complete; two environmental failures** | Full roster table above. Commands exit 0 except the two missing-host-tool suites. No card change exists to gate. |
| 7 | Changeset for `mrbinnacle-skills` | **Not met** | No user-visible card change to describe; a changeset claiming a repair would be false |
| 8 | Platform claims re-checked and dated | **Not met** | The undated `subscription auth` claim at case-study.md:29-30 is left as-is. The card-text edit that would carry a date is gated on the writing-for-agents Skill call. |
| 9 | Skill tool call `mattpocock-skills:writing-for-agents` | **Not met — call attempted and failed** | Skill tool returned not-found for the required name form this session. This body does not claim the call succeeded. |
| 10 | SKILL.md size and description bar | **Baseline only** | 5638 bytes, 193-character description — both inside bounds *before* any edit; no post-edit measurement possible |
| 11 | `pre-commit run --all-files` | **Met for this incomplete tree** | `pre-commit run --all-files` passed every hook this session. Must be re-run after card-text edits on a complete build. |

## Mutation campaign

None. No code or validator was changed, so no mutant was applied and no named assertion killed a mutant. `scripts/mutation_receipt.py` was not run; it needs a committed tree carrying a code change, and there is none.

## Tests that would pin each criterion (for the next build)

These are the tests this incomplete build did **not** get to write. They are named so the follow-on session does not start from zero:

1. **Example pointer** — a card-file check or a link/anchor test that asserts `SKILL.md` contains a heading whose text includes `Example` and that the `gotchas.md` pointer target resolves. Pin by asserting the heading exists; the pointer text stays as written. Fail-before: current tree has no such heading.
2. **Occasion record + count** — `scripts/validate_card_files.py` already enforces both directions: the integer opening `Occasions counted` must equal the number of dates in the row, and every date in the row must appear in another `.md` file under the card; a dated line carrying `occurrence`/`occurrences` must have its date in the row. Writing the S415 dated entry and incrementing the row is what makes that check bite. Fail-before: incrementing without a corroborating dated record, or recording without citing, reds the suite. The suite already has cases for both directions (`a count above its dated references is rejected`, `a dated occurrence record the row does not cite is rejected`).
3. **Jargon** — the ticket's own grep is the pin: `grep -nE 'PHASE B|\bT3\b' case-study.md` must return nothing, or each hit must sit in a defining sentence. Fail-before is the current three undefined hits.
4. **Description routing** — assert the frontmatter `description` string contains the stale-handoff trigger phrase and the fix-and-re-run phrase, and that length stays ≤ 200 (`scripts/validate_card_files.py`). Fail-before: current description names neither branch. Note: SKILL.md's body table at line 35 already contrasts the two paths; the criterion is about the **description**, which is the retrieval surface.
5. **Size and description bars** — already covered by `scripts/validate_card_files.py` / `scripts/test_validate_card_files.py`; no new test needed beyond keeping the card inside the bars after the edit.
6. **Platform claim date** — a prose claim check (or a review pin) that any `subscription auth` sentence in `case-study.md` carries a check date beside it. Fail-before: current undated sentence at case-study lines 29-30.
7. **No code defect** — this ticket must not change `scripts/` or `skills/*/validate_*.py`. A follow-on that does must add a test first and quote the red run in the PR body.

## Platform claims

| Claim | Where | Source used | Date | Status |
|---|---|---|---|---|
| Claude Code uses subscription auth (no `ANTHROPIC_API_KEY` required in that environment) | `case-study.md` lines 29-30 | Not re-checked | — | **Left undated.** Ticket requires re-check through Context7 or vendor docs *and* a date beside the claim in the card text. The card-text edit that would carry the date is gated on the writing-for-agents Skill call, which is unavailable. Do not half-apply the date without the Skill-call precondition. |

No other platform, library or API claim was added or edited by this incomplete build. This host has no Context7 tool in the available tool set; a follow-on with Context7 available must re-check the subscription-auth claim against Claude Code's live docs and date it in the card text.

## Changeset

None. A changeset describes what changes for a user who has the plugin installed. No card text changed; a changeset claiming a repair would be false. The existing `.changeset/` entries on this branch are unrelated (prior tickets).

## Issue-comment attempt

Ticket: *"If the checkout is not readable, stop and comment on this issue."*

Attempted prerequisite: `gh auth status` → not logged into any GitHub hosts. No token in the environment (`GITHUB_TOKEN` unset). Network calls against the GitHub API are also forbidden by this launch's constraints (one prior `urlopen` against the API idled a build for thirty minutes). The comment could not be posted. This PR body is the substitute record.

## What unblocks this ticket

1. Place the private research checkout beside this worktree at the sibling path the dispatch-count script assumes, with `checkpoint-archive-S415.md` and `evaluation-chain-batch-2-S414.md` readable at the lines the ticket names. Re-confirmed absent on this host in four consecutive sessions.
2. Install or load `mattpocock-skills:writing-for-agents` so the Skill tool can be called before any card-text edit. Re-confirmed unavailable this session; the required name form returns not-found.
3. Provide a GitHub token if the runner still requires an issue comment; otherwise treat this body as that comment.
4. For criterion 6 on a complete build: a host with `pwsh`/`powershell` and the `claude` CLI on PATH, so `test_link_skills_guard.py` and `test_install_form.py` can run.

## Companion artifacts

- Issue: #378 of MrBinnacle/skills (tracker text supplied in the launch; not re-fetched from the network).
- Blocked by: #374 (dispatch-count rewrite). Observation: `EVIDENCE.md` already carries the measured dispatch row dated 2026-10-06, so #374 has landed on this branch's base; this ticket still does not edit that row.
- Source records named by the ticket but **not present on this host**: private research checkout paths `.claude/state/checkpoint-archive-S415.md` and `docs/research/evaluation-chain-batch-2-S414.md`, plus the S523 audit notes. Those files do not exist here; nothing in this PR body quotes them as read.
- Scratch evidence body: `.scratch/issue-378/pr-body.md` (this file). The runner reads it off the branch and removes it before push; it is not part of the final diff and must not be cited as a changed file.
- Changeset: none.
- Mutation receipt: none (no code change).

## Bottom line

Every acceptance checkbox that depends on card text or on the S415 source record is unmet. The two hard prerequisites — the private research checkout and the writing-for-agents Skill — are both absent, and both were re-verified independently this session. The tree is otherwise green at baseline: card-file validator PASS, de-personalization gate PASS, workflow validators exit 0, two environmental failures unrelated to this branch. No occurrence was invented. No Skill-tool success is claimed. The incomplete stands.
