# #378 — halt-as-deliverable: broken Example pointer, S415 occasion, jargon, description routing

**Status: INCOMPLETE.** Stopped before any card-text edit. Two hard prerequisites named by the ticket are missing on this host. No occurrence was recorded without its source. No Skill-tool claim is made that was not performed.

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

## Read-before-write observations at head

Branch: `agent/issue-378`. Head is clean. Worktree is one git checkout; nothing outside it is used as a source of truth for card text.

| Check | Command / observation | Result |
|---|---|---|
| Broken pointer present | `gotchas.md` lines 3-5 name `` `SKILL.md` → Example `` | Present |
| Example heading absent | Headings in `SKILL.md`: Problem, Use when, Solution, Verification, Notes | **No Example heading** — defect is real at head, not absent |
| Jargon present, undefined | `grep -nE 'PHASE B\|\bT3\b' case-study.md` | Hits at lines 6 (T3), 12 (PHASE B), 28 (PHASE B') — none define the term |
| Description length today | frontmatter `description` | 193 characters — under the 200 bar; no rewrite made |
| SKILL.md size today | `wc -c` | 5638 bytes — inside 400–7,168 |
| Card validator baseline | `PYTHONUTF8=1 python scripts/validate_card_files.py` | PASS (pre-existing allowlisted reachability note for this card's EVIDENCE.md; recorded 2026-09-06, not introduced here) |
| Dispatches row | `EVIDENCE.md` | Already carries `2 dispatches ... measured 2026-10-06` — issue #374 has landed; this ticket does not edit that row |
| Occasions row | `EVIDENCE.md` | Opens `3 —` with three dated references; no S415 date added |

## Blocker 1 — private research checkout not present

The ticket requires reading two source records before any occasion may be recorded:

- `.claude/state/checkpoint-archive-S415.md:17` — the S415 two-arm halt (the occasion this ticket must record)
- `docs/research/evaluation-chain-batch-2-S414.md:216` — an evaluation noting that the card's counted occasions record the discipline holding, not the failure the card names

Those paths are relative to the maintainer's private research repository, which the ticket says must sit beside this worktree at the sibling path `scripts/refresh_dispatch_counts.py` assumes. That checkout is not on this host. Searched: parent of the worktree (`/home/agent`), `/tmp`, `/opt`, `/var`, `/usr/local`, and the whole filesystem for the directory name and for both cited filenames. Nothing found.

Ticket instruction, verbatim: *"If the checkout is not readable, stop and comment on this issue; do not record an occurrence you have not read."*

The container holds no GitHub token. `gh auth status` reports not logged into any GitHub host. A comment on issue #378 cannot be posted from here. This PR body is the durable record the runner will publish.

What I did **not** do, because the source was unread:

- No dated entry for the S415 two-arm halt in `gotchas.md`, `case-study.md`, or any other card `.md` file.
- No increment of `Occasions counted` (still `3 —`).
- No inventing of an evidentiary role (originating failure vs later application vs catch attributable to this card). The ticket requires the role be named from the source; naming it without the source would be a fabricated provenance line.

A build that records an occurrence it has not read is the failure this evidence-first collection exists to refuse. The honest incomplete stands.

## Blocker 2 — writing-for-agents Skill not available

Acceptance criterion 9, verbatim: *"Card text (`SKILL.md`, `EVIDENCE.md`, `gotchas.md`, aux files, descriptions) is edited only after the implementer calls the Skill tool with `mattpocock-skills:writing-for-agents`; the PR body says that call was made."*

This environment's Skill tool loads only `customize-opencode`. There is no mattpocock plugin, no `installed_plugins.json`, and no local skill under any path on the host. Calling Skill with `mattpocock-skills:writing-for-agents` would fail; writing "that call was made" in this body without making it would be false.

That criterion gates every card-text edit this ticket needs:

- Example section in `SKILL.md` (criterion 1)
- S415 occasion record (criterion 2)
- Jargon definition in `case-study.md` (criterion 3)
- Description rewrite for stale-handoff and fix-and-re-run branches (criterion 4)
- Platform-claim dating in card text (criterion 8)

Without the Skill call, none of those edits may be made. No card file was edited.

## Blocker 3 — pre-commit (resolved during this session)

Criterion 11 requires `pre-commit run --all-files`. At session start the binary was absent from PATH and from the project venv. It was installed into the project venv (`pre-commit 4.6.2`) from PyPI; this is tooling install, not a card or validator change.

Observed after install, on the current tree (no card-text edits present):

```
pre-commit run --all-files
```

Final output line:

```
Taste prose (error level) on staged markdown under README.md, CATALOG.md, skills/, docs/.......................Passed
```

All hooks passed, including every residue check and `validate_path_residue.py`. The de-personalization gate is therefore green for this incomplete tree. On a complete build the same command must be re-run after the card-text edits, and this body updated.

Note: the residue hooks refuse the private research directory's name in any `*.md` file. This body and any future card text use a generic descriptor for that checkout — which this body already does.

## Acceptance criteria — status

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Example heading + filled example; pointer resolves | **Not met** | No Example heading at head; no edit made (Skill-call gate) |
| 2 | S415 occasion dated, counted, role named | **Not met** | Research checkout absent; no occurrence invented |
| 3 | PHASE B / T3 defined or removed in case-study.md | **Not met** | Hits still at lines 6, 12, 28; no edit made (Skill-call gate) |
| 4 | Description routes stale-handoff and fix-and-re-run | **Not met** | Description unchanged (193 chars, pre-existing text) |
| 5 | No code defect; red-then-green for any script change | **N/A** | No script or validator changed |
| 6 | Validators and suites green at PR head | **Not met as a deliverable** | Baseline `validate_card_files.py` PASS recorded above; full workflow roster not run because no card change exists to gate; would be run on a complete build |
| 7 | Changeset for `mrbinnacle-skills` | **Not met** | No user-visible card change to describe |
| 8 | Platform claims re-checked and dated | **Not met** | The ticket names one undated claim (`subscription auth` in `case-study.md` around lines 29-30). No card edit made, so no re-check was applied to card text. Left as-is rather than half-dated without the Skill-call precondition. |
| 9 | Skill tool call `mattpocock-skills:writing-for-agents` | **Not met** | Skill not installed; call not made; this body does not claim it was |
| 10 | SKILL.md size and description bar | **Baseline only** | 5638 bytes, 193-character description — both inside bounds *before* any edit; no post-edit measurement possible |
| 11 | `pre-commit run --all-files` | **Met for this incomplete tree** | Installed `pre-commit 4.6.2` into the project venv; `pre-commit run --all-files` passed every hook. Must be re-run after card-text edits on a complete build. |

## Mutation campaign

None. No code or validator was changed, so no mutant was applied and no named assertion killed a mutant.

## Tests that would pin each criterion (for the next build)

These are the tests the incomplete build did **not** get to write. They are named so the follow-on session does not start from zero:

1. **Example pointer** — a card-file check or a link/anchor test that asserts `SKILL.md` contains a heading whose text includes `Example` and that the `gotchas.md` pointer target resolves. Pin by asserting the heading exists; the pointer text stays as written.
2. **Occasion record + count** — `scripts/validate_card_files.py` already enforces both directions: the integer opening `Occasions counted` must equal the number of dates in the row, and every date in the row must appear in another `.md` file under the card; a dated line carrying `occurrence`/`occurrences` must have its date in the row. Writing the S415 dated entry and incrementing the row is what makes that check bite. Fail-before: incrementing without a corroborating dated record, or recording without citing, reds the suite.
3. **Jargon** — the ticket's own grep is the pin: `grep -nE 'PHASE B|\bT3\b' case-study.md` must return nothing, or each hit must sit in a defining sentence. Fail-before is the current three undefined hits.
4. **Description routing** — assert the frontmatter `description` string contains the stale-handoff trigger phrase and the fix-and-re-run phrase, and that length stays ≤ 200 (`scripts/validate_card_files.py`). Fail-before: current description names neither branch.
5. **Size and description bars** — already covered by `scripts/validate_card_files.py` / `scripts/test_validate_card_files.py`; no new test needed beyond keeping the card inside the bars after the edit.
6. **Platform claim date** — a prose claim check (or a review pin) that any `subscription auth` sentence in `case-study.md` carries a check date beside it. Fail-before: current undated sentence at case-study lines 29-30.
7. **No code defect** — this ticket must not change `scripts/` or `skills/*/validate_*.py`. A follow-on that does must add a test first and quote the red run in the PR body.

## Validator commands (baseline run, incomplete build)

Full workflow roster was not executed as a deliverable gate because no card change exists to gate. The one validator this ticket's domain would touch first was run as a baseline:

```
PYTHONUTF8=1 python scripts/validate_card_files.py
```

Final output line:

```
PASS: 14 published card(s), all carry SKILL.md, gotchas.md and EVIDENCE.md; every EVIDENCE.md states Occasions counted and Dispatches recorded and Re-screen trigger; every description is stated and within 200 characters; every SKILL.md is between 400 and 7168 bytes; every local link resolves with case matching; every reader-facing auxiliary reachable from SKILL.md; every SKILL.md carries a when-to-open pointer to gotchas.md -- EXCEPT the 14 allowlisted breach(es) listed above, recorded 2026-09-06 and not repaired by this gate
```

On a complete build, every command from:

```
grep -rnE 'python3? +[^ ]*(validate_|test_)' .github/workflows/
```

must be run at the PR head with `PYTHONUTF8=1`, and each final line quoted here. That roster includes the session-boundary parity suites and the poison control under `skills/engineering/im-{down,up}/`; this ticket does not touch those cards.

## Platform claims

| Claim | Where | Source used | Date | Status |
|---|---|---|---|---|
| Claude Code uses subscription auth (no `ANTHROPIC_API_KEY` required in that environment) | `case-study.md` lines 29-30 | Not re-checked | — | **Left undated.** Ticket requires re-check through Context7 or vendor docs *and* a date beside the claim in the card text. The card-text edit that would carry the date is gated on the writing-for-agents Skill call, which is unavailable. Do not half-apply the date without the Skill-call precondition. |

No other platform, library or API claim was added or edited by this incomplete build.

## Changeset

None. A changeset describes what changes for a user who has the plugin installed. No card text changed; a changeset claiming a repair would be false.

## Issue-comment attempt

Ticket: *"If the checkout is not readable, stop and comment on this issue."*

Attempted prerequisite: `gh auth status` → not logged into any GitHub hosts. No token in the environment. Network calls against the GitHub API are also forbidden by this launch's constraints (one prior `urlopen` against the API idled a build for thirty minutes). The comment could not be posted. This PR body is the substitute record.

## What unblocks this ticket

1. Place the private research checkout beside this worktree at the sibling path the dispatch-count script assumes, with `checkpoint-archive-S415.md` and `evaluation-chain-batch-2-S414.md` readable at the lines the ticket names.
2. Install or load `mattpocock-skills:writing-for-agents` so the Skill tool can be called before any card-text edit.
3. ~~Install `pre-commit`~~ — done this session; gate is green on the incomplete tree. Re-run after card-text edits.
4. Provide a GitHub token if the runner still requires an issue comment; otherwise treat this body as that comment.

## Companion artifacts

- Issue: #378 of MrBinnacle/skills (tracker text supplied in the launch; not re-fetched from the network).
- Blocked by: #374 (dispatch-count rewrite). Observation: `EVIDENCE.md` already carries the measured dispatch row dated 2026-10-06, so #374 appears landed on this branch's base; this ticket still does not edit that row.
- Source records named by the ticket but **not present on this host**: private research checkout paths `.claude/state/checkpoint-archive-S415.md` and `docs/research/evaluation-chain-batch-2-S414.md`, plus the S523 audit notes. Those files do not exist here; nothing in this PR body quotes them as read.
- Scratch evidence body: `.scratch/issue-378/pr-body.md` (this file). The runner reads it off the branch and removes it before push; it is not part of the final diff and must not be cited as a changed file.
- Changeset: none.
- Mutation receipt: none (no code change).
