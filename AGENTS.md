# AGENTS.md — skills repo conventions

This repo is a collection of reusable agent skills. When you (an agent — Claude or otherwise) are working with this repo as the working directory, follow these conventions. The root [`CLAUDE.md`](CLAUDE.md) is this repo's project delta — thin, repo-local, and safe to load as the rules of this clone, because that is what it is. The published template for adopters lives at [`templates/BASE-OPERATING-RULES.md`](templates/BASE-OPERATING-RULES.md) and describes no repo. This file carries the working conventions the delta deliberately does not repeat.

## Repository layout

Skills are organized into bucket folders under `skills/`:

- `engineering/` — workflow disciplines for shipping software
- `orchestration/` — disciplines for multi-agent work (dispatch, joinability, synthesis)
- `meta/` — skills about the skill system itself

Shipped skills progressively carry an `EVIDENCE.md` provenance record (origin incident,
validated-against, screen/paired result with UNMEASURED first-class, standing cost,
re-screen trigger). New promotions MUST include one; see top-level README → "The receipts, explained".

Each bucket has a `README.md` listing every skill in that bucket with a one-line description, linking the skill name to its `SKILL.md`. Promote and demote skills by adding or removing them from the bucket README.

Beyond `skills/`, the repo publishes the base-operating-rules template at `templates/BASE-OPERATING-RULES.md`, which adopters copy to their own `~/.claude/CLAUDE.md`. Three files, three jobs, and they must not absorb each other: the **template** is a starting point any project can adopt and describes no repo; the root **`CLAUDE.md`** is this repo's own thin delta, which also serves as the worked example the template points at; this **`AGENTS.md`** governs how an agent works *inside this repo*.

⚠ **Keep the template off any path that is loaded automatically.** A file named `CLAUDE.md` is picked up as the operating rules of the directory it sits in, so a template parked at the repo root hands every agent that opens this clone a set of rules that were never about this clone — with a prose disclaimer as the only correction. That is the layer-placement error this collection exists to catch, and the repo shipped it for several releases. If the template ever needs a different home, keep the new one equally unloadable.

⚠ **The template's numbered sections name no skill, and that is load-bearing — keep it that way when you edit them.** The file is copied wholesale into an adopter's `~/.claude/CLAUDE.md`, so a skill named inside a *rule* dangles for a reader who installed none of this collection — which is precisely what the template's own §14 tells them not to do ("list only what the reader can actually run"). Skill names belong below the horizontal rule, under **Companion skills in this repo**, where the heading scopes them. Neither this file nor the root delta has that constraint: both are copied nowhere, so naming a skill in either is fine.

## Per-skill layout

Each skill is a directory containing `SKILL.md` (entry point) plus sibling files (aux disciplines, templates, gotchas, case studies). Layout is FLAT — no `references/` / `templates/` subdirectories unless the skill genuinely needs multiple distinct domains.

## Source of truth & maintainer workflow

For the **published** skills in this repo, the repo — not any local install — is the source of
truth. Maintainers install the published skills as **symlinks back into a clone** so a `git pull`
updates every installed copy and local↔repo drift is structurally impossible:

- `scripts/link-skills.ps1` (Windows) iterates the skills in this repo and replaces each local
  install dir with a symlink into the clone. It is a maintainer dev tool, not the supported
  end-user installer (end users use `npx skills add`). It dry-runs by default and backs up any
  real dir it replaces; Windows symlinks need Developer Mode or an elevated shell.
- Private, unpublished skills in a maintainer's local library are never symlinked and never enter
  this repo. Only what lives here is linked.

**Every change is a branch → PR → gate → merge:**

1. Branch from `main`. Edit the skill *in the clone* (the clone is the source of truth).
2. Open a PR. CI runs the **de-personalization gate** (residue scan, fail-closed) and the **link
   check**. A PR that trips the residue gate is told the file, line, and generic replacement.
3. Add a **changeset** (`npx changeset`) describing the change — this generates the changelog
   entry and the version bump.
4. Merge to `main`. Cutting a release is a **manual** step (no auto-release CI): run
   `npm run version` to roll pending changesets into a version bump + `CHANGELOG.md` update,
   commit it, and tag by hand if wanted.

**Promotion of a new skill** (private → published):

1. Author and prove the skill privately. It must pass the [admission policy](ADMISSION.md) and
   clear the collection's transformative-value bar — would a current frontier model still get
   this wrong without it? — before it is eligible.
2. Copy it into the correct bucket, **de-personalize** (the gate blocks residue), flatten to the
   per-skill flat layout, and add `EVIDENCE.md` + `gotchas.md`.
3. PR → gate → merge (with a changeset).
4. **Then** replace the maintainer's local real dir with a symlink to the repo copy
   (`link-skills.ps1`), so from that point the published skill has exactly one copy and cannot
   drift.

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
top-level README; update every scoreboard site that asserts the kept/retired/turned-away
counts so they match the repository after the removal; add a row + a short narrative to
`RETIRED.md` with the cause stated plainly; and link the evidence at the **last release tag**
(`blob/<tag>/…`) so "record intact" survives the file's removal. If a general lesson outlives
the skill, name it in the retirement note as ordinary hygiene rather than resurrecting the
card.

The scoreboard is asserted in **five places across three files** — keep them in lockstep:

1. `assets/banner-light.svg` — `aria-label`
2. `assets/banner-light.svg` — rendered scoreboard `<text>`
3. `assets/banner-dark.svg` — `aria-label`
4. `assets/banner-dark.svg` — rendered scoreboard `<text>`
5. `README.md` — banner `<img alt>`

`scripts/validate_scoreboard.py` (run in the `validator` job) derives kept / retired /
turned-away from the skill directories and `RETIRED.md` and refuses a partial edit. A miss
turns the build red; do not treat any single prose line as the checklist. The front-page
slogan ("N cards, not N hundred") is rhetoric, not a scoreboard site — update it only if the
voice still fits.

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
