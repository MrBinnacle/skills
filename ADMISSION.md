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

## Authorship is a precondition, not an admission question

A candidate enters this repository's tree, under `skills/`, `_quarantine/` or
anywhere else, only when this collection authored it; another author's skill is
composed by name from its own source and never held here, as
[ADR 0006](docs/adr/0006-the-collection-holds-only-what-it-authored.md) records.
A candidate that fails this precondition never reaches the four questions, so
the precondition does not change them or what counts as answering them, and
adding it does not bump this policy's version. [precondition added 2026-10-20]

## A mod is not a card

A Claude Code mod this collection authored is held under `mods/`, beside the cards. The
authorship precondition above applies to it. The four questions do not, because they test
whether a skill earns a place in the context window and a mod loads nothing into it. A mod
enters on its own conditions, recorded in
[ADR 0009](docs/adr/0009-the-collection-also-ships-mods-it-authored.md). The four questions and
what counts as answering them are unchanged, so this section does not bump this policy's
version. [section added 2026-10-23]

## Form constraints are not admission questions

A card that passes all four questions must still take the published form:
frontmatter, size bounds, the evidence rows, and harness neutrality (its
`SKILL.md` names the action, not one harness's tool, hook or path; the
harness-specific recipe lives in a sibling file). Those rules live in
[`AGENTS.md`](AGENTS.md): frontmatter, sizes and harness neutrality under
"Authoring conventions", the evidence rows under "Repository layout".
`scripts/validate_card_files.py` checks the description length, the size
bounds and the evidence rows; `scripts/validate_harness_neutrality.py`
checks harness neutrality. They decide form, not worth, and adding one does not
bump this policy's version: the four questions are unchanged. [pointer added
2026-10-10]

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
  outcomes of the without-skill arm of a **screen** (controlled unaided runs;
  the with-skill arm never ran), not a separate policy text.
- Front-page and contributing prose that pair "the gate" with what may enter
  the collection are about the **admission policy**.

Downstream edits to the front page, the exit register, and the banner should
apply this table rather than inventing a fourth reading.
