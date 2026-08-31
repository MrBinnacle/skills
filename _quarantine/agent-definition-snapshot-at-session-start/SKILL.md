---
name: agent-definition-snapshot-at-session-start
description: |
  A subagent reports a tool as unavailable and the harness says it is "disabled for this session,
  in subagents as well as here" — but the main session is using that tool fine. Use when:
  (1) you edited a file in `.claude/agents/` and dispatched that agent in the SAME session to
  confirm the fix; (2) a subagent returns "No such tool available: X" for a tool listed in its own
  `tools:` frontmatter; (3) a newly written agent file returns "Agent type '<name>' not found";
  (4) you are about to escalate a subagent capability gap as a harness limitation or a settings
  problem. The agent registry — file list AND file contents — is resolved once at session start,
  so a correct repair reports as a failure and the failure names the tool rather than the
  staleness. Prevents a stale snapshot being escalated as a missing capability.
author: Claude Code
version: 1.0.0
date: 2026-08-26
---

# An agent definition is snapshotted at session start

## Problem

The natural loop for repairing a subagent is: read its definition, fix the frontmatter, dispatch
the agent, confirm the fix. **That loop cannot work.** The Agent tool resolves `.claude/agents/*.md`
once, at session start. Every edit after that point is inert for the rest of the session.

So the confirming dispatch runs against the pre-repair snapshot, and **a correct repair reports as
a failure.** Worse, the failure report names the *tool*, not the staleness — which sends the next
hour hunting a capability that is not missing.

## Context / Trigger Conditions

Any one of these:

- A subagent returns **`Error: No such tool available: X. X is disabled for this session, in
  subagents as well as here.`** while the main session has successfully used `X` in the same
  session. The second half of that sentence is the generic absent-tool string and is **not a
  statement about your configuration**.
- A subagent reports a tool as unavailable that **is listed in its own `tools:` frontmatter**.
- A newly created agent file returns **`Agent type '<name>' not found`** with the file plainly on
  disk.
- You edited anything under `.claude/agents/` earlier in this session.
- You are about to write "the harness does not support X in subagents", "no edit to any file in
  this repository can change that", or "this needs a settings change" — about a subagent capability.

## Solution

### 1. Check the commit time against the session start, before believing the report

    git log -S'<the tool name>' --format='%h %ad %s' --date=iso -- .claude/agents/<agent>.md

If the grant landed **during this session**, the dispatch that failed ran against a snapshot taken
before it. That is the whole explanation. Nothing else needs investigating.

### 2. Read the agent listing, not the file

**The cheapest correct check is free and almost nobody uses it.** The session's own available-agents
listing renders each agent's *resolved* tools:

    design-make: Design MAKE seat ... (Tools: Read, Grep, Glob, Bash, Edit, Write, Skill)

**The file states intent. The listing states the runtime.** When the question is what a subagent can
actually call, the listing is the authority and the file is a proposal. If the two disagree, the
file was edited after the session began.

### 3. Confirm the repair in a NEW session

There is no in-session workaround. Start a fresh session and dispatch then. Note that a plugin or
skill reload is not sufficient evidence on its own — see Verification.

### 4. Do not adopt a workaround for a defect that has not been established

The expensive failure here is not the lost hour. It is **paying an architectural cost to route
around a capability that was never missing** — proxying content into the parent's context, merging
two agents into one, or deleting a role from a pipeline. Establish the snapshot explanation first.

## Verification

Isolate the mechanism in two steps. Both were run on 2026-08-26 and both are cheap:

| Step | Action | Result that confirms the snapshot |
| --- | --- | --- |
| **File list** | Write a new throwaway agent file mid-session, dispatch it | `Agent type '<name>' not found` |
| **File contents** | Narrow an *existing* agent's `tools:` mid-session (remove one tool), dispatch it, ask it to enumerate its own callable schema | The removed tool is **still present** |

Step 2 is the one that matters and the one usually skipped. Step 1 alone leaves open that contents
are re-read per dispatch while only the file list is cached — they are not.

**A PASS from a new session does not identify the mechanism by itself.** If you also reloaded
plugins, restarted the harness, or changed settings between the two dispatches, you changed more
than one variable and cannot attribute the fix. Run the two-step isolation above instead.

## Example

**Observed 2026-08-26.** A four-stage agent pipeline had a stage whose entire remit was firing a
named skill. Its `tools:` grant omitted `Skill`, so the grant was added and the stage re-dispatched
in the same session. It returned:

    Error: No such tool available: Skill. Skill is disabled for this session, in subagents as well as here.

The parent session had called `Skill` four times in that same session, including one call that
returned a full skill body. The claim was recorded as a defect stating that the tool was
unavailable to subagents, that *"the refusal is above the file"*, and that *"no edit to any file in
this repository can change that"* — and it was escalated as a decision between enabling the tool,
adopting a costly workaround, or **deleting the stage from the pipeline**.

All of it was false. `git log -S` put the grant at `11:48` inside a session that closed at `16:33`.
A fresh session dispatched the same agent and `Skill` returned the skill body. The two-step
isolation then confirmed both the file list and the file contents are fixed at session start.

The cost of not checking: one defect became two, a workaround was adopted whose stated cost was
paid for nothing, and an architectural decision to remove a working component reached the owner's
desk.

## Notes

- **The error message overstates its own scope.** "in subagents as well as here" is emitted whether
  or not the tool is available in the parent. Reading it literally sends you to look for a
  session-level flag that does not exist.
- **A tool grant in `tools:` frontmatter is necessary and not sufficient.** It must also be in the
  snapshot the running session resolved.
- Generalises past `Skill` to **every** field of an agent definition — model, description, prompt
  body, and any tool.
- The inverse also holds and is the more dangerous direction: **narrowing** a grant mid-session
  does not take effect either, so a subagent can still hold a tool you believe you revoked. Do not
  rely on a mid-session edit as a security or blast-radius control.
- See also: `subagent-research-reliability` for the neighbouring failure — the description claiming
  a capability the frontmatter never granted, which is a *real* grant defect and is repaired the
  same way, in a new session.
