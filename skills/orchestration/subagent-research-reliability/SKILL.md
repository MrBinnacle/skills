---
name: subagent-research-reliability
description: Pre-dispatch, name the return channel — a subagent handback can be empty. Verify tool grants match the task. Post-return, verify every claim, negatives first.
---

# Subagent Research Reliability

Run three checks around a research subagent: name its return channel before dispatch, confirm its tool grant matches the task, and re-derive every claim you will act on after it returns. You get a finding set you can use, with each failed claim corrected in place against what the source says.

Two recorded catches in one session, 2026-05-28. A `research-scout` agent described as "performs web research with citations" held `tools: Read, Bash, Grep` — no web tools, so it could only no-op or answer from training data. And a returned finding attached real Cursor CVE IDs (CVE-2025-54136, CVE-2025-54135) to an arXiv paper that does not cite them: a fabricated cross-reference built on real identifiers. An ad hoc pass found both, and that pass is what Check 2 now prescribes. So these are the failures that motivated the checks, not failures the checks caught. Sources: [`EVIDENCE.md`](EVIDENCE.md), [`gotchas.md`](gotchas.md).

## Use when

You are about to dispatch a research subagent, or to act on what one returned — a citation, an ID, a quoted rule, a locator, a reported negative. Also when an agent's description claims a capability its frontmatter may not grant, or a completion notification arrives with no findings.

## Check 0 — Name the return channel in the dispatch

You get one final text result: inline for a foreground agent, a completion notification for a background one. Intermediate tool output never reaches you. That path alone has failed — observed 2026-08-04 and 2026-08-24, agents completed with an empty handback and the work survived only in a transcript you cannot read.

Name two routes, so one failing is survivable:

1. `SendMessage` to `main`, findings in the message body. Primary.
2. One file at one absolute path you supply.

Route 2 needs a bounded escalation. Bounding it keeps the read-only default intact:

> BOUNDED WRITE ESCALATION, this segment only: write exactly ONE file, at `<absolute path>` and nowhere else. The repository stays read-only — create nothing under `<repo>`, and post nothing to the tracker.

**A completion notification means the agent stopped. It does not mean the agent reported.** Never describe findings from a notification alone.

**Size the contract here, not on recovery.** If the return runs past roughly a dozen structured records, or past one independent section, name the batching in this prompt, and license a partial return in so many words:

> Send what you have and name the sections you did not reach and why. A partial report that names its own gaps is useful. Silence is not.

**Do not nudge a third time.** Two failed deliveries means re-run the work yourself or re-dispatch with a batched contract. Read [`large-returns.md`](large-returns.md) before nudging a second time.

## Check 1 — Verify the tool grant before dispatching

Read `.claude/agents/X.md`, or `~/.claude/agents/X.md`, and look at the frontmatter `tools:` list. If it does not include `WebSearch` or `WebFetch`, that agent cannot search the web, whatever its description says.

Fix it two ways: dispatch `general-purpose`, which holds `*`, with the protocol in the prompt; or add the web tools to that agent's `tools:`.

**The description is not the capability. The frontmatter is.**

## Check 2 — Re-derive every claim you will act on

Treat the return as leads. Verify each claim against the source it names before it reaches an artifact.

**For web sources**, dispatch a separate `general-purpose` agent whose only job is to fetch each URL and return one verdict per URL: `VERIFIED` (resolves, content matches), `PARTIAL` (resolves, a detail differs), `UNRESOLVED` (404), `UNCONFIRMABLE`. Tell it to check that the source exists and matches, not to assess quality. This catches dead URLs, invented CVE and arXiv IDs, and real IDs bolted onto the wrong source.

**For local-repository research**, re-run the command yourself. It is one call and it is the whole check. [`EXAMPLES.md`](EXAMPLES.md) walks a full pass of both halves.

| Claim | Re-run |
| --- | --- |
| A checked negative — "zero hits across these five files" | The grep, over the same set. **Do negatives first.** A false negative is the one error that looks like a clean result, and it is why you commissioned the sweep. |
| A quoted rule | `grep` the naming file for the phrase. Observed: an agent quoted a rule as *"unless it blocks a gate"* where the file reads *"unless it blocks a rule"*, inside a comment about to be posted. |
| A locator | Open it. A line number written where a section heading belongs sends a reader to a section that does not exist. |

## Verification

Before dispatch: the prompt names both routes and one absolute path, and the agent's `tools:` covers the task. After return: every claim you acted on was re-derived from its own source, every reported negative was re-run, and every failed claim was corrected in place with what the source says.
