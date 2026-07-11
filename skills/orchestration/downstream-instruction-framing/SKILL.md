---
name: downstream-instruction-framing
description: Framing discipline for any artifact instructing a downstream reader — handoffs, plans, ADRs, subagent prompts. Bans blanket do-not-re-litigate framing; requires per-decision Revisit-if clauses.
---

# Downstream-Instruction Framing Discipline

## Problem

When writing instructions for a downstream reader (handoff, plan, ADR, subagent prompt), LLMs
default to authoritative framing: "Approved Decisions — Do Not Re-Litigate," "Execute the
following steps," "These are final." This framing reads natural and decisive — and is almost
always wrong.

The downstream reader is engaged precisely because their proximity to the evidence (target
repo, file access, ability to run tests, project-local rules loaded) gives them judgment the
upstream author lacks. Command framing strips that judgment exactly when it is most valuable.
The result: a smart downstream agent silently follows a plan that contradicts what they can
plainly see in the code.

The upstream author is **always** the less-informed reviewer relative to the downstream
executor. Framing must reflect that asymmetry, not invert it.

## Context / Trigger Conditions

Apply this skill when writing **any** of: handoff documents, execution plans, subagent dispatch
prompts, workflow scripts, scheduled-agent briefs, ADRs proposing future work, or instructions
to a fresh agent session opening elsewhere.

Symptoms that it's being violated: headers like "Execute the following" / "Do Not Re-Litigate" /
"These are final"; decision lists with no "Revisit if:" clauses; no acknowledgment that the
downstream reader has more evidence access; no explicit license to disagree; imperative mood
throughout ("Implement X. Do Y.") rather than proposal mood ("Recommend X.").

## Solution

### 1. Default framing: informed proposals from a less-informed reviewer

Open every downstream-instruction artifact with an explicit framing block. Template:

```
## How to Treat This Document

You are not being given orders. You are being given the prior session's best research
output, written by a session that [name the evidence asymmetry — e.g., could not read
the target codebase directly / worked from summaries only / had no test-run authority].

Your situational advantage over the author:
- [Specific capability the downstream reader has that the author did not]
- [Repeat for each concrete advantage]

Therefore: treat the prior decisions and recommendations as *informed proposals from a
less-informed reviewer*. They reflect what looked right from outside [the relevant
context]. You are inside [the relevant context] now.

You are explicitly licensed and encouraged to:
- Disagree with the recommendations if [evidence access] reveals the framing was wrong.
  Surface the disagreement to the user with reasoning; don't silently follow a bad plan.
- Restructure sequencing if the real dependency graph differs.
- Reject items that turn out to be solved already, duplicative, or premature.
- Add items the prior session missed. The coverage is a floor, not a ceiling.
- Redesign approaches if the proposed design conflicts with what the actual code shows.

What you should NOT do:
- Treat any "decision" below as immutable. It was approved against the framing the
  author gave the user. Different framing, different decision.
- Silently deviate. The user is the decision authority on scope changes; surface
  disagreement with reasoning, then let them decide.
- Re-open questions the user has closed *without new evidence*. Disagreement is
  welcome; arbitrary re-opening is not.
```

### 2. Per-decision "Revisit if:" clauses

When listing prior decisions, attach a `Revisit if:` clause to each:

```
## User-Approved Directional Decisions (Revisable With New Evidence)

These were approved by the user against the framing this session presented. They are the
working direction, not commands.

- Phase X expands to include items A, B, C. *Revisit if:* any item is already done,
  duplicative, or has a wrong cost estimate by >2x.
- Design Y was approved. *Revisit if:* the actual architecture makes it incompatible,
  or there's a simpler/better way you can see from inside the tree.
```

### 3. Acceptable narrow use of "do not re-litigate"

The phrase is acceptable only when scoped to a **specific question** the user has explicitly
closed *in the current conversation* with a "decided, move on" signal.

Acceptable: "User explicitly decided 'PostgreSQL not SQLite' in turn 14. Do not re-litigate
this specific choice." (One decision, named, just closed.)

Not acceptable: "Approved Decisions — Do Not Re-Litigate" as a section header covering multiple
decisions, or any blanket framing applied to all prior choices.

### 4. Imperative → proposal mood

| Anti-pattern | Replacement |
|---|---|
| "Execute the following plan" | "Recommended execution path" |
| "Do X" | "X looks right from here; recommend" |
| "These are final" | "These are the working direction" |
| "Implement A, B, C" | "Implementation candidates: A, B, C" |
| "Must do X" | "X is the prior session's best recommendation" |

Imperative mood is appropriate only for genuine hard constraints (security boundaries,
NEVER-tier rules, user-explicit "this is non-negotiable" decisions).

## Verification

After drafting any downstream-instruction artifact:

- [ ] "How to Treat This Document" section (or equivalent) names the evidence asymmetry
- [ ] The downstream reader's situational advantages are stated
- [ ] Disagreement-with-reasoning is explicitly licensed
- [ ] Every prior decision has a "Revisit if:" clause
- [ ] "Do not re-litigate" is absent, OR scoped to a single explicitly-closed question
- [ ] Headers and decision lists are in proposal mood
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
```

## Notes

- **Subagent prompts are the riskiest case.** A subagent reads the dispatch prompt as
  near-system-tier and will rarely push back even when licensed to. For subagent prompts,
  invest in the framing block doubly hard.
- **Does not apply to genuine hard constraints.** Security boundaries and user-stated
  non-negotiables are imperative for legitimate reasons. The skill governs the *default*
  framing of *proposed* work.
- **The "Revisit if:" clause is a forcing function for the upstream author too.** If you can't
  name a condition under which the decision should be revisited, the decision may be
  under-justified — either it's a genuine non-negotiable (mark it as such) or you haven't
  thought through the failure modes.
- **Failure mode this prevents:** a smarter, closer-to-the-evidence downstream agent silently
  executing a plan that contradicts what they can plainly see, because the upstream framing
  told them not to question it.
