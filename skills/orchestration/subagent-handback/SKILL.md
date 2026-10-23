---
name: subagent-handback
description: Use when prompting, briefing or dispatching a research subagent, or when one goes idle with no report. Name a return channel, check its tool grant, verify every claim, negatives first.
---

# Subagent Research Reliability

## Problem

Dispatching subagents for research has three silent failure modes. Each produces a confident
result that is worth nothing, and they fail in dispatch order:

1. **The findings are a dead letter.** The agent finishes with nothing the caller can use.
2. **The agent can't actually search.** Its `tools:` grant lacks WebSearch/WebFetch even though
   its description says "performs web research." It returns a no-op or answers from memory.
3. **The agent returns claims that do not hold.** Fabricated citations and cross-references, a
   misquoted rule, a line number dressed as a section, and — the dangerous one — **a checked
   negative that is false**: "zero hits across all five files" when one of the five hits.

All three are invisible if you trust the returned text. [EVIDENCE.md](EVIDENCE.md) records the
catches.

## Context / Trigger Conditions

- About to call the Agent tool for research of any kind — web, literature, market scan, or a
  read-only sweep of the repository — or writing its brief, whoever sends it.
- A dispatched agent or teammate went idle, or its completion notification carries no findings.
- Curating anything a research subagent returned — citations, IDs, dates, quoted rules, or a
  reported negative — before acting on it.

## Solution

### Check 0 — Pre-dispatch: name the return channel in the dispatch itself

**What the platform promises.** A subagent's intermediate output stays in its own context; its
final text is the return, inline for a foreground agent and in the completion notification for a
background one. A named agent that launches as a teammate also delivers its final text: its idle
notification "includes its final answer" (code.claude.com `sub-agents.md`, `agent-teams.md`, read
2026-10-17). The `SendMessage` description's "plain text output is NOT visible to other agents"
covers text written mid-turn, not the final answer, so a named teammate's final text reaches the
spawner by design.

**What happens anyway.** Background agents have stopped with an empty handback (observed
2026-08-04, 2026-08-24, 2026-08-25), and work that lived only in their transcript was gone. Name a
payload channel the caller can read without trusting the handback, and give two routes so one
failing is survivable:

1. **`SendMessage` to `main`**, with the findings in the message body.
2. **A file at one absolute path you supply**, under a bounded write escalation:

> BOUNDED WRITE ESCALATION, this segment only: write exactly ONE file, at `<absolute path>` and
> nowhere else. The repository stays read-only — create nothing under `<repo>`, and post nothing to
> the tracker.

**A stop is not a report.** An idle or completion notification means the agent stopped; it may
carry nothing. Never characterise findings from a notification alone.

**A file is not final when you first read it.** A background agent may still be writing: one
verifier's file was 253 lines when first read and 494 later. Re-check its length before relying
on any summary of it.

#### When the nudge fails, size is why

One `SendMessage` restating the output contract usually recovers a dead letter. It failed on
2026-08-26 for the two agents with large contracts (three full inventories; seventeen records);
the two with small or medium contracts delivered first time. The seventeen records came back only
when the nudge named the split:

> Send them in THREE separate messages, not one. Message 1: items 1-6. Message 2: items 7-12.
> Message 3: items 13-17.

- **Size the contract at dispatch.** Above roughly a dozen structured records, or more than one
  independent section, specify the batching in the original prompt.
- **License a partial return:** *"send what you have and name the sections you did not reach and
  why. A partial report that names its own gaps is useful. Silence is not."*
- **Do not nudge a third time.** Two failed deliveries means re-run the work yourself or
  re-dispatch with a batched contract.

### Check 1 — Pre-dispatch: verify the agent's tool grant matches the task

- Read `.claude/agents/X.md` (or `~/.claude/agents/X.md`) frontmatter `tools:`. If it lacks
  `WebSearch`/`WebFetch`, the agent **cannot web-search** regardless of its description. Observed:
  a `research-scout` "performs web research ... with citations" had `tools: Read, Bash, Grep`.
- **A grant is necessary, not sufficient.** When tool search is enabled, deferred tools stay out
  of the agent's schema until `ToolSearch` loads them (`tools-reference.md`, read 2026-10-17); the
  web tools were deferred in the observed harness. Make the first step
  `ToolSearch select:WebSearch,WebFetch`, with a STOP if they are unavailable. A scout without them
  answers from memory and looks exactly like one that searched.
- **Fix:** dispatch `general-purpose` with the research protocol in the prompt, or add the web
  tools to `tools:`. **The description is not the capability — the frontmatter is.**

### Check 2 — Post-return: verify every claim you will act on

Treat a return as leads: verify each claim against its named source before it reaches an
artifact.

**For web sources**, dispatch a SEPARATE verification subagent whose only job is to WebFetch each
URL and report `VERIFIED` / `PARTIAL` / `UNRESOLVED` / `UNCONFIRMABLE` — source existence and
content match, not quality. It catches dead URLs, fabricated IDs, and **fabricated
cross-references** (observed: real Cursor CVEs attributed to an arXiv paper that does not cite them).

**For local-repository research**, re-derive the claim yourself:

| Claim | Check |
| --- | --- |
| **A checked negative** — "zero hits across these five files" | **Verify negatives first**, and **widen the search set**: re-running the agent's grep over the agent's set repeats its blind spot. Search the wider tree, other spellings, and the places the claim implies. Observed: a sweep of the project hooks folder missed two hooks in the user-level folder. |
| **A quoted rule** | `grep` the naming file for the phrase. Observed: *"unless it blocks a gate"* where the file reads *"unless it blocks a rule"*. |
| **A locator** | Open it. A line number written where a section belongs points at nothing. |

Only claims that survive become actionable.

Open [gotchas.md](gotchas.md) when a handback arrives empty or a verifier's verdict looks wrong.

## Verification

- Pre-dispatch: the prompt names both return routes, and the escalation names one absolute path.
- Pre-dispatch: the agent's `tools:` includes the needed web tool, and the prompt loads deferred
  tools first; or you used `general-purpose`.
- Post-return: every actioned claim was re-derived from its own source, and every reported
  negative was re-searched over a wider set. Failed claims are corrected in place.

## Example

[EXAMPLES.md](EXAMPLES.md) holds two dead-letter incidents and the threat-watch verification pass.
