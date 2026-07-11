# Contributing

Issues and PRs welcome. The bar is deliberately high — most skill ideas correctly fail it,
and that's the system working, not gatekeeping for its own sake.

## Proposing a skill

Use the [Propose a skill](https://github.com/MrBinnacle/skills/issues/new?template=propose-a-skill.md)
issue template. The short version of the gauntlet:

1. **It must pass the [skill-necessity-gate](skills/meta/skill-necessity-gate/SKILL.md).**
   Six questions deciding whether the capability belongs in a skill, in project rules, in a
   hook — or nowhere.
2. **A current frontier model, without the skill, should plausibly still fail the situation.**
   If the model already handles it unaided, the skill is a no-op — four of the author's own
   candidates died exactly here ([RETIRED.md](RETIRED.md)), so yours failing is good company.
3. **It ships complete:** `SKILL.md` (lean; frontmatter is `name` + `description` ≤ 200 chars,
   quoted if it contains `: `), `gotchas.md` (append-only failure log, seeded), and
   `EVIDENCE.md` — the dated real incident behind it, or "conviction; no observed origin"
   stated plainly. Honest UNMEASURED fields are expected; invented scores are rejected.

## Reporting a gotcha

A skill misfired or bit you in a way its `gotchas.md` doesn't cover? Use the
[Report a gotcha](https://github.com/MrBinnacle/skills/issues/new?template=report-a-gotcha.md)
template. Dated, quoted observations become append-only `gotchas.md` entries, credited.

## House rules

- **No private residue.** CI runs a fail-closed de-personalization gate over every `.md`
  (see [CLAUDE.md](CLAUDE.md)). If it blocks your PR, it names the fix.
- **Plain language.** Every file should read cleanly to someone who has never seen this
  repo. Jargon needs a definition at first use or it doesn't ship.
- **Security concerns** go through [SECURITY.md](SECURITY.md), not the issue tracker.
