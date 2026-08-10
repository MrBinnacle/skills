# Admission policy

`admission-policy v1`

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

The four questions are answered by running
[`skill-necessity-gate`](skills/meta/skill-necessity-gate/SKILL.md) — the
**gate card**. That skill is the reference method for this policy, not the
policy itself.

The four questions distill that card's **first three gates only** (layer
triage, recurrence, and measured worth). The card's remaining gates cover
invocation topology, statefulness, and shape: those are authoring guidance for
a candidate that has already cleared admission. They are not admission
criteria and do not belong in this file.

## Naming: "the gate"

This repository has used the phrase "the gate" for two different instruments.
Naming this policy makes a third. The convention:

| Prefer | Means | Lives |
|---|---|---|
| **admission policy** | the binding four-question rule for what may enter | this file (`admission-policy v1`) |
| **gate card** / **skill-necessity-gate** | the reference procedure for answering the four questions | `skills/meta/skill-necessity-gate/` |
| **screen** / **admission screen** | the empirical with/without-skill measurement that produces ceiling and turned-away outcomes | recorded in [`RETIRED.md`](RETIRED.md); instrument upstream of this collection |

Bare "the gate" is ambiguous. Read it from context, or replace it with one of
the three names above when editing:

- Turned-away rows and "screened out at the gate" prose in `RETIRED.md` are
  **screen** outcomes (controlled unaided runs), not a separate policy text.
- Front-page and contributing prose that pair "the gate" with what may enter
  the collection are about the **admission policy**, answered via the
  **gate card**.

Downstream edits to the front page, the exit register, and the banner should
apply this table rather than inventing a fourth reading.
