---
name: downstream-instruction-framing
description: Framing discipline for artifacts instructing a downstream reader — handoffs, plans, ADRs, subagent prompts. Separates evidence access from decision rights; marks which decisions evidence can reopen.
---

# Downstream-Instruction Framing Discipline

Evidence and failure modes: [EVIDENCE.md](EVIDENCE.md), [gotchas.md](gotchas.md).

## Problem

LLMs default to authoritative downstream instructions: "Approved Decisions — Do Not
Re-Litigate," "Execute the following steps," "These are final." This is usually wrong.

The downstream reader often has evidence the author lacks: target-repo access, tests, and local
rules. Command framing can make them silently follow a plan the code contradicts.

Test that asymmetry **per decision**: who can access the evidence that bears on it? Downstream
often knows the target code and tests better; upstream may know legal rules, security policy,
product intent, or external facts unavailable in the worktree.

Evidence and decision authority are separate. Better evidence licenses a revisit request, not
the right to change scope, values decisions, or explicit user constraints.

## Context / Trigger Conditions

Apply when writing handoffs, plans, dispatch prompts, workflow briefs, future-work ADRs, or
instructions to a fresh session.

Symptoms: blanket "Do Not Re-Litigate" / "These are final" headers; evidence-sensitive decisions
without "Revisit if:"; no per-decision evidence test; or proposed work written as commands.

## Solution

### 1. Default framing: informed proposals from a less-informed reviewer

Open with a framing block adapted to the actual evidence asymmetry. Full paste-ready template:
[FRAMING-TEMPLATE.md](FRAMING-TEMPLATE.md).

### 2. Classify each decision; add "Revisit if:" only when evidence can change it

For every decision ask: **what evidence could change this outcome, and who can access it?** Label
it `Revisable with new evidence` and add a specific `Revisit if:` only when such evidence exists.
Label values decisions and explicit user constraints `Non-negotiable`; keep them imperative.
Decision-status block examples live in [FRAMING-TEMPLATE.md](FRAMING-TEMPLATE.md).

### 3. Acceptable narrow use of "do not re-litigate"

Use the phrase only for a **specific question** the user explicitly closed in the current
conversation.

Acceptable: "User decided 'PostgreSQL not SQLite' in turn 14. Do not re-litigate this choice."

Not acceptable: a blanket "Approved Decisions — Do Not Re-Litigate" header.

### 4. Imperative → proposal mood

| Anti-pattern | Replacement |
|---|---|
| "Execute the following plan" | "Recommended execution path" |
| "Do X" | "X looks right from here; recommend" |
| "These are final" | "These are the working direction" |
| "Implement A, B, C" | "Implementation candidates: A, B, C" |
| "Must do X" | "X is the prior session's best recommendation" |

Imperative mood remains appropriate for legal and security boundaries, values decisions,
NEVER-tier rules, and explicit non-negotiables. Better evidence does not soften them.

## Verification

After drafting any downstream-instruction artifact:

- [ ] Each decision tests who can access the evidence that bears on it
- [ ] Evidence and decision authority are separate
- [ ] Every evidence-sensitive decision is labeled revisable and has a specific "Revisit if:"
- [ ] Values decisions and explicit user constraints are labeled non-negotiable and imperative
- [ ] Disagreement-with-reasoning is licensed only for revisable instructions
- [ ] "Do not re-litigate" is absent, OR scoped to a single explicitly-closed question
- [ ] Revisable recommendations use proposal mood; genuine hard constraints do not
- [ ] Downstream is required to surface disagreement rather than silently deviate

If any answer is no, revise before delivery.

## Example

**Anti-pattern (caught and corrected 2026-06-07, a private production project's security
handoff):**

```markdown
## Approved Decisions (Already Made — Do Not Re-Litigate)

- Phase E expands to include E-ADD-1 through E-ADD-5.
- The security-item δ-pattern design is drafted. Recommended absorption as E-ADD-6.
```

**Corrected version:**

```markdown
## User-Approved Directional Decisions (Revisable With New Evidence)

These were approved by the user against the framing this session presented. If reading the
actual codebase changes the framing, surface the change and let the user re-decide.

- Phase E expands to include E-ADD-1 through E-ADD-5. *Revisit if:* any item is already
  done, duplicative, or has a wrong cost estimate by >2x.
- The security-item δ-pattern design is drafted. Recommended absorption as E-ADD-6.
  *Revisit if:* the actual architecture makes the separation incompatible, or there's a
  simpler way to close the threat you can see from inside the tree.
- **Non-negotiable:** Preserve the user-set security boundary; surface conflicts, do not
  override it.
```

## Notes

- **Subagent prompts are riskiest.** Agents read dispatches as near-system-tier and rarely push
  back; make their framing block explicit.
- **Does not apply to genuine hard constraints.** Security boundaries and user-stated
  non-negotiables are imperative for legitimate reasons. The skill governs the *default*
  framing of *proposed* work.
- **Use "Revisit if:" only when evidence can change the outcome.** Otherwise mark a values
  decision or explicit user constraint non-negotiable; a fake revisit condition is noise.
- **Failure prevented:** downstream silently executes a plan its evidence contradicts.
