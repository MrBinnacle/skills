# AGENTS.md — skills repo conventions

This repo is a collection of reusable agent skills. When you (an agent — Claude or otherwise) are working with this repo as the working directory, follow these conventions. The root [`CLAUDE.md`](CLAUDE.md) is this repo's project delta — thin, repo-local, and safe to load as the rules of this clone, because that is what it is. The published template for adopters lives at [`templates/BASE-OPERATING-RULES.md`](templates/BASE-OPERATING-RULES.md) and describes no repo. This file carries the working conventions the delta deliberately does not repeat.

## Repository layout

Skills are organized into bucket folders under `skills/`:

- `engineering/` — workflow disciplines for shipping software
- `orchestration/` — disciplines for multi-agent work (dispatch, joinability, synthesis)
- `meta/` — skills about the skill system itself

Shipped skills carry an `EVIDENCE.md` provenance record (origin incident, occasions counted,
validated-against, screen/paired result with UNMEASURED first-class, standing cost,
re-screen trigger). New promotions MUST include one; see top-level README → "The receipts, explained".
Two of those rows are contract rather than convention — `Occasions counted` and
`Re-screen trigger` — and `scripts/validate_card_files.py` refuses a published card that
does not state both; see "Recording a new occurrence" below.

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

## Vocabulary of record

`CONTEXT.md` at the repo root fixes what each governed term means; use its terms and respect
its Avoid-notes on every surface. Which words may appear in public *asset* copy is the
narrower `assets/tokens.json` question. When code or a validator disagrees with the glossary,
the enforced artifact is the primary source — fix the glossary.

## Bucket README discipline

Every bucket folder must have a `README.md` that lists every skill in the bucket, one line each, with the skill name linked to its `SKILL.md`.

## Top-level README

The top-level `README.md` must list every shipped skill under its bucket. Skills not in any bucket README are not shipped — move them to an `in-progress/` bucket or remove them.

## Recording a new occurrence

Recurrence accrues in the ordinary course of work, not in a special counting session. The
systemic gap the S295 triage found
([`dispositions/2026-08-15-S295-admission-triage.md`](dispositions/2026-08-15-S295-admission-triage.md))
was not that these cards lack incidents — it was that incidents get recorded once and
recurrence is never counted. When a card's problem happens again:

1. **Record it where it happened first.** Append a dated entry to the card's `gotchas.md`
   (append-only), or to its case study / `SKILL.md` verification section — wherever the
   occurrence actually belongs. The dated entry is the evidence; the count is only a reading
   of it.
2. **Then count it.** Add the dated reference to the card's `Occasions counted` row and
   increment the integer that opens the row. `scripts/validate_card_files.py` requires that
   integer to equal the number of dates in the row, and requires each of those dates to appear
   elsewhere in the card's own files — so a count cannot rise without the record that justifies
   it. The row's dated references *are* its occasions: a dated link to anything else (a triage
   record, a release) does not belong in that row.
3. **Fan-out is not recurrence.** Two symptoms of one task, a design session, and a fixture
   proving a validator rejects something are one occasion or none — ADMISSION.md criterion 2's
   own words: "not inflated by fan-out from a single run."
4. **The label tracks the count in both directions.** Under two counted occasions the card
   states `RECURRENCE-THIN` in its `EVIDENCE.md`; at two it comes off, because a stale honesty
   label is its own kind of dishonest. The check matches the token, so removing the token is
   the whole edit — a card that argues about the label in prose keeps tripping it.
5. **Dated disposition records are snapshots and are not rewritten.** A card that later earns
   its way out of the thin tier says so in its own file and in the changeset; the triage record
   that found it thin keeps saying what it found on the day it ran.

## Retirement

Retirement is a first-class event, not an afterthought — the collection's credibility comes
from shrinking honestly. A skill leaves two ways:

- **Screen null** — a newer model passes the skill's task with-and-without at the ceiling
  (skill-harness); nothing is left for the skill to improve.
- **Pre-registered platform-fix** — the skill's `EVIDENCE.md` re-screen trigger names a
  specific platform change that would make the underlying failure impossible; when that change
  ships, the skill retires against its own stated criterion, no screen required.

Execute a retirement as: remove the skill directory; drop it from its bucket README and the
top-level README; add a row + a short narrative to
`RETIRED.md` with the cause stated plainly; and link the evidence at the **last release tag**
(`blob/<tag>/…`) so "record intact" survives the file's removal. If a general lesson outlives
the skill, name it in the retirement note as ordinary hygiene rather than resurrecting the
card.

The banner no longer states counts (owner ruling 2026-08-23, skill-harness #216: a static
graphic that must track repository state is a maintenance tax). Instead it carries one ruled
line, asserted **byte-identically in five places across three files** — keep them in lockstep:

1. `assets/banner-light.svg` — `aria-label`
2. `assets/banner-light.svg` — rendered banner-line `<text>`
3. `assets/banner-dark.svg` — `aria-label`
4. `assets/banner-dark.svg` — rendered banner-line `<text>`
5. `README.md` — banner `<img alt>`

The ruled line is `These aren't the Claude Code skills you're looking for.` — a site may
prefix it (the aria-label and alt lead with `skills — `) but not alter a byte of it, so a
softened restatement ("are not", a dropped period, a straightened apostrophe) fails.

`scripts/validate_scoreboard.py` (run in the `validator` job) asserts that line, and still
derives the inventory counts from the records as a conformance check even though no page
site states them: **admitted** from the skill directories, **retired** and **solutions
looking for a problem** from `RETIRED.md`, and **measured** from each card's own `EVIDENCE.md`
controlled fields — a card counts as measured when `Screen result` or `Paired verdict` states
anything other than `UNMEASURED`. A card with no `EVIDENCE.md`, or with a controlled field
missing, is refused rather than counted as unmeasured: deriving a zero from an absent record
invents the number the derivation exists to keep honest. The derived counts appear in the
PASS line, which is where to read the inventory state from.

The same script also derives the front page's **origin tiering** from each card's `EVIDENCE.md`
`Origin` field, over a closed vocabulary of `OBSERVED` (a dated real incident), `DESIGNED` (built
on purpose) and `DISTILLED` (written from research, no triggering incident). `README.md` states
that tiering in two places — "Where these came from" and "What the receipts are worth" — and both
must state all three numbers on one line, in that order. An Origin field opening with a word
outside the vocabulary is refused rather than guessed at, on the same rule as the controlled
fields: a card that has not said which tier it is cannot be counted into either.

A miss turns the build red; do not treat any single prose line as the checklist. The front-page
slogan ("N cards, not N hundred") is rhetoric, not a validator site — update it only if the
voice still fits.

## The rotation and harvest pass

When the maintainer asks for a rotation, hygiene, weeding, or TLC pass over this collection,
this section is the procedure. It is written so a cold session can run the whole pass from
this repository plus two maintainer-supplied evidence locations — session records and usage
telemetry. The maintainer's private trigger skill only names those locations and points here;
if a cold session cannot run the pass from this section, the defect is in this section.

**Harvest first, tidying second.** Evidence accrues across every project the maintainer
works, faster than anyone collects it. The pass collects it, reconciles what it changes, and
adjudicates what it licenses. "Less" is the bar, not a number: admission stays
default-refuse, the count is whatever survives, and movement in both directions is the
mechanism working. An evolving ecosystem, not a chop list.

### Inputs, and which are authoritative

| Source | Authority |
|---|---|
| Published cards (`EVIDENCE.md`, `gotchas.md`) | Authoritative — the record of what a card is worth. |
| `README.md` per-card table; scoreboard-derived counts | Derived. Reconciled, never authored independently. |
| Usage telemetry (maintainer-supplied) | Authoritative for invocation counts. Silent on efficacy. |
| Session records (maintainer-supplied) | Authoritative for occasions — the cheapest evidence in the system. |
| External planning notes | Never canonical. Hypotheses, each checked against this repo. |

### The pass

1. **Mine recurrence.** Read every published `EVIDENCE.md`; note `Occasions counted`,
   `Screen result`, and any `RECURRENCE-THIN`. For each thin card, search the session
   records for a second independent occurrence of the card's origin failure, and land any
   find per "Recording a new occurrence" above — the dated entry first, then the count.
   Done when every thin card has been searched and every found occasion is recorded.
2. **Scan the usage signal.** Report per-card invocation baseline, latest, and delta from
   the telemetry. Registry practice (Homebrew's 90-day install floor, Debian's
   cruft-report, npm's download floor) separates the mechanical scan that surfaces
   candidates from the criteria that decide them; this step is that scan. A card absent
   from the log entirely is a discriminator candidate: search the records for occasions
   where the card's trap occurred and the card did not fire. Found → retrieval defect (the
   description never matches how the situation gets phrased; fix the description). None
   found → insurance (the trap never came up; consistent with `CANT_TELL_YET`). Invocation
   is retrieval evidence, never an occasion count. Done when every published card has a row
   and every never-fired card carries a diagnosis or a dated "discriminator unrun".
3. **Reconcile, then validate.** Propagate each count or label change to every derived
   surface, walking the consequence chain before the edit — a one-integer change
   legitimately breaks several pins at once, and each break is the guard working: fix the
   surface, keep the pin. Then run the gate set with `PYTHONUTF8=1`:
   `scripts/validate_card_files.py`, `scripts/validate_scoreboard.py`,
   `scripts/test_validate_card_files.py`, `scripts/test_readme_admission_lead.py` — and
   `scripts/test_validate_conformance.py` plus `scripts/validate_conformance.py --root .`
   (the scheduled job's own pair) when the pass touched governance surfaces. Done when all
   pass AND a re-run of the whole pass with no new evidence would produce zero diff: the
   pass re-derives from current records every time, keeps no incremental state, and is safe
   to run twice.
4. **Adjudicate.** New candidates enter through the [admission policy](ADMISSION.md),
   answered via the gate card; retirement candidates leave through "Retirement" above.
   `_quarantine/` promotion is `git mv`, so the card carries its history. Open a
   candidate's `PROVENANCE.md` before diagnosing drift or duplication — one candidate is a
   staged patch to an already-promoted card, and it has been misread as version drift once
   already. Done when every surfaced candidate carries a disposition or a dated deferral.
5. **Ship.** Branch → PR with a changeset; merge is the maintainer's. The PR body reports
   every disposition, flattering or not.

### Hard stops, from the first executed pass (2026-08-23)

- **A passing acceptance test is not a screen result.** The screen vocabulary is closed —
  `UNMEASURED`, `KEEP`, `CUT`, `CANT_TELL_YET` — and `validate_scoreboard.py` refuses a
  fifth term. A screen is a with-and-without comparison; an acceptance run exercised only
  the with. Evidence with no slot goes in another field, deliberately — extending the
  vocabulary is a policy edit, never a side effect of recording.
- **Relative links move.** A card's links resolve differently in `_quarantine/` and the
  published tree; re-check them on any move between trees.
- **The de-personalization gate fires on raw incident notes.** That is the gate working:
  de-personalize the entry, keep the evidentiary story, never exempt the file.

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

## Prose voice — literal-humanist register

Default register for every substantive prose artifact in this repo: README, docs, skill
cards' prose surfaces, ADRs, issues, pull requests, release notes, review comments, commit
bodies. It does not restyle source code.

For substantive prose:

1. State what happened — dates, amounts, versions, quoted terms.
2. Name the mechanism — translate each label into the action it performs.
3. State the consequence and its allocation — who gained, who paid.
4. State the finding. Never leave the operative conclusion for the reader to infer.
5. Attach uncertainty only to the proposition that is actually uncertain.
6. End with the next action, test, or decision.

Syntax: short sentences, concrete nouns, direct verbs, active voice, one step per
sentence. Never: euphemism after the underlying action is known; "perhaps",
"possibly", or "arguably" as cushioning for a supported claim; "readers may
conclude"; sarcasm or victory laps; passive voice that hides the responsible
component; abstractions that erase the person affected.

## License

MIT. See `LICENSE`.
