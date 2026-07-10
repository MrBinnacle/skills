# skills

**Confidence is not evidence.**

Most agent failures at the judgment layer are not reasoning failures or missing
context. They are verification failures: the agent's confidence stood in for a
check that never happened. These are composable disciplines that put the check
back in the loop — verify before asserting, separate a decision from its
ratification, distrust an instrument that disagrees with itself, log each failure
mode so the next run does not relearn it.

Documentation and context frameworks keep an agent oriented to where the work
goes. These skills govern whether its judgment can be trusted to get there:
orchestration, decision quality, and engineering rhythm, each a standalone
discipline you can drop into Claude Code or any compatible runtime.

Every skill carries its own append-only `gotchas.md`: the observed and
anticipated failure modes that produced the discipline.

Authored by [Matthew Gruber](https://github.com/MrBinnacle). Layout inspired by
[github.com/mattpocock/skills](https://github.com/mattpocock/skills).

## Available skills

### Engineering — workflow disciplines for shipping software

- [**closure-mode-at-boundaries**](skills/engineering/closure-mode-at-boundaries/SKILL.md) — codifies the closure→build transition at sprint/phase boundaries. Dispatch a parallel SME swarm, then execute the swarm's action list before presenting a revised frame. Prevents the failure mode of forwarding multi-voice menus instead of executed verifications.
- [**git-pull-rebase-trap**](skills/engineering/git-pull-rebase-trap/SKILL.md) — `git pull --no-ff` is silently ignored when `pull.rebase=true`: the rebase proceeds and rewrites every local SHA. Pre-flight config check, explicit fetch+merge alternative, SHA-backfill recovery. Born from an observed 22-commit rewrite incident — [evidence record](skills/engineering/git-pull-rebase-trap/EVIDENCE.md).

### Orchestration — disciplines for multi-agent work

- [**parallel-review-disposition-schema**](skills/orchestration/parallel-review-disposition-schema/SKILL.md) — dispatch discipline for 3+ parallel agents adjudicating a shared finding-set: fixed decision-vocabulary enum, shared per-item output block, explicit item ownership, mandatory status line — so isolated outputs JOIN at synthesis instead of returning N strong reviews that don't compose. Two documented instantiations — [evidence record](skills/orchestration/parallel-review-disposition-schema/EVIDENCE.md).

### Meta — skills about the skill system itself

- [**skill-necessity-gate**](skills/meta/skill-necessity-gate/SKILL.md) — six-gate procedure deciding whether a proposed capability should become a skill (most shouldn't). Layer triage → recurrence → measured worth → invocation topology → statefulness → low-cost shape, plus library-audit and absence-detection modes. Grounded in Matt Pocock's methodology triangulated against Anthropic's official skill docs; includes the reflexive rule that eval harnesses and other instruments run the same gates before being built.

## Evidence records

*Confidence is not evidence* applies to this collection itself. Skills here are
progressively moving to carrying an `EVIDENCE.md` — a provenance record stating, per
skill: the dated **observed origin failure** (or "conviction; no observed origin",
stated plainly) · what it has been **validated against** · its **screen / paired-eval
result**, with **UNMEASURED as a first-class value** rather than a gap to hide · its
**standing context cost** · and a named **re-screen trigger**.

The re-screen rule is the part most collections lack: frontier models improve, and a
trap skill is only valid against models that still fall into the trap. Major model
releases trigger a cheap re-screen; a skill the new model no longer needs gets publicly
**retired with its evidence record updated** — model progress becomes collection
history, not silent rot. Methodology (paired Full-vs-Null evaluation, admissibility,
the ceiling problem) lives in the companion repo:
[skill-harness](https://github.com/MrBinnacle/skill-harness) — see its registered
[v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md)
for why naive "the skill scored 1.0" benchmarks mislead, and the
[double-ceiling case study](https://github.com/MrBinnacle/skill-harness/blob/main/docs/case-studies/double-ceiling-structurally-unmeasured.md)
for why these evidence records treat UNMEASURED as a result, not a failure:
a frontier agent passed 14/14 no-skill epochs on two deliberately-hardened
synthetic tasks — on that task class there is nothing for a skill to improve,
and any benchmark claiming otherwise owes you its Null-arm pass rate first.

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
  meta/                         ← skills about the skill system itself
    README.md                     bucket index
    skill-necessity-gate/
      SKILL.md                    entry point — the six gates
      governing-dynamics.md       the evidence behind each gate (GD-1…11)
      absence-detection.md        library-audit + missing-skill modes
      loops-and-autonomy.md       GD-10 supplement for autonomous loops
      gotchas.md                  append-only failure-mode log
  in-progress/                  ← unshipped skills; not listed under Available skills
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
