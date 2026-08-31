---
name: private-steering-head-over-public-repos
description: |
  Running one private repository that decides, audits and stages work for two or more public
  repositories it owns. Use when: (1) a question arrives that a sibling repo already answers and
  you are about to answer it from the steering repo instead; (2) you are about to build an
  instrument — script, metric, harness, gate, receipt schema, checker — without reading the
  siblings first; (3) you write or match a bare `#N` issue reference that will be read in a
  different repository than it was written in; (4) you are summing or averaging board health,
  drift or coverage across repos; (5) an artifact is produced and its home repo is unobvious;
  (6) a wayfinder-style map or index spans repos. Covers the cross-repo issue-number collision,
  per-board failure-mode asymmetry, the sibling-first prior-art gate, and artifact routing.
author: Claude Code
version: 1.0.0
date: 2026-08-26
---

# A private steering head over public repositories

## Problem

A common and unnamed topology: **one private repository decides, and two or more public
repositories ship.** The private repo holds the reasoning, the audits, the doctrine and the staging
of launches; the public repos hold the artifacts the world sees.

It works well, and it has failure modes that only appear at the seams between the repos. Every one
of them produces a *confident* wrong answer rather than an error, because each repo is internally
consistent and the contradiction lives in the gap.

## Context / Trigger Conditions

- You are in the steering repo and about to answer a question about a sibling **from memory,
  from the steering repo's own docs, or from public literature**.
- You are about to build any instrument — a script, metric, harness, gate, checker, receipt schema,
  dashboard, fixture set or scoring procedure.
- You are writing, parsing, or matching an issue reference that may be read in a different repo
  than the one it names.
- You are aggregating board health, drift counts, coverage or defect totals **across** repos.
- An artifact has just been produced and more than one repo could plausibly hold it.
- An index, map or manifest in one repo points at tickets in another.

## Solution

### 1. The nearest prior art is the sibling, and it outranks the literature

Before building an instrument, **read the siblings.** A prior-art sweep that cites the outside
literature and skips the repo one directory over has failed, not partially succeeded.

The failure mode is specific: the steering repo is where *reasoning* happens, so it is where you
naturally look for what is known — but the *instruments* live in the sibling. Assume the pattern
you are about to invent is already implemented next door until a read says otherwise.

**The gate applies to promotion, not to measurement.** Writing a one-off script in a scratch
directory to answer a question in front of you is a different act from adding an instrument to a
repo. Run the gate at the moment you promote it.

### 2. Write `owner/repo#N`, always — issue numbers are per-repo

**Bare `#N` is ambiguous across repositories and both writing it and matching it fail.**

- **Writing:** a bare `#N` in a body rendered in a *different* repo resolves against that repo,
  silently linking to an unrelated issue or pull request.
- **Matching:** a regex or tool that extracts `#N` and looks it up loses the owning repo. It will
  return a real, wrong ticket, and the collision is most likely exactly where numbering ranges
  overlap — which is early in every repo's life.

Verified on 2026-08-26: a cross-board scan for references to steering-repo `#25` and `#33` flagged
a public repo's map — which was referencing **its own** `#25` and `#33`. The scan reproduced a
defect already filed in the same steering repo, while hunting for other people's defects.

**Native cross-repo dependency edges have the same hazard.** If tooling resolves blocking edges by
bare number, keep cross-repo blocks out of the native mechanism and state them in prose, or fix the
resolver first.

### 3. Never sum board health across repos — report per-board and per-predicate

Different repos develop **different** failure modes, and a total hides both.

Measured across two public siblings on 2026-08-26:

| defect class | public repo A | public repo B |
| --- | --- | --- |
| label / cross-reference drift | **10** instances | 1 |
| closed tickets with **no recorded resolution** | 0 of 17 | **6 of 26** |

Each board is clean on the other's failure mode. A single "drift score" summed across both would
have reported a healthy pair and missed both classes. **A cross-repo health metric must be a
matrix, never a scalar.**

### 4. Route artifacts by a written boundary rule, decided once

Ambiguity about where an artifact lands produces duplicates in two repos, which then diverge. Write
the rule down and apply it mechanically. A rule that works:

- **Receipts, dispositions of record, and the published artifacts** → the collection repo.
- **Measurement machinery and methodology** → the instrument repo.
- **Research provenance, audits, doctrine, and framework** → the steering head.

The steering head is also the only place that can hold **cross-repo tickets**, because it is the
only one without a public-surface constraint. That is a real capability, not an accident, and it is
why maps spanning several repos live there.

### 5. Check an index at the ENTRY level, not the mention level

Where a map or index in one repo points at tickets across repos, "is this ticket referenced" is the
wrong question. **The unit is the entry.** A ticket named inside a *different* entry's prose has no
entry of its own, and a reader cannot scan or zoom from it.

Both failure directions are real and each has a measured cost:

- **Too narrow** — matching only bare `#N` misses entries written as titled markdown links.
- **Too broad** — matching anywhere in the section scores a cross-reference as an entry.

Check both. A poison fixture for each direction is what proves the checker works.

### 6. When a closed ticket records no decision, say so — never gist the title

A ticket closed with no resolution comment has **no decision to index**. The only material
available is the title, and a title states an *intention*, not an outcome.

**Writing a plausible gist from a title puts a claim nobody made onto a public board.** Observed:
a ticket titled "rewrite the front door…" had zero comments, and the file it named was later
rewritten again by a different ticket. A title-derived gist would have recorded stale work as a
decision of record.

The correct entry states that the decision was not recorded. This is the same discipline as
refusing to invent a measurement: **a missing decision is a typed refusal, never a paraphrase.**

## Verification

- Before promoting any instrument: name what you found in each sibling, or the search that found
  nothing there.
- Grep your own output for `(?<![\w/])#\d+` before posting cross-repo. Every hit should be
  `owner/repo#N`.
- Any cross-repo health report renders as a table with one row per repo and one column per
  predicate. If it renders a single number, it is wrong.
- Every artifact produced in a session has a named home repo, chosen by the written rule and not by
  where the session happened to be.

## Notes

- **The steering head's own board is a board too** and drifts the same way. Audit all three,
  including the one you are sitting in.
- **Merging and publishing are different acts.** Merging a pull request on a sibling is routine
  maintenance; a release tag, a new published asset, or anything that changes what the public sees
  is a publication decision and belongs to the owner.
- The topology's core benefit is that **a question about a sibling has a determinate home**:
  measured in the instrument, recorded in the collection, reasoned about in the head. Most seam
  failures above are what happens when a question is answered in the wrong one of the three.
- See also: `agent-definition-snapshot-at-session-start` for the neighbouring class where a stale
  snapshot is mistaken for a missing capability.
