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
  write escalation quoted in `Check 0`, each naming one absolute path. **All three created their
  file. Two delivered complete content** — 6 of 6 blocks (10,869 bytes) and 7 of 7 blocks (20,500
  bytes, including the `EVIDENCE-ROWS` field requested for three published cards). The third
  created its file at **0 bytes**.
- **The returns were substantive, not acknowledgements.** One block quotes a card's origin
  paragraph verbatim, names the section it sits under, and lists the distinctive literals asked
  for. The agents had done the work throughout; none of it could reach the session through plain
  text.

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

**One thing this also corrects about route 1.** The completion signal that resolved this arrived
*as* a `SendMessage` carrying a content-bearing summary — the first message from any of these
agents to carry content rather than an idle notification. Route 1 is therefore not inert. What it
failed to carry, across three attempts, was the *findings*; it succeeded at carrying a *pointer to
where the findings were written*. That is the division of labour the routes should have.

**Finding: the two routes are not redundant and not interchangeable — they carry different things.**
`Check 0` presents them as redundancy, "so one failing is survivable". On this evidence that is the
wrong model. Route 1 carried no findings across three attempts and nine idle notifications; route 2
carried every finding that arrived. Route 1 then carried the one thing route 2 structurally cannot:
the signal that the write had finished.

**So: the file path carries the payload, and the message carries completion.** A future edit to
`Check 0` should say that, and should add the completion contract the gap above describes. Neither
edit is made here — this is the candidate's evidence record, and changing the check is a change to
its procedure that belongs in its own reviewable diff.

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
