# CLAUDE.md — skills repo conventions

This repo is a collection of reusable agent skills. When you (Claude) are loaded with this repo as the working directory, follow these conventions.

## Repository layout

Skills are organized into bucket folders under `skills/`:

- `engineering/` — workflow disciplines for shipping software
- `orchestration/` — disciplines for multi-agent work (dispatch, joinability, synthesis)
- `meta/` — skills about the skill system itself

Shipped skills progressively carry an `EVIDENCE.md` provenance record (origin incident,
validated-against, screen/paired result with UNMEASURED first-class, standing cost,
re-screen trigger). New promotions MUST include one; see top-level README → "Evidence records".

Each bucket has a `README.md` listing every skill in that bucket with a one-line description, linking the skill name to its `SKILL.md`. Promote and demote skills by adding or removing them from the bucket README.

## Per-skill layout

Each skill is a directory containing `SKILL.md` (entry point) plus sibling files (aux disciplines, templates, gotchas, case studies). Layout is FLAT — no `references/` / `templates/` subdirectories unless the skill genuinely needs multiple distinct domains.

## Authoring conventions

- **Frontmatter** — `name:` + `description:` only. Description ≤ 200 chars, written as a *router* ("Use when X, Y, Z") not a summary. Topology (`disable-model-invocation`) is set per the rule below.
- **Topology is a choice, not a default** — decide per skill: model-invocable (a *background reference* safe to auto-pull) vs **procedure** (`disable-model-invocation: true`, human-invoked, zero standing cost). A skill that *dictates strategic work* — planning, what/how, an orchestration swarm, a decision the human should own — is a procedure, not an auto-firing ability. Default to model-invocable only for background references; when unsure, run `skill-necessity-gate` Gate 3.
- **A discipline you *require* to fire cannot live only in the skill layer.** Both topologies rely on model-pull to fire — a model-invocable skill on retrieval, a procedure on the human remembering to invoke it — and model-pull is unreliable. In a proactive/`/loop` context it is not merely unreliable but *absent*: with the human turn removed, retrieval probability goes to zero, a `disable-model-invocation` procedure arrives as inert plain text, and a prompt-triggered nudge never fires — only a **PreToolUse/PostToolUse hook**, which fires on the tool call itself, still runs. So if an adopter *depends on* a discipline firing, back it with a deterministic hook (a UserPromptSubmit nudge that surfaces the skill, or a PreToolUse block) **in their own environment**; the published skill stays the model-invocable reference. Ask "does this discipline survive the loop?" — if its firing depends on retrieval or on a prompt arriving, it needs a hook, not just a skill.
- **Naming** — `UPPERCASE-NAMED.md` for documents/templates/formats (e.g., `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`). `lowercase-named.md` for concepts/aspects/principles (e.g., `transition.md`, `mocking.md`). `SKILL.md` is always uppercase.
- **Sizes** — `SKILL.md` 400 bytes to ~7 KB. Aux files 400 B to ~3 KB each. If `SKILL.md` is over 5 KB, split.
- **Cross-references** — inline at moment-of-need. No trailing "Related" / "See also" section.
- **`gotchas.md` is required** — append-only log of OBSERVED + ANTICIPATED failure modes. Seed with `[ANTICIPATED]` entries; replace or supplement with observed gotchas. Never delete entries — gotchas are stress-test signal, not failure evidence.
- **Discipline vs implementation** — make explicit in `SKILL.md` which parts of the skill are the stable contract vs. illustrative. Adopters need to know what they can swap.
- **Factual claims are dated and checkable — verify them before shipping AND before correcting.** A skill that asserts platform behavior (a flag, a hook payload, an API) rots when the platform changes. Verify against live docs or an empirical repro before you ship a claim, and again before you "fix" one — a wrong correction to an evidence-first repo is worse than the original error. Record the check (version, date) where it's load-bearing.

## Bucket README discipline

Every bucket folder must have a `README.md` that lists every skill in the bucket, one line each, with the skill name linked to its `SKILL.md`.

## Top-level README

The top-level `README.md` must list every shipped skill under its bucket. Skills not in any bucket README are not shipped — move them to an `in-progress/` bucket or remove them.

## Retirement

Retirement is a first-class event, not an afterthought — the collection's credibility comes
from shrinking honestly. A skill leaves two ways:

- **Screen null** — a newer model passes the skill's task with-and-without at the ceiling
  (skill-harness); nothing is left for the skill to improve.
- **Pre-registered platform-fix** — the skill's `EVIDENCE.md` re-screen trigger names a
  specific platform change that would make the underlying failure impossible; when that change
  ships, the skill retires against its own stated criterion, no screen required.

Execute a retirement as: remove the skill directory; drop it from its bucket README and the
top-level README; decrement the count copy ("N skills, not N hundred"); add a row + a short
narrative to `RETIRED.md` with the cause stated plainly; and link the evidence at the **last
release tag** (`blob/<tag>/…`) so "record intact" survives the file's removal. If a general
lesson outlives the skill, name it in the retirement note as ordinary hygiene rather than
resurrecting the card.

## De-personalization gate

Skills are extracted from a private source tree that legitimately carries private-project
provenance — project codenames, ticket-style IDs, a private repo directory and link. None of
that may reach this public collection. A fail-closed pre-push check enforces the boundary:
`.pre-commit-config.yaml` runs regex hooks over every `*.md` and **refuses the commit/push**
if a known residue pattern appears, reporting the file, line, and the suggested generic
replacement (carried in the hook name).

It does **not** auto-rewrite — by design. A silent scrub would hide the source↔publish
divergence and paper over the root cause; the block forces a conscious de-personalization edit
so the decision stays audited. Keep the evidentiary story (e.g. "a personal production
project's phase-2 security-audit lock"); drop only the unverifiable private identifier.

- **Activate once per clone:** `pre-commit install --hook-type pre-commit --hook-type pre-push`
- **Full-tree sweep on demand:** `pre-commit run --all-files`
- **Maintainer name/email are deliberately NOT in the committed config** — publishing them in a
  public block-list would itself de-anonymize. Add them to a git-ignored local overlay if wanted.

## License

MIT. See `LICENSE`.
