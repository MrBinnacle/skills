# Provenance — this is a PATCH to an already-promoted skill, not a new skill

**Staged 2026-08-19. Not active. Nothing is live from this directory.**

## What this is

`subagent-research-reliability` is **already promoted**. It lives in the canonical skills repo at
`C:\Users\mlpgr\2026_Projects\skills\skills\orchestration\subagent-research-reliability\` and is
symlinked into the active set at `~/.claude/skills/subagent-research-reliability`.

The `SKILL.md` beside this file is that skill **with a patch applied**. It is staged here rather
than left live because the standing rule is quarantine-first and manual review before anything
reaches the active set.

**The patch was originally written straight through the symlink into the canonical repo.** That
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
2. **`Check 2` widened from citations to any claim the work rests on.** The committed version is scoped
   to web sources and URLs. The general case is wider and has its own table: **checked negatives
   first** (a false negative is the one error that looks like a clean result), quoted rules, and
   locators, each with the re-run that tests it.
3. **The `Problem` section goes from two failure modes to three**, in dispatch order, and the
   description gains the dead-letter branch. A second worked example is added under `Example`.

## The evidence behind it

### Occurrence 1 — origin. Session S026 of a private linter project, 2026-08-18/19

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
  recovered nothing. On this evidence route 2 — the file at a named path — is the one that carries delivery,
  half, and route 1 is not a substitute for it.

### Route 2 tested directly, same session, 2026-08-24

The paragraph above originally recorded route 2's standalone sufficiency as untested. It was then
tested against the same four agents, and the result is recorded here rather than folded into the
claim above, so the order of evidence stays visible.

- **Route 1, three attempts, zero recoveries.** The dispatch itself, a `SendMessage` restating the
  output contract verbatim, and a third wake. Each produced an idle notification carrying no
  content. Nine idle notifications in total across the four agents.
- **Naming a payload channel, one attempt: 3 of 3 recovered.** Three of the four agents were
  re-instructed with the bounded write escalation quoted in `Check 0`, each naming one absolute
  path. All three returned complete content.

| agent | route 2 (named file) | route 1 (message) | outcome |
|---|---|---|---|
| A | 6 of 6 blocks, 10,869 bytes | — | complete via route 2 |
| B | 7 of 7 blocks, 20,500 bytes | completion summary | complete via route 2, signalled via route 1 |
| C | **blocked by the host's own guard**, 0 bytes | 6 of 6 blocks, full content | complete via route 1 fallback |
| D | *never given a channel* | — | **never delivered** |

- **Agent D is a natural control.** It was the only one never given a payload channel, and it is
  the only one that never delivered anything. The variable that separates delivery from silence is
  whether a channel was named, not which channel.
- **The returns were substantive, not acknowledgements.** One block quotes a card's origin
  paragraph verbatim, names the section it sits under, and lists the distinctive literals asked
  for. The agents had done the work throughout; none of it could reach the session until a channel
  existed to carry it.

### A gap in route 2, found by falling into it

**This section originally reported one return as incomplete — "five blocks where seven were asked
for". That was wrong, and how it went wrong is the finding.**

The file was read while the agent was still writing it. At that moment it held 5 blocks and 14,175
bytes. It finished at 7 blocks and 20,500 bytes. A partial write was measured and recorded as an
incomplete delivery.

**`Check 0` tells the dispatcher to name one file path. It does not say how the reader knows the
write has finished.** File existence is not completion, and a file-based channel has no
end-of-message marker the way a message does. The failure is quiet in the dangerous direction: a
partially-written file reads as a complete short answer, and nothing distinguishes the two.

The empty third file is the same gap at its limit — 0 bytes is indistinguishable from "created
and abandoned" without a completion signal.

**Route 2 needs a completion contract, not just a path.** Require the agent to signal completion
when the write is done (a `SendMessage` naming the finished file, a sentinel final line, or an
atomic rename from a temporary name), and treat an unsignalled file as still in flight. Until
`Check 0` says so, a reader who samples early will report a truncated return as a short one.

### The second failure mode of route 2: the host's own tooling policy

Agent C's file stayed at 0 bytes because **this host's `PreToolUse` Bash guard blocked the write**.
The agent attempted to author prose into the named `.md` file through a Bash heredoc, which the
guard refuses on this machine — correctly, because heredoc prose authoring is known to fail here.

The agent then **fell back to route 1 and returned all six blocks in the message body.**

So route 2 has a failure mode that has nothing to do with the agent and nothing to do with the
research: **the environment's own tooling policy can forbid the write.** A dispatch that names a
file path should also name the tool to write it with, or the agent will reach for whichever
mechanism the host happens to block.

### What the three occurrences together actually establish

This section's finding moved three times as evidence arrived, and the movement is recorded rather
than smoothed over.

1. First reading: *route 2 is sufficient, route 1 is not.* Drawn from route 1 failing three times
   and route 2 succeeding once.
2. Second reading: *the routes are not redundancy; the file carries payload and the message
   carries completion.* Drawn from a completion summary arriving by message.
3. **Current reading, and the one the full evidence supports: `Check 0`'s redundancy framing is
   correct, and the reason it is correct is sharper than the check states.** The two routes fail
   for **unrelated** causes — route 2 on host tooling policy, route 1 on the agent not treating it
   as the payload channel — so one failing genuinely is survivable. Agent C is the proof: route 2
   was blocked outright and the findings still arrived.

**The instruction that mattered is to name a payload channel at all.** With none named, 0 of 4
agents delivered across three rounds and nine empty idle notifications. With one named, 3 of 3
delivered. Which channel mattered less than that a channel existed.

**Finding: `Check 0`'s core instruction is confirmed, and two additions would strengthen it.**

Confirmed as written: name a return channel in the dispatch, and give two routes so one failing is
survivable. Both halves are kept here — naming any channel took delivery from 0 of 4 to
3 of 3, and the redundancy rescued the one agent whose primary route was blocked.

Two things the check does not yet say, both learned here:

1. **A completion contract.** `Check 0` names a path but never says how the reader knows the write
   finished. File existence is not completion, and a partial write reads as a complete short
   answer. Require a signal on completion, and treat an unsignalled file as still in flight.
2. **Name the writing tool, not just the path.** The host's own guard can forbid the mechanism the
   agent reaches for. Agent C lost route 2 entirely to a `PreToolUse` rule.

Neither edit is made here. This is the candidate's evidence record; changing the check is a change
to its procedure and belongs in its own reviewable diff.

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
