<!--
Thanks for contributing. This collection stays small on purpose — every skill taxes
context in every conversation, whether or not it fires. The checklist mirrors
CONTRIBUTING.md; if this PR isn't a new skill (docs, fix, tooling), delete the skill
section and keep the rest.
-->

## What this changes

<!-- One or two sentences. If it's a new skill, name the specific failure it answers. -->

## Which failure does it answer?

<!-- The real incident or recurring failure mode behind this change. Link an EVIDENCE.md
     entry or describe the origin plainly. "Seemed useful" is not a failure. -->

## Checklist

- [ ] It passes the [skill-necessity-gate](../skills/meta/skill-necessity-gate/SKILL.md) — this is a bet a pattern recurs, not a one-off convenience.
- [ ] `SKILL.md` stays lean; aux detail lives in sibling files (`gotchas.md`, references).
- [ ] Ships a `gotchas.md`, and — for any real-incident origin — an `EVIDENCE.md` with the dated story and honest **UNMEASURED** where nothing has been screened yet.
- [ ] Frontmatter is minimal: `name:` + `description:` (≤ 200 chars, quoted if it contains `: `).
- [ ] No private residue (paths, internal project names, session IDs) — the pre-commit gate will also check this.

## Anything the reviewer should push back on

<!-- Where are you least sure? Naming this makes the review better, not weaker. -->
