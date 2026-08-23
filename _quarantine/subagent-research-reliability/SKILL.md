---
name: subagent-research-reliability
description: Reliability checks for research subagents. Pre-dispatch, name the return channel (a subagent's plain text is a dead letter — the main session never sees it) and verify the agent's tool grant includes the tools the task needs (else it no-ops or fabricates). Post-return, verify every claim before acting, citations and checked negatives alike.
---

# Subagent Research Reliability

## Problem

Dispatching subagents for research has three silent failure modes. Each produces a confident
result that is worth nothing, and they fail in dispatch order:

1. **The findings are a dead letter.** The agent researches correctly and answers in plain text.
   **Plain text a subagent prints is not visible to the main session.** The work exists in a
   transcript nobody reads. What arrives instead is an idle notification carrying no content,
   which reads like completion.
2. **The agent can't actually search.** Its `tools:` grant lacks WebSearch/WebFetch even though
   its description says "performs web research." It returns a no-op or fabricates citations from
   training data.
3. **The agent returns claims that do not hold.** Fabricated citations, CVE IDs, arXiv IDs and
   cross-references are the web case. The general case is wider: a misquoted rule, a line number
   dressed as a section, and — the dangerous one — **a checked negative that is false**, where the
   agent reports "zero hits across all five files" and one of the five hits.

All three are invisible if you trust the returned text. Modes 2 and 3 were hit and caught in one
session (2026-05-28 — see [EVIDENCE.md](EVIDENCE.md)); modes 1 and 3 in another (2026-08-18).

## Context / Trigger Conditions

- About to call the Agent tool for research of any kind — web, literature, threat-intel, market
  scan, or a read-only sweep of the local repository.
- The agent's description claims a capability its frontmatter may not grant.
- An idle notification arrives from a dispatched agent and carries no findings.
- Curating anything a research subagent returned — citations, IDs, dates, quoted rules, or a
  reported negative — before acting on it.

## Solution

### Check 0 — Pre-dispatch: name the return channel in the dispatch itself

**State how findings come back, in the prompt, every time.** A subagent that is not told will
answer in plain text, and plain text is a dead letter: the main session never receives it. The only
signal that arrives is an idle notification, which is indistinguishable from a finished report.

Give two routes, so one failing is survivable:

1. **`SendMessage` to `main`**, with the findings in the message body — the primary channel.
2. **A file at one absolute path you supply**, which you can read directly.

Route 2 needs a **bounded write escalation**, and bounding it is what keeps the read-only default
intact. Name the exact path, and state what stays read-only:

> BOUNDED WRITE ESCALATION, this segment only: write exactly ONE file, at `<absolute path>` and
> nowhere else. The repository stays read-only — create nothing under `<repo>`, and post nothing to
> the tracker.

**An idle notification means the agent stopped. It does not mean the agent reported.** Treat the
two as different events, and never characterise findings from a notification alone.

### Check 1 — Pre-dispatch: verify the agent's tool grant matches the task

Before dispatching `subagent_type=X` for web research, confirm X actually has the web tools:

- Read `.claude/agents/X.md` (or `~/.claude/agents/X.md`) frontmatter `tools:`. If it lists only
  `Read, Bash, Grep` (no `WebSearch`/`WebFetch`), the agent **cannot web-search** regardless of
  its description.
- Observed: a `research-scout` agent described as "Performs web research ... with citations" had
  `tools: Read, Bash, Grep`. Dispatching it for a live web beat would no-op or fabricate.
- **Fix:** dispatch `general-purpose` (tools `*`, includes WebSearch/WebFetch) with the research
  protocol embedded in the prompt; OR add WebSearch/WebFetch to the agent's `tools:`.
  **The description is not the capability — the frontmatter is.**

### Check 2 — Post-return: verify every load-bearing claim, not just the citations

Treat a subagent's return as a set of leads. **Verify each claim you intend to act on**, against the
source it names, before it reaches an artifact.

**For web sources**, dispatch a SEPARATE verification subagent (general-purpose) whose ONLY job is to
WebFetch each source URL and report, per URL: `VERIFIED` (resolves + content matches) / `PARTIAL`
(resolves but a detail differs) / `UNRESOLVED` (404) / `UNCONFIRMABLE`. Tell it explicitly: verify
source existence + content match, do NOT assess the threat/quality.

- It catches dead URLs, fabricated CVE/arXiv IDs, and **fabricated cross-references** (a real ID
  bolted onto the wrong source).
- Observed catch: real Cursor CVEs (CVE-2025-54136/54135) attributed to an arXiv paper that
  doesn't cite them.

**For local-repository research**, re-run the command yourself. It is one call and it is the whole
check. Three classes fail here and each has its own re-run:

| Claim | Re-run |
| --- | --- |
| **A checked negative** — "zero hits across these five files" | The grep, over the same set. **Verify negatives first**: a false negative is the one error that looks like a clean result, and it is the reason the sweep was commissioned. |
| **A quoted rule or constraint** | `grep` the naming file for the quoted phrase. Observed catch: an agent quoted a standing rule as *"unless it blocks a gate"* where the file reads *"unless it blocks a rule"* — inside a draft comment about to be posted. |
| **A locator** | Open it. A line number written where a section heading belongs sends a reader to a section that does not exist. |

Only claims that survive become actionable.

## Verification

- Pre-dispatch: the prompt names both return routes, and the write escalation names one absolute
  path. Re-read the prompt for the words `SendMessage` and the path before sending it.
- Pre-dispatch: the dispatched agent type's `tools:` includes the needed web tool, OR you used
  `general-purpose`.
- Post-return: every actioned claim was re-derived from its own source — a fetched URL, a re-run
  grep, an opened locator. Every reported negative was re-run. Claims that failed are corrected in
  place, with what the source actually says.

## Example

Threat-watch beat: 3 `general-purpose` subagents (NOT the web-toolless `research-scout` agent)
ran clusters in parallel → 9 findings. A 4th general-purpose subagent WebFetched all 9 source
URLs → 7 VERIFIED, 2 PARTIAL, and flagged one fabricated CVE-to-paper linkage. Only verified
findings were recorded as actionable; the fabrication was corrected in the log.

**Dead letter, 2026-08-18.** Three `Explore` scouts were dispatched over one repository with no
return channel named. All three researched correctly. Four idle notifications arrived carrying no
content; a state file was committed saying the scouts "have not reported" and telling the next
session to re-dispatch. Re-instructing them with `SendMessage` plus one authorised scratchpad path
recovered every finding — including one that **contradicted an accepted ADR in an already-approved
plan**. The research was never the problem. The channel was, and it cost a wrong commit.

## Notes

- Claude Code discipline (custom agents, `subagent_type`, WebSearch/WebFetch tools, agent
  frontmatter).
- A verification subagent is cheap relative to the cost of acting on a hallucinated citation
  (e.g., filing a security finding against a fake CVE, or bumping a dependency for a CVE that
  doesn't exist).
- Background dispatch pairs well with this (curate on return rather than blocking) — provided
  Check 0 gave the return a channel. Echo the verdict inline; a background temp file is the
  redundant route, never the only one.
- **A verified return is worth more than an unverified one, not less.** Check 2 caught three false
  claims in one repo-only return whose substantive disposition was correct. Verification is what
  makes a scout's work usable; treating it as distrust is how the step gets skipped.
- A project's research-agent SKILL may define the finding schema, but the AGENT definition is
  where the tool-capability trap lives — they can drift apart. See also
  `superpowers:subagent-driven-development` (spec/review loops) for the broader dispatch
  discipline family.
