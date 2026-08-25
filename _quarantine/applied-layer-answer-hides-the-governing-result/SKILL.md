---
name: applied-layer-answer-hides-the-governing-result
description: "Fires after a prior-art sweep SUCCEEDS: its sources are applied docs, not the theory they instantiate; you are about to record 'no prior art'; or a name-grep of zero is becoming an absence claim."
author: Claude Code (extracted from a research session, 2026-08-25)
version: 1.0.0
date: 2026-08-25
---

# An applied-layer answer hides the governing result

## Problem

A search that fails prompts a wider search. **A search that succeeds shallowly does not.**

This is the whole mechanism. When a prior-art sweep returns material that is relevant, correct and
citable, every quality signal reads green: sources found, claims supported, citations recorded. The
sweep is *done*. Nothing in the process asks whether the answer sits at the right depth, because
nothing has gone wrong.

So the sweep terminates one layer above the result that actually governs the problem — typically in
applied papers, vendor documentation, practitioner writing or case studies, all of which are
instances of a theory nobody went looking for.

The cost is asymmetric and delayed. A wrong answer gets caught. A *shallow* answer gets built on,
cited forward, and hardens into the frame everything downstream assumes.

## Context / Trigger Conditions

Fire this **after a sweep succeeds**, not after one fails.

- A prior-art or literature sweep returned usable sources and you are about to act on them.
- The sources are applied: schema docs, evaluation frameworks, tooling papers, practitioner blogs,
  vendor documentation, case studies, "how we did X" writeups.
- Two or more sweeps on the same question both returned the same layer. **Agreement between
  shallow sweeps is not corroboration — it is the same blind spot run twice.**
- You are about to write that something "has no prior art", "does not reduce to existing work", or
  "appears to be novel."
- The problem involves an object with a mathematical or formal identity: an ordering, an
  equivalence, a minimality claim, a sufficiency condition, an information measure, a decision rule.
- **Second face:** you grepped for a NAME, found zero hits, and are about to conclude the
  CAPABILITY does not exist.

## Solution

### The question that breaks it

> **What is this answer an instance of?**

Ask it of the material the sweep returned, then search *that*. Repeat until the answer stops moving.

The applied layer describes a practice. The layer beneath names the object the practice manipulates
and usually proves something about it — uniqueness, tractability, a boundary, an impossibility.
That proof is what you actually needed.

### The ladder

Walk down until the answer stops changing:

1. **Practice** — how people do it. Blogs, vendor docs, tooling.
2. **Applied research** — papers reporting results in your domain.
3. **The formal object** — the ordering, equivalence, quotient, measure, or game the applied work
   instantiates.
4. **The theorem about that object** — and, critically, its *boundary conditions*, which are what
   tell you whether your case is the easy one or the undecidable one.

### Finish on the object, not on the citation

A sweep is finished when you can name the object your problem is an instance of, or state honestly
that you looked for it and it has no formal identity. Citations in hand is the state that feels
finished and is not.

### For the second face (name-grep → false absence)

A grep for a name answers a question about your **query string**, not about the **territory**.
Before recording an absence:

- Read the **index** — the command table, the API surface, the exported symbols, the docs contents
  page — rather than grepping for the word you expect.
- Consider that the capability may exist under a different name, an older name, or a renamed one.
- **An absence claim must name the command that establishes it and that command's limit.** The
  nearest relative here is `declined-computation-hides-a-discarded-field`: both separate a real
  limit from a self-inflicted one, that skill through data discarded at a type boundary, this one
  through a search term that missed a renamed capability.

## Verification

You have actually gone deeper when at least one of these is true:

- You can name the formal object and the result about it, with a source.
- You found a **boundary condition** the applied layer never mentioned (a tractability cliff, an
  undecidability result, a uniqueness or non-uniqueness fact, a failure case of a theorem).
- Your original framing turns out to be a **special case** of something more general, and you can
  say which special case and why that restriction was the right choice.
- Or: you searched the lower layer specifically and it is genuinely absent — record *that*, with
  the search, as a finding.

If a deeper sweep returns nothing and you cannot say what you searched for, you have not verified
absence; you have repeated the original sweep with more words.

To see both faces caught in one session — a criterion that turned out to be Blackwell's
sufficiency ordering, and a grep that manufactured an absence — read
[`worked-example.md`](worked-example.md).

## Notes

- **The named mechanism is satisficing** (Simon): search terminates at the first *adequate* option
  rather than the best one. Worth knowing because it predicts when this fires — under time
  pressure, and when the first result is genuinely good. A bad first result is safer than a decent
  one.
- **This fires on a filter, not on every question.** Most questions are answered correctly at the
  applied layer, and descending on every one is its own waste. The trigger list above is the
  filter: fire on formal objects, on novelty claims, and on repeated same-layer sweeps.
- **Two shallow sweeps agreeing is the strongest false signal here**, because agreement reads as
  corroboration. It is one blind spot, sampled twice.
- **Cost asymmetry is what justifies the check.** Finding the governing result late means every
  downstream artifact already encodes the shallow frame.
- Running and verifying a multi-agent sweep is a different job, covered by
  `cite-verified-research-sweep`. That skill makes a sweep's findings trustworthy; this one asks
  whether the sweep stopped at the right layer. A sweep can pass every check there and still fail
  this one.
