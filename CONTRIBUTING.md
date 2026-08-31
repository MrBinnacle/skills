# Contributing

Issues and PRs welcome. The bar is deliberately high — most skill ideas correctly fail it,
and that's the system working, not gatekeeping for its own sake.

## Proposing a skill

Use the [Propose a skill](https://github.com/MrBinnacle/skills/issues/new?template=propose-a-skill.md)
issue template. The short version of the gauntlet:

1. **It must pass the [admission policy](ADMISSION.md).**
   Four questions deciding whether the capability belongs in a skill, in project rules, in a
   hook — or nowhere. The policy is the whole test: answer the four questions against your
   candidate and cite the evidence each one asks for.
2. **A current frontier model, without the skill, should plausibly still fail the situation.**
   If the model already handles it unaided, the skill is a no-op — four of the author's own
   candidates died exactly here ([RETIRED.md](RETIRED.md)), so yours failing is good company.
3. **It ships complete:** `SKILL.md` (lean; frontmatter is `name` + `description` ≤ 200 chars,
   quoted if it contains `: `), `gotchas.md` (append-only failure log, seeded), and
   `EVIDENCE.md` — the dated real incident behind it, or "conviction; no observed origin"
   stated plainly. Honest UNMEASURED fields are expected; invented scores are rejected.

## Opening a PR

- Branch from `main`; keep each PR to one skill or one coherent change.
- CI must pass: the de-personalization gate (no private residue in any `.md`) and the link check.
- Add a changeset: `npx changeset`, pick the bump, write a one-paragraph human-readable summary.
  The changeset file is committed with your PR and becomes the changelog entry when a maintainer
  cuts the next release (`npm run version` — a manual step, no auto-release CI).

## Prose style (Vale)

The collection lints its prose with [Vale](https://vale.sh) against the **Taste** style. The
rules are authored in the sibling measurement repository,
[skill-harness](https://github.com/MrBinnacle/skill-harness), and vendored here as a byte-equal
copy under `styles/Taste/`. Edit them there, not here — a local edit fails the digest check in
`styles/Taste/STYLE_SOURCE.json`, which exists so the two repositories cannot quietly come to
mean different things by "the Taste style".

Install the hooks once per clone:

```bash
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

Three hooks run:

| Hook | What it checks | Blocks? |
|---|---|---|
| `vale-style-config` | vendored digests, the generated rule, the marketing scope | **yes** |
| `vale-prose` | staged `.md` at error level | only on error rows |
| `vale-commit-msg` | your commit message at error level | only on error rows |

**Every Taste row currently ships at `warning`, so the last two are a deliberate no-op today.**
They are installed now so that promoting a row later is a level change rather than a new
integration. CI mirrors this split: the configuration check runs inside the required `validator`
job and blocks; the prose findings run in a separate `vale` job that reports and never gates.

Vale is not a Python dependency. If you do not have it installed the prose hooks print an
install hint and pass — CI installs the pinned version, so the check still happens there.

**One scope rule worth knowing before you widen anything.** The banned-marketing word list in
`assets/tokens.json` applies to public asset copy only — README *headings*, the SVG assets, and
the package description. Its own note states that those words appear in body prose and working
documentation on purpose. `scripts/validate_vale_style.py` fails the build if the rule is bound
anywhere else, and `scripts/validate_brand_kit.py` remains the gate for the surfaces Vale cannot
read.

## Reporting a gotcha

A skill misfired or bit you in a way its `gotchas.md` doesn't cover? Use the
[Report a gotcha](https://github.com/MrBinnacle/skills/issues/new?template=report-a-gotcha.md)
template. Dated, quoted observations become append-only `gotchas.md` entries, credited.

## House rules

- **No private residue.** CI runs a fail-closed de-personalization gate over every `.md`
  (see [AGENTS.md](AGENTS.md)). If it blocks your PR, it names the fix.
- **Plain language.** Every file should read cleanly to someone who has never seen this
  repo. Jargon needs a definition at first use or it doesn't ship.
- **Security concerns** go through [SECURITY.md](SECURITY.md), not the issue tracker.
