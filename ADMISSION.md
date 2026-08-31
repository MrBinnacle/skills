# Admission policy

The declared version and the bump rule are in [Version](#version) below. They are
stated there once and nowhere else in this file, so that a version bump cannot be
applied to some copies and missed on others.

This file is the binding rule for what skills may enter this collection. It is
whole and versioned on purpose: past decisions can name the edition they were
made under, and a cross-repository digest of the policy text can travel without
depending on section offsets inside a larger document.

## Version

- **Declared version:** `admission-policy v1`
- **Bump rule:** any material change to the four questions below, or to what
  counts as answering them, requires a version bump (`v1` → `v2`, …). Editorial
  clarification that does not change the rule does not.

## The four-question admission test

A candidate enters only when all four are true:

1. An **unaided failure exists** — a current frontier model, given the situation
   the skill is for and *without* the skill, still fails the job the skill
   claims to fix. Observed, not predicted: run it unaided first.
2. The failure **recurs independently** — it is not a one-off; occasions are
   counted, not predicted, and not inflated by fan-out from a single run.
3. A **skill is the correct control surface** for it — not a project rule, not
   an MCP/connector, not something the agent can read from the repo, not a
   harness-supplied default, and not an always-on preference that belongs in
   standing instructions.
4. **Evidence supports admission and later retirement** — the case is written
   down so a later reader can see why it entered, and so it can leave when a
   newer model ceilings it or a pre-registered platform fix lands.

Default answer: not admitted.

## Reference method

There is none, and that is deliberate. This policy used to name
`skill-necessity-gate` as the reference procedure for answering its four
questions. That card retired on 2026-08-31 (issue #178) because it could not
satisfy criterion 1 of this policy: its own evidence record counted zero
observed occurrences.

The four questions were always the binding rule and they stand unchanged. They
distilled the retired card's first three gates — layer triage, recurrence, and
measured worth — and that distillation already happened, so the policy loses a
pointer rather than any of its substance. The card's remaining gates were
authoring guidance for a candidate that had already cleared admission; the
topology rule among them now lives in [`AGENTS.md`](AGENTS.md) as a rule in its
own right.

## Naming: "the gate"

This repository has used the phrase "the gate" for more than one instrument.
The convention:

| Prefer | Means | Lives |
|---|---|---|
| **admission policy** | the binding four-question rule for what may enter | this file; see [Version](#version) for the edition |
| **screen** / **admission screen** | the empirical with/without-skill measurement that produces ceiling and turned-away outcomes | recorded in [`RETIRED.md`](RETIRED.md); instrument upstream of this collection |

Bare "the gate" is ambiguous. Read it from context, or replace it with one of
the three names above when editing:

- Turned-away rows and "screened out at the gate" prose in `RETIRED.md` are
  **screen** outcomes (controlled unaided runs), not a separate policy text.
- Front-page and contributing prose that pair "the gate" with what may enter
  the collection are about the **admission policy**.

Downstream edits to the front page, the exit register, and the banner should
apply this table rather than inventing a fourth reading.
