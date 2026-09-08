---
name: curated-context-becomes-the-reviewers-boundary
description: Use when assembling a brief for a reviewer or subagent, or when its answer collides with a rule you never sent. Your selection became its design boundary, so the collision is manufactured, not found.
author: Claude Code
version: 1.0.0
date: 2026-09-06
---

# Curated context becomes the reviewer's design boundary

## Problem

You send a reviewer the rules you judged relevant. It returns a recommendation that violates a rule you did not send. You now have a collision that looks like a disagreement between two authorities, and it is not one — the reviewer never had the second authority in front of it.

The damage is not the collision. It is what you do next. The natural write-up is *"the reviewer proposed X, but our conventions say Y, so the tree overrides."* That sentence attributes to the reviewer an error you created, and it closes the question without anyone testing whether Y is right.

Worse, it is self-sealing. You selected the context, so the answer came back shaped like your selection, which reads as confirmation.

## Context / Trigger conditions

- A review recommends something the codebase's own documented conventions forbid.
- You are drafting the words "the reviewer did not know about" or "our rule overrides this."
- You are assembling a brief and deciding which rules count as relevant to the question.
- A recommendation fits your existing framing unusually well.
- The reviewer had no repository access and worked from what you pasted.
- You are dispatching a subagent to design or decide, rather than to fetch.

## Solution

### 1. Treat the collision as evidence about your brief first

Before writing that a reviewer was wrong, check whether it was shown the rule it violated. If it was not, the finding is about the brief. Say so in that order — the brief, then the rule — because the reverse order buries it.

### 2. Then test the house rule anyway

A rule the reviewer never saw has not been defended, only invoked. Three cheap tests, in order:

- **Does the exemplar obey it?** Find the artifact the rule was drawn from. It may not adjudicate at all — a silent exemplar means the rule was generalised past its source.
- **Did the corpus obey it?** Measure by role, not by filename. A rule with a prohibition half and a positive half tends to get the prohibition obeyed and the positive ignored.
- **Is the rule doing more than one job?** Rule plus rationale plus empirical claim plus future decision procedure, in one sentence, gets obeyed selectively.

### 3. Put the six things in every brief

The reviewer cannot ask for what it does not know exists. What goes in, every time:

1. **The decision and its authority.** What is being decided, what the reviewer may recommend changing, and which constraints come from external compatibility rather than local preference.
2. **The applicable instructions, verbatim.** The governing section in full, plus any section it references that bears on the decision. Not your paraphrase, and not the subset you judged relevant.
3. **The current artifact.** The actual file or diff and its revision. Not rules and measurements about it.
4. **The operating environment.** How the artifact is installed, discovered, loaded and validated. Include the validator's implementation when asking what it should enforce.
5. **Evidence and its limits.** What was measured and how. Separate observed facts from interpretations, and say what the exemplar actually demonstrates.
6. **Prior advice and what you did with it.** The recommendation being reconsidered and the edits made from it, so the reviewer is not reconstructing either from your account.

### 4. Mark the constraints revisable, and mean it

State which rules are amendable and which are externally binding. A brief that presents house conventions as fixed gets back a recommendation that designs around them, which is the same failure wearing different clothes.

### 5. Close with a disclosure

> These are the applicable conventions I found. These are the unresolved facts. These parts of my interpretation are hypotheses.

That is not a claim to have found everything. It is a check against converting your selection into the reviewer's boundary without either of you noticing.

## Verification

Before sending:

- Every rule that could bear on the decision is in the brief verbatim, or its absence is disclosed.
- The artifact itself is attached, not only facts about it.
- Each constraint is marked revisable or externally binding.
- Interpretations are labelled as interpretations.

After the answer returns, and this is the load-bearing check:

- For every point where the recommendation collides with a local rule, ask whether that rule was in the brief. If it was not, the collision is yours.

## The failure, in one line

A reviewer was sent two authoring rules out of a conventions section and returned a template that collided with a third rule it was never shown. The first write-up called that the reviewer's error. Testing the house rule instead found it defective — the exemplar it was drawn from could not adjudicate it, and 21 of 47 reader-facing files in the corpus were unreachable because the prohibition half had been obeyed and the positive half had not.

The full case, including the corrected measurement and the causal claim that rode along with it, is in [`worked-case.md`](worked-case.md).

## Notes

- **The reviewer being right is not the point.** The point is that a curated brief makes the question unanswerable correctly, whichever way it goes.
- **Volume is not completeness.** Sending the whole repository is the opposite error and produces a worse answer. Completeness is about decision-relevant context.
- **Access is not inspection.** If the reviewer has a pinned checkout, paths can replace pasted text only when it actually reads them. Assume it did not unless it says what it read.
- **This is the mirror of over-constraining.** A brief that hides rules gets a recommendation that violates them; a brief that presents rules as immovable gets a recommendation that designs around them. Both are the brief deciding the answer.
- See also: `downstream-instruction-framing` for the decision-rights half of the same problem — separating evidence access from authority to change scope. See also: `verbatim-content-subagent-dispatch` for embedding a spec verbatim rather than by pointer, which is this discipline applied to execution rather than to design.
