---
name: Propose a skill
about: New skills run the gauntlet — most ideas correctly fail it, and that's the system working.
title: "Proposal: <skill-name>"
labels: proposal
---

## The situation the skill fires in

<!-- One paragraph. What specific moment does this skill exist for? -->

## The incident behind it

<!-- The dated, real failure that justified it — what an agent actually got wrong.
     "Conviction, no observed origin" is an acceptable answer, stated plainly;
     it just means the EVIDENCE.md will say so. -->

## The gauntlet (be honest — most ideas fail here)

- [ ] I ran it against the [admission policy](../../ADMISSION.md) and it passed
- [ ] A current frontier model, given the situation WITHOUT the skill, plausibly still fails (if the model already does this unaided, the skill is a no-op — see [RETIRED.md](../../RETIRED.md) for four of the author's own candidates that died exactly here)
- [ ] It's a skill, not a hook/project-rule/one-off (the admission policy's layer question)

## What ships with it

- [ ] `SKILL.md` — lean, minimal frontmatter (`name` + `description` ≤ 200 chars, quoted if it contains `: `)
- [ ] `gotchas.md` — append-only failure log, seeded
- [ ] `EVIDENCE.md` — dated origin (or "conviction; no observed origin" stated plainly)
