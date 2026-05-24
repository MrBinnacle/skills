# CLAUDE.md — skills repo conventions

This repo is a collection of reusable agent skills. When you (Claude) are loaded with this repo as the working directory, follow these conventions.

## Repository layout

Skills are organized into bucket folders under `skills/`:

- `engineering/` — workflow disciplines for shipping software

Each bucket has a `README.md` listing every skill in that bucket with a one-line description, linking the skill name to its `SKILL.md`. Promote and demote skills by adding or removing them from the bucket README.

## Per-skill layout

Each skill is a directory containing `SKILL.md` (entry point) plus sibling files (aux disciplines, templates, gotchas, case studies). Layout is FLAT — no `references/` / `templates/` subdirectories unless the skill genuinely needs multiple distinct domains.

## Authoring conventions

- **Frontmatter** — `name:` + `description:` only. Description ≤ 200 chars. Triggers baked into the description sentence ("Use when X, Y, Z"). Add `disable-model-invocation: true` only when the skill is opt-in-only and should never auto-trigger.
- **Naming** — `UPPERCASE-NAMED.md` for documents/templates/formats (e.g., `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`). `lowercase-named.md` for concepts/aspects/principles (e.g., `transition.md`, `mocking.md`). `SKILL.md` is always uppercase.
- **Sizes** — `SKILL.md` 400 bytes to ~7 KB. Aux files 400 B to ~3 KB each. If `SKILL.md` is over 5 KB, split.
- **Cross-references** — inline at moment-of-need. No trailing "Related" / "See also" section.
- **`gotchas.md` is required** — append-only log of OBSERVED + ANTICIPATED failure modes. Seed with `[ANTICIPATED]` entries; replace or supplement with observed gotchas. Never delete entries — gotchas are stress-test signal, not failure evidence.
- **Discipline vs implementation** — make explicit in `SKILL.md` which parts of the skill are the stable contract vs. illustrative. Adopters need to know what they can swap.

## Bucket README discipline

Every bucket folder must have a `README.md` that lists every skill in the bucket, one line each, with the skill name linked to its `SKILL.md`.

## Top-level README

The top-level `README.md` must list every shipped skill under its bucket. Skills not in any bucket README are not shipped — move them to an `in-progress/` bucket or remove them.

## License

MIT. See `LICENSE`.
