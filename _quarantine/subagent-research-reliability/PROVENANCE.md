# Provenance — this is a PATCH to an already-promoted skill, not a new skill

**Staged 2026-08-19. Not active. Nothing is live from this directory.**

## What this is

`subagent-research-reliability` is **already promoted**. It lives in the canonical skills repo at
`C:\Users\mlpgr\2026_Projects\skills\skills\orchestration\subagent-research-reliability\` and is
symlinked into the active set at `~/.claude/skills/subagent-research-reliability`.

The `SKILL.md` beside this file is that skill **with a patch applied**. It is staged here rather
than left live because the standing rule is quarantine-first and manual review before anything
reaches the active set.

⚠ **The patch was originally written straight through the symlink into the canonical repo.** That
was a direct edit to a live, version-controlled, promoted skill and it skipped the review gate. The
canonical file has been **reverted to its committed state**, so the active skill is unchanged and
this directory holds the only copy of the patch.

## To resurrect it

The canonical path is the target — copying into `~/.claude/skills/<name>/` would create a real
directory shadowing the symlink and give you two divergent copies.

```sh
cp ~/.claude/skills/_quarantine/subagent-research-reliability/SKILL.md \
   /c/Users/mlpgr/2026_Projects/skills/skills/orchestration/subagent-research-reliability/SKILL.md
cd /c/Users/mlpgr/2026_Projects/skills && git diff   # review, then commit
```

Verify it took: `grep -c "dead letter" ~/.claude/skills/subagent-research-reliability/SKILL.md`
returns `3` through the symlink.

## What the patch changes

Three edits, +78 / −26 against the committed version.

1. **New `Check 0` — name the return channel in the dispatch.** Leading word: **dead letter**. A
   subagent's plain text is not visible to the main session, so findings that were correctly
   researched never arrive; what arrives is an idle notification carrying no content, which is
   indistinguishable from a finished report. The check specifies two routes — `SendMessage` to
   `main`, plus one absolute path under a bounded write escalation that keeps the repo read-only —
   and includes the escalation wording verbatim.
2. **`Check 2` widened from citations to any load-bearing claim.** The committed version is scoped
   to web sources and URLs. The general case is wider and has its own table: **checked negatives
   first** (a false negative is the one error that looks like a clean result), quoted rules, and
   locators, each with the re-run that tests it.
3. **The `Problem` section goes from two failure modes to three**, in dispatch order, and the
   description gains the dead-letter branch. A second worked example is added under `Example`.

## The evidence behind it

### Occurrence 1 — origin. Session `workspace_lint` S026, 2026-08-18/19

- Three `Explore` scouts were dispatched over one repository with **no return channel named**. All
  three researched correctly. **Four idle notifications arrived carrying no content.** A state file
  was committed asserting the scouts "have not reported" and instructing the next session to
  re-dispatch — asserting *has nothing to report* from evidence for *has not reported*.
- Re-instructing with `SendMessage` plus one authorised scratchpad path recovered every finding,
  including one that **caught an approved implementation plan contradicting an accepted ADR**. The
  research was never the problem; the channel was, and it cost a wrong commit.
- Post-return verification then caught **three false supporting claims** in a return whose
  substantive disposition was correct: a "checked negative" reporting zero hits across five files
  when one of the five hit; a standing rule quoted as *"unless it blocks a gate"* where the file
  reads *"unless it blocks a rule"*, inside a draft comment about to be posted; and line numbers
  supplied where the citation standard requires section headings.

### Occurrence 2 — independent recurrence, 2026-08-24, a different repository

Found by the rotation and harvest pass over this collection, in the pass's own session.

- Four `reader` subagents were dispatched to extract origin text from 25 skill cards. The dispatch
  **named no return channel**; each prompt ended `Your final message IS the data`. That is plain
  text, which is the dead letter.
- **Four idle notifications arrived carrying no content.** No extract reached the main session.
- **`SendMessage` re-instruction alone did not recover the findings.** All four agents were sent a
  message restating the output contract verbatim. Each woke, and each emitted a second idle
  notification carrying no content. The extraction was abandoned and redone in-session by a
  mechanical script over the same 25 cards.
- **This narrows Check 0's two routes: they are not interchangeable.** Occurrence 1 recovered with
  `SendMessage` **plus** one authorised absolute path. Occurrence 2 used `SendMessage` alone and
  recovered nothing. On this evidence route 2 — the file at a named path — is the load-bearing
  half, and route 1 is not a substitute for it.

### Route 2 tested directly, same session, 2026-08-24

The paragraph above originally recorded route 2's standalone sufficiency as untested. It was then
tested against the same four agents, and the result is recorded here rather than folded into the
claim above, so the order of evidence stays visible.

- **Route 1, three attempts, zero recoveries.** The dispatch itself, a `SendMessage` restating the
  output contract verbatim, and a third wake. Each produced an idle notification carrying no
  content. Nine idle notifications in total across the four agents.
- **Route 2, one attempt, immediate recovery.** Three agents were re-instructed with the bounded
  write escalation quoted in `Check 0`, each naming one absolute path. **Two of three wrote their
  file within the same wake**, 10,869 and 14,175 bytes, containing the requested verbatim card
  extracts in the requested block format. The third had not written at the time of recording.
- **The returns were substantive, not acknowledgements.** One block quotes a card's origin
  paragraph verbatim, names the section it sits under, and lists the distinctive literals asked
  for. The agents had done the work throughout; none of it could reach the session through plain
  text.
- **One partial return, recorded rather than rounded up.** The seven-block file contained five
  blocks. Route 2 delivered, and delivered incompletely, in the same run.

**Finding: route 2 is sufficient on its own and route 1 is not.** `Check 0` presents the two routes
as redundancy — "so one failing is survivable". That framing understates the asymmetry. Route 1
failed three times against the identical task, agents and session in which route 2 succeeded on the
first attempt. **State the file path in the dispatch. Treat `SendMessage` as a supplement to it,
never as the channel.** A future edit to `Check 0` should reorder the two routes accordingly.

**The two occurrences are independent.** Different repository, different agent type (`Explore`
against `reader`), different task (repository research against text extraction), six days apart.
The four agents within occurrence 2 are one dispatch and count as one occasion, not four.

**The discipline that would have caught occurrence 2 was staged in this directory and not live.**
`grep -c "dead letter"` returns `0` against the promoted card and `3` against the `SKILL.md` beside
this file. The operator had the published skill installed and active throughout; it carries no
`Check 0`, because `Check 0` is this patch. The failure recurred in the gap the patch closes.

## Review notes for promotion

- **Admission criterion 2 (recurrence) is now answered for the `Check 0` branch: two independent
  occasions, 2026-08-18/19 and 2026-08-24, both dated above.** Criterion 2 was the standing blocker
  on every candidate in `_quarantine/`. It is the only criterion this pass measured; criteria 1, 3
  and 4 are untouched and unclaimed here. Promotion additionally requires an `EVIDENCE.md`, which
  this candidate does not carry, and the frontmatter normalization in `AGENTS.md` step 2a.
- The skill body is Claude Code-specific (`SendMessage`, idle notifications, the Agent tool). Check
  that against the canonical repo's portability posture before committing — the orchestration
  folder may hold platform-neutral skills.
- The bounded-escalation wording is quoted as a block for copy-paste. Confirm it matches the
  project's own escalation convention if one exists.
- No `version:` or `date:` frontmatter was added, because the committed file carries neither and
  dates its evidence inline instead. Matching house style was the deliberate choice.
