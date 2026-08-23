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

Session `workspace_lint` S026, 2026-08-18/19.

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

## Review notes for promotion

- The skill body is Claude Code-specific (`SendMessage`, idle notifications, the Agent tool). Check
  that against the canonical repo's portability posture before committing — the orchestration
  folder may hold platform-neutral skills.
- The bounded-escalation wording is quoted as a block for copy-paste. Confirm it matches the
  project's own escalation convention if one exists.
- No `version:` or `date:` frontmatter was added, because the committed file carries neither and
  dates its evidence inline instead. Matching house style was the deliberate choice.
