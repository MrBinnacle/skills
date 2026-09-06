---
name: subagent-research-reliability
description: Pre-dispatch, name the return channel — a subagent handback can be empty. Verify tool grants match the task. Post-return, verify every claim, negatives first.
---

# Subagent Research Reliability

## Problem

Dispatching subagents for research has three silent failure modes. Each produces a confident
result that is worth nothing, and they fail in dispatch order:

1. **The findings are a dead letter.** The agent researches correctly, then finishes with nothing
   the caller can use. Platform docs (verified 2026-09-06, code.claude.com/docs/en/tools-reference.md,
   sub-agents.md): intermediate tool output stays in the subagent context; only the final text
   result returns — inline for foreground, as a completion notification for background. Observed
   2026-08-04 and 2026-08-24: background agents complete with an empty handback, and work that
   lived only in the subagent transcript is gone. Name an explicit payload channel every time.
2. **The agent can't actually search.** Its `tools:` grant lacks WebSearch/WebFetch even though
   its description says "performs web research." It no-ops or fabricates citations from training.
3. **The agent returns claims that do not hold.** Fabricated citations, CVE/arXiv IDs and
   cross-references are the web case. Wider: a misquoted rule, a line number dressed as a
   section, and — the dangerous one — **a checked negative that is false** ("zero hits across
   five files" when one of the five hits).

All three are invisible if you trust the returned text. Modes 2 and 3 were hit and caught in one
session (2026-05-28 — see [EVIDENCE.md](EVIDENCE.md)); modes 1 and 3 in another (2026-08-18).

## Context / Trigger Conditions

- About to call the Agent tool for research of any kind — web, literature, threat-intel, market
  scan, or a read-only sweep of the local repository.
- The agent's description claims a capability its frontmatter may not grant.
- A completion notification arrives from a dispatched agent and carries no findings.
- Curating anything a research subagent returned — citations, IDs, dates, quoted rules, or a
  reported negative — before acting on it.

## Solution

### Check 0 — Pre-dispatch: name the return channel in the dispatch itself

**State how findings come back, in the prompt, every time.** The platform delivers one final text
result. Intermediate tool output never reaches the parent. Relying on that path alone has failed
in the field. Name a payload channel the caller can read without trusting the handback.

Give two routes, so one failing is survivable:

1. **`SendMessage` to `main`**, with the findings in the message body — the primary channel.
2. **A file at one absolute path you supply**, which you can read directly.

Route 2 needs a **bounded write escalation**. Name the exact path, and state what stays read-only:

> BOUNDED WRITE ESCALATION, this segment only: write exactly ONE file, at `<absolute path>` and
> nowhere else. The repository stays read-only — create nothing under `<repo>`, and post nothing to
> the tracker.

**A completion notification means the agent stopped. It does not mean the agent reported.** An
empty notification is still a stop signal with no findings. (Older notes called the same stop an
"idle notification"; that is not the cross-session `notify_when_idle` feature.) Treat stop and
delivery as different events.

#### Variant — large deliverable, empty handback

When the return is large (more than roughly a dozen structured records, or more than one
independent section), size the batching in the original prompt, license a partial return
explicitly, and do not nudge a third time. Full shape, the 2026-08-26 table, and the recovery
nudge wording: [EXAMPLES.md](EXAMPLES.md) → "Large deliverable, 2026-08-26".

### Check 1 — Pre-dispatch: verify the agent's tool grant matches the task

Before dispatching `subagent_type=X` for web research, confirm X actually has the web tools:

- Read `.claude/agents/X.md` (or `~/.claude/agents/X.md`) frontmatter `tools:`. If it lists only
  `Read, Bash, Grep` (no `WebSearch`/`WebFetch`), the agent **cannot web-search** regardless of
  its description.
- Observed: a `research-scout` described as "Performs web research ... with citations" had
  `tools: Read, Bash, Grep`. Dispatching it for a live web beat would no-op or fabricate.
- **Fix:** dispatch `general-purpose` (tools `*`) with the research protocol in the prompt; OR
  add WebSearch/WebFetch to the agent's `tools:`. **The description is not the capability —
  the frontmatter is.**

### Check 2 — Post-return: verify every load-bearing claim, not just the citations

Treat a subagent's return as leads. **Verify each claim you intend to act on**, against the
source it names, before it reaches an artifact.

**For web sources**, dispatch a SEPARATE verification subagent (general-purpose) whose ONLY job
is to WebFetch each source URL and report, per URL: `VERIFIED` / `PARTIAL` / `UNRESOLVED` /
`UNCONFIRMABLE`. Tell it: verify source existence + content match, do NOT assess threat/quality.

- Catches dead URLs, fabricated CVE/arXiv IDs, and **fabricated cross-references** (a real ID
  bolted onto the wrong source).
- Observed: real Cursor CVEs (CVE-2025-54136/54135) attributed to an arXiv paper that doesn't
  cite them.

**For local-repository research**, re-run the command yourself:

| Claim | Re-run |
| --- | --- |
| **A checked negative** — "zero hits across these five files" | The grep, same set. **Verify negatives first**: a false negative looks like a clean result. |
| **A quoted rule or constraint** | `grep` the naming file for the quoted phrase. |
| **A locator** | Open it. A line number where a section heading belongs sends a reader nowhere. |

Only claims that survive become actionable.

## Verification

- Pre-dispatch: the prompt names both return routes, and the write escalation names one absolute
  path. Re-read the prompt for `SendMessage` and the path before sending.
- Pre-dispatch: the dispatched agent type's `tools:` includes the needed web tool, OR you used
  `general-purpose`.
- Post-return: every actioned claim was re-derived from its own source. Every reported negative
  was re-run. Failed claims are corrected in place with what the source actually says.

## Example

See [EXAMPLES.md](EXAMPLES.md) for worked examples including the dead-letter incident and the
threat-watch verification pass.
