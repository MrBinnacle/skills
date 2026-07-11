---
name: subagent-research-reliability
description: Reliability checks for web-research subagents. Pre-dispatch, verify the agent's tool grant actually includes web tools (else it no-ops or fabricates). Post-return, verify every citation before acting.
---

# Subagent Research Reliability

## Problem

Dispatching subagents for web research has two silent failure modes that both produce
confident-looking but worthless output:

1. **The agent can't actually search.** Its `tools:` grant lacks WebSearch/WebFetch even though
   its description says "performs web research." It returns a no-op or fabricates citations from
   training data.
2. **The agent searches but hallucinates sources.** LLM research output contains
   plausible-but-fake citations, CVE IDs, arXiv IDs, dates, or fabricated cross-references
   (e.g., a real CVE attributed to a paper that never cites it).

Both are invisible if you trust the returned text. Both were hit and caught in one session
(2026-05-28 — see [EVIDENCE.md](EVIDENCE.md)).

## Context / Trigger Conditions

- About to call the Agent tool with a custom `subagent_type` for web research / literature /
  threat-intel / market scan.
- The agent's description claims a web capability.
- Curating findings (citations, CVE/arXiv IDs, advisory URLs, dates) returned by a research
  subagent before acting on them.

## Solution

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

### Check 2 — Post-return: verify citations with a dedicated pass

Never treat research-subagent citations as confirmed. After research returns, dispatch a
SEPARATE verification subagent (general-purpose) whose ONLY job is to WebFetch each source URL
and report, per URL: `VERIFIED` (resolves + content matches) / `PARTIAL` (resolves but a detail
differs) / `UNRESOLVED` (404) / `UNCONFIRMABLE`. Tell it explicitly: verify source existence +
content match, do NOT assess the threat/quality.

- It catches dead URLs, fabricated CVE/arXiv IDs, and **fabricated cross-references** (a real ID
  bolted onto the wrong source).
- Observed catch: real Cursor CVEs (CVE-2025-54136/54135) attributed to an arXiv paper that
  doesn't cite them.
- Only findings that survive verification become actionable (eligible to become a tracked
  finding, a security-finding candidate, or a dependency action).

## Verification

- Pre-dispatch: the dispatched agent type's `tools:` includes the needed web tool, OR you used
  `general-purpose`.
- Post-return: every actioned citation carries a VERIFIED/PARTIAL verdict; UNRESOLVED or
  fabricated ones are dropped or annotated in place.

## Example

Threat-watch beat: 3 `general-purpose` subagents (NOT the web-toolless `research-scout` agent)
ran clusters in parallel → 9 findings. A 4th general-purpose subagent WebFetched all 9 source
URLs → 7 VERIFIED, 2 PARTIAL, and flagged one fabricated CVE-to-paper linkage. Only verified
findings were recorded as actionable; the fabrication was corrected in the log.

## Notes

- Claude Code discipline (custom agents, `subagent_type`, WebSearch/WebFetch tools, agent
  frontmatter).
- A verification subagent is cheap relative to the cost of acting on a hallucinated citation
  (e.g., filing a security finding against a fake CVE, or bumping a dependency for a CVE that
  doesn't exist).
- Background dispatch + notify-on-complete pairs well (don't block; curate on return) — but echo
  the verdict inline, never leave it only in a background temp file.
- A project's research-agent SKILL may define the finding schema, but the AGENT definition is
  where the tool-capability trap lives — they can drift apart. See also
  `superpowers:subagent-driven-development` (spec/review loops) for the broader dispatch
  discipline family.
