---
"mrbinnacle-skills": minor
---

Move the published operating-rules template off the repo root, and put a real project delta
there instead.

A file named `CLAUDE.md` is loaded automatically as the operating rules of the directory it
sits in. The file at this repo's root was the template published for adopters to copy — which
describes no repo and was never meant to govern this one. So every agent that opened this clone
loaded 384 lines of the wrong thing as its project instructions, with a paragraph of prose as
the only correction. `AGENTS.md` had already diagnosed this in words ("not a description of how
this repo operates"), but the placement that framing was built on never followed. This is a
layer-placement error of exactly the kind the collection exists to catch, shipped at the root of
the collection.

- The template moves to `templates/BASE-OPERATING-RULES.md`. It is unchanged as doctrine; its
  header now explains why it is not filed as a `CLAUDE.md`, and it becomes one when you copy it
  to `~/.claude/CLAUDE.md`.
- The root `CLAUDE.md` is now this repo's genuine project delta — what actually governs work in
  this clone. It is thin on purpose and points at `AGENTS.md` for the working conventions rather
  than restating them.
- That delta also serves as the worked example the template refers to. The template previously
  offered an empty stub and a parenthetical list of what might go in one; a real delta is a
  better answer than a placeholder, and cannot drift out of date without someone noticing,
  because it is the file the repo runs on.
- Its **Question routing** section is the part most worth copying: every question has a
  respondent, the human is the last rung rather than the first, and a fork that evidence can
  settle is not a fork.

An earlier change (#7) moved the template *to* the root on the grounds that it was "the repo's
real `CLAUDE.md`", and removed `templates/` because a duplicate copy-target would reintroduce
drift. The first premise is what `AGENTS.md` later corrected. The second concern does not apply
here: there is still exactly one copy of the template, and the root file is now different
content doing a different job.

`README.md`, `AGENTS.md`, and the `.pre-commit-config.yaml` comment are updated to match, and
`AGENTS.md` picks up the constraint as a convention so the template cannot quietly drift back
onto a loaded path.
