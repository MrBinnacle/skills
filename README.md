# Skills

Reusable agent skills for Claude Code and compatible runtimes. Each skill is a focused workflow discipline that adds itself to your agent's tool surface and triggers on the situations it fits.

Authored by [Matthew Gruber](https://github.com/MrBinnacle). Repo layout inspired by [github.com/mattpocock/skills](https://github.com/mattpocock/skills).

## Available skills

### Engineering — workflow disciplines for shipping software

- [**closure-mode-at-boundaries**](skills/engineering/closure-mode-at-boundaries/SKILL.md) — codifies the closure→build transition at sprint/phase boundaries. Dispatch a parallel SME swarm, then execute the swarm's action list before presenting a revised frame. Prevents the failure mode of forwarding multi-voice menus instead of executed verifications.
- [**azimuth**](skills/engineering/azimuth/README.md) — *placeholder; added separately.*

## Install

### Claude Code

Each skill is a directory containing `SKILL.md` + sibling files. Claude Code discovers skills by directory name; the `SKILL.md` frontmatter `description:` field drives auto-invocation.

**Option 1 — clone the whole collection:**

```bash
git clone https://github.com/MrBinnacle/skills.git ~/.claude/skills/mr-skills
```

Then symlink the skill directories you want into your skills root:

```bash
ln -s ~/.claude/skills/mr-skills/skills/engineering/closure-mode-at-boundaries \
      ~/.claude/skills/closure-mode-at-boundaries
```

**Option 2 — copy individual skill directories:**

```bash
git clone https://github.com/MrBinnacle/skills.git /tmp/mr-skills
cp -r /tmp/mr-skills/skills/engineering/closure-mode-at-boundaries \
      ~/.claude/skills/
```

### Other Claude-compatible runtimes

Each skill's `SKILL.md` uses the [Anthropic Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) frontmatter convention (`name:` + `description:`). Runtimes that follow the same convention should discover the skills with their native mechanism. Per-skill `prerequisites.md` files list required runtime capabilities (parallel dispatch, ≥2 subagents, etc.).

## Repository layout

```
skills/
  engineering/                  ← workflow disciplines for shipping software
    README.md                     bucket index
    closure-mode-at-boundaries/
      SKILL.md                    entry point
      swarm-composition.md        roster + role-to-runtime mapping
      transition.md               5-step closure→build discipline
      case-study.md               worked example
      formalization.md            wire into your lock-skill terminal step
      prerequisites.md            runtime + project surface requirements
      prompt-templates.md         copy-pasteable per-role prompts
      gotchas.md                  append-only failure-mode log
    azimuth/
      README.md                   placeholder
```

## Authoring conventions

If you want to contribute or adapt:

1. **Frontmatter is minimal** — `name:` + `description:` only. Description ≤ 200 chars. Triggers baked into the description sentence ("Use when X, Y, Z").
2. **Naming convention** — `UPPERCASE-NAMED.md` for documents / templates / formats. `lowercase-named.md` for concepts / aspects / principles. `SKILL.md` is always uppercase.
3. **Sizes** — `SKILL.md` 400 B to ~7 KB. Aux files 400 B to ~3 KB each. If `SKILL.md` is over 5 KB, you are probably bundling too much — split into sibling aux files.
4. **Cross-references** — inline at moment-of-need. No trailing "Related" / "See also" section.
5. **Every skill ships `gotchas.md`** — append-only log of OBSERVED + ANTICIPATED failure modes. Never delete entries.
6. **Discipline vs implementation** — make explicit which parts of the skill are the stable contract (the discipline) vs. illustrative (specific subagent IDs, paths, project names). Adopters need to know what they can swap.

## Contributing

Issues and PRs welcome. Each skill is independently versioned via the repo's git history. New skills:

1. Pick the appropriate bucket directory (or propose a new one).
2. Add the skill directory under the bucket.
3. Update the bucket's `README.md` to list the skill with a one-line description linking to its `SKILL.md`.
4. Update the top-level `README.md` to list the skill under its bucket.

## License

MIT — see [LICENSE](LICENSE).
