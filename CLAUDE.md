# CLAUDE.md — project delta

This is the repo-local half of a two-layer design. The global half — the project-agnostic
operating rules — is published here as
[`templates/BASE-OPERATING-RULES.md`](templates/BASE-OPERATING-RULES.md), a template for
adopters to copy to `~/.claude/CLAUDE.md`. This file holds only what governs work in *this*
clone, and it is what an agent should load when working here.

It doubles as the worked example that template points at. It is short on purpose: a delta that
outgrows a screen is usually holding something that belongs in the global layer, in
[AGENTS.md](AGENTS.md), or in a skill.

## What this repo is

A small collection of agent skills kept only while evidence supports keeping them. Each skill
ships a `SKILL.md`, a `gotchas.md` (append-only observed failure modes), and an `EVIDENCE.md`
provenance record. Skills that stop earning their place are retired into `RETIRED.md` with the
evidence attached rather than deleted quietly.

The collection is deliberately small. Adding a skill is the exception; the default answer to
"should this be a skill?" is no. The binding rule is [`ADMISSION.md`](ADMISSION.md).

## Where the working conventions live

[AGENTS.md](AGENTS.md) governs work inside this repo — per-skill layout, the maintainer
workflow, authoring conventions, bucket README discipline, the de-personalization gate. Read it
before changing anything. This file does not repeat it, and neither file should grow the
other's content.

## Fluency profile

The maintainer owns: which skills ship, which retire, what clears the evidence bar, and the
voice of anything public-facing.

Research and recommend on: wording, structure, verification approach, and whether a claim is
actually supported. Bring a recommendation and the reasoning behind it, not a menu.

## Question routing

Every question has a respondent, and the maintainer is the last rung, not the first. Their
attention is the scarcest resource in this repo, so reaching for it is a cost the question has
to earn. Route it before it gets there:

- **Checkable at source** — a file, a config value, a test, a commit, a label → go and check it.
- **A fact about a library, API, or framework** → the documentation, fetched now rather than
  recalled. Do not answer from memory about a platform that changes.
- **A domain or literature question** → research it properly and cite what you found.
- **A contestable value judgment** — is this synthesis sound, does this claim hold, is this
  review right → an independent reviewer, ideally one that did not produce the work. Grading
  your own homework is not review.
- **Needs a human who is not the maintainer** — an external expert, a domain specialist → put
  the question to them directly. The point is to move it *away* from the maintainer, not to
  open a second channel at them.

The maintainer's two rungs, and they are the whole list:

1. **A genuine values fork** — scope, priorities, risk tolerance, product direction. Surface it
   as a named, unanchored fork, never as a finished answer awaiting a signature.
2. **An action only they can physically perform** — merging a pull request, wiring a hook,
   an external login.

Everything else is yours to settle. Before surfacing any fork, try to kill it with evidence
first: if a competent reader holding the same files would derive one answer, it is arithmetic,
not a decision — assert it, note what would change your mind, and move on. A question you
answered with evidence beats a batched question, and a batched question at a natural boundary
beats three interruptions.

Two failure directions, both real. Routing a determinate question upward wastes the scarcest
reviewer. Deciding a genuine values call yourself takes a decision that was never yours. The
discriminator is whether the answer is derivable, not how confident you feel.

## Local gates

Every change is a branch, then a pull request, then the gates, then a merge the maintainer
fires. Three jobs run on a pull request:

- **de-personalization gate** — a fail-closed residue scan. It reports the file, line, and a
  generic replacement; it never rewrites for you. Run `pre-commit run --all-files` before
  pushing rather than discovering it in CI.
- **links** — every relative link and anchor is resolved. Moving or renaming a file means
  fixing every pointer to it in the same change.
- **tests** — the session-boundary validator suites, plus a poison control asserting that a
  stale packet is actually rejected.

A gate that cannot fail is not a gate. If you add one, show it going red before you trust it
green.

## Commits

`type(scope): description` — types `feat`, `fix`, `docs`, `chore`, `ci`. Scope is the skill
name for skill changes, or the surface for everything else (`readme`, `template`, `release`).
Every user-visible change needs a changeset (`npx changeset`); it generates the changelog entry
and the version bump.

## Scope and non-goals

**In scope:** the skills themselves, their evidence records, the published template, and the
public-facing surfaces that explain both.

**Out of scope here:** the measurement machinery that produces disposition verdicts, and the
research that derives the underlying framework. Both live in separate repos. Findings arrive
here as a change to a skill or its evidence record — not as methodology, which belongs where it
is built.
