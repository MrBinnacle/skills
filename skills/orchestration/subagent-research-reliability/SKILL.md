---
name: subagent-research-reliability
description: Pre-dispatch, name the return channel — a subagent's plain text is a dead letter. Verify tool grants match the task. Post-return, verify every claim, negatives first.
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

#### Variant — the nudge fails, and the size of the report is why

Recovery from a dead letter is normally one `SendMessage` restating the output contract, and that
had held every prior time. **On 2026-08-26 it stopped working, and the exception has a shape.**

Two agents in one session finished their work and never delivered, one of them **twice, including
after a full contract-restating nudge.** Two other agents in the same session delivered first time.
The variable was not the agent type, the model, or the prompt quality:

| agent | output contract | delivered |
| --- | --- | --- |
| single verbatim result + short field list | small | first try |
| five labelled harvests | medium | first try |
| **three full inventories, one row per closed child across three boards** | **large** | **never** |
| **seventeen structured records** | **large** | **only when batched** |

**Ask for the report in explicit batches when the deliverable is large.** Naming the split in the
nudge recovered seventeen records that a single-message nudge had already failed to extract:

> Send them in THREE separate messages, not one. Message 1: items 1-6. Message 2: items 7-12.
> Message 3: items 13-17.

Two further rules that make the failure cheap:

- **Size the contract at dispatch.** If the return is more than roughly a dozen structured records
  or several independent sections, specify the batching in the original prompt rather than
  discovering the ceiling on recovery.
- **Always license a partial return, explicitly:** *"send what you have and name the sections you
  did not reach and why. A partial report that names its own gaps is useful. Silence is not."*
  Without that line an agent holding a large incomplete result has no sanctioned way to deliver it.

⛔ **Do not nudge a third time.** Two failed deliveries is the signal to re-run the work yourself or
re-dispatch with a batched contract. In the observed case the caller re-ran the sweep directly and
the result was better than the agent's method would have produced, because a scripted check
replaced hand-matching.

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

See [EXAMPLES.md](EXAMPLES.md) for worked examples including the dead-letter incident and the
threat-watch verification pass.
