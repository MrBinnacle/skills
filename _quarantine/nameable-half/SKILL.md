---
name: nameable-half
description: Use when writing or trusting a checkpoint band, handoff or packet that compresses a receipt. A summary reading "all X are P" where the source said "P or Q" keeps the half with the familiar name.
author: Claude Code
version: 1.0.0
date: 2026-09-07
---

# A Summary Narrows a Disjunction to Its Nameable Half

## Problem

A receipt records a disjunction: *every case is under P or Q*. A later summary of that
receipt records *all cases are under Q*.

Nothing was fabricated. The count survives, the verdict survives, and the sentence reads
as a faithful compression. But the summary now asserts something its own source does not
support, and it asserts it with a universal quantifier the source never used. A reader who
acts on the summary fixes Q and finds most of the problem still there.

The literature calls this an intrinsic hallucination — a faithfulness failure where the
output contradicts material the model was given, rather than inventing material it was
not. Overgeneralization is the named sub-case, and it accounts for roughly a fifth of
hallucinations in summarization work.

**The selection is not random.** The member that survives is the more nameable one, because
compression optimises for a sentence that reads well and a well-known noun reads better than
a path nobody recognises. `node_modules/` survives; `.sandcastle/worktrees/agent-issue-154/`
does not. So the dropped member is frequently the LARGER one — size and nameability are
unrelated.

## Context / Trigger Conditions

Fires wherever a durable summary is written from a longer record, and wherever one is read
before acting:

- Session checkpoints, state bands, close packets, handoff documents, resume notes.
- A pull-request description compressing a design document.
- A ticket body compressing an investigation log.
- An incident summary compressing a timeline.
- Any "what I found" paragraph whose evidence lives in a separate file.

Reach for it the moment a claim carries **`all`, `every`, `none`, `only`, or `always`** and
the evidence for it is somewhere else.

## Solution

Two moves. The first is for the writer, the second for the reader.

### Writing: keep the disjunction, drop the adjective

When compressing, the enumeration is the load-bearing part and the prose around it is not.
Cut the prose. If two locations, two causes or two conditions were recorded, the summary
carries both or it carries neither.

If both genuinely will not fit, write the count per member rather than a bare total:
`48 under A, 6 under B`. That is shorter than most of the sentences it replaces, and it
cannot narrow.

### Reading: check the quantifier against the receipt, not the claim against the world

Auditing a summary by asking "is this true?" fails here, because the summary is *nearly*
true and the near-miss is the whole defect. Ask instead:

1. **Locate the source sentence.** The summary cites a receipt, or names a command. Open it.
2. **Compare the enumerations.** Does a list in the source appear complete in the summary?
   Count the members on each side.
3. **Compare the quantifiers.** `all` / `every` / `only` in the summary against `or` /
   `most` / `some` / a bare plural in the source. A quantifier that appears in the summary
   and not in the source is the finding.
4. **Ask which member is more nameable.** If exactly one survived and it is the one with
   the familiar name, treat the other as present until a command says otherwise.

The cheapest instrument is the one that produced the number. Re-run it and group by the
dimension the summary collapsed.

## Verification

The command that settles it groups the raw output by the dropped dimension:

```sh
# The summary said "all 54 breaches are in node_modules/".
python scripts/validate_brand_kit.py 2>&1 | grep '^  - ' | cut -d/ -f1 | sort | uniq -c
#      48   - .sandcastle
#       6   - node_modules
```

The total agrees with the summary. The distribution refutes it. **A summary that gets the
count right is not thereby confirmed** — check the count and the partition separately,
because compression preserves totals far more reliably than it preserves partitions.

## Example

A checkpoint band recorded, of a repository's copy checker:

> all 54 breaches sit in untracked `node_modules/`, because the checker walks the
> filesystem instead of reading the tracked set

The receipt it was written from recorded, correctly, at `docs/design/make-log-S425.md:212`:

> Every breach is under `.sandcastle/worktrees/agent-issue-154/` or `node_modules/`.

Measured: 48 under `.sandcastle/worktrees/`, 6 under `node_modules/`, 54 total, 0 in a
tracked file.

The count was right. The mechanism was right. The location was wrong in the way that
mattered: a session that cleaned `node_modules/` would have cleared 6 of 54, seen the gate
still red, and concluded the diagnosis was wrong.

**The error entered at the compression step, not at the measurement step.** The receipt was
accurate and stayed accurate. That is the argument for auditing the summary against its
source rather than trusting the summary because its source was careful.

The same band carried three more instances, each with its command in
[`worked-case.md`](worked-case.md). Four in one document is a rate, not a slip.

## Notes

- **This is not vagueness, and a vagueness check will not catch it.** The compressed claim
  is sharper than the source. Guidance to "avoid over-compressing into vagueness" points at
  the opposite failure and gives this one a clean pass.
- **A lossless-claim inventory will not catch it either.** The claim inventory is unchanged
  across the compression; one factual claim got narrower. See `context-hygiene`, whose gate
  is claim-level (`SKILL.md:74-76`) and which documents two sibling traps at `:92-93` —
  optionality lost to flattening, reachability lost to relocation. This is a third member of
  that family and needs its own recognizer.
- **Scope it honestly.** This is not a claim that summaries are unreliable in general, and
  it does not license re-deriving every fact. The trigger is narrow: a quantifier whose
  evidence is elsewhere.
- **The receipt can be wrong too.** This card says the summary is the more likely site, not
  the only one. When the receipt and the summary disagree, run the command.
- Related: `quiet-false-assumptions` (an unlabelled inference between two verified facts
  inherits their credibility), and `lock-the-shape-not-the-value` (a test asserting a
  measured figure's literal value cannot see staleness).
