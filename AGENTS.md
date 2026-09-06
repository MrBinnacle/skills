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
Three of those rows are contract rather than convention — `Occasions counted`,
`Dispatches recorded` and `Re-screen trigger` — and `scripts/validate_card_files.py` refuses a
published card that does not state all three; see "Recording a new occurrence" below.

`Dispatches recorded` (added 2026-08-24) is the measured-demand row, and it is required so it
cannot be silently dropped. Its form is checked, not just its presence: the row opens with a
positive integer or with the exact phrase `No recorded dispatch`, and it carries a
`measured <YYYY-MM-DD>` clause. **A zero written as a numeral is refused.** Two cards fire
through hook mechanisms the platform's dispatch counter cannot observe, so their zero must read
as "no recorded dispatch" — a figure the counter cannot see must not be published as "unused".
A measured figure with no date cannot be judged stale, which is why the date clause is checked
separately from any other date in the row.

**A dispatch is not an occasion.** A dispatch counts one invocation of a card: demand
evidence, never recurrence, lift, or worth. Writing a dispatch count into the recurrence row is
the fan-out inflation ADMISSION.md criterion 2 refuses. The two rows answer different questions
and are checked separately.

Each bucket has a `README.md` listing every skill in that bucket with a one-line description, linking the skill name to its `SKILL.md`. Promote and demote skills by adding or removing them from the bucket README.

Beyond `skills/`, the repo publishes the base-operating-rules template at `templates/BASE-OPERATING-RULES.md`, which adopters copy to their own `~/.claude/CLAUDE.md`. Three files, three jobs, and they must not absorb each other: the **template** is a starting point any project can adopt and describes no repo; the root **`CLAUDE.md`** is this repo's own thin delta, which also serves as the worked example the template points at; this **`AGENTS.md`** governs how an agent works *inside this repo*.

**Keep the template off any path that is loaded automatically.** A file named `CLAUDE.md` is picked up as the operating rules of the directory it sits in, so a template parked at the repo root hands every agent that opens this clone a set of rules that were never about this clone — with a prose disclaimer as the only correction. That is the layer-placement error this collection exists to catch, and the repo shipped it for several releases. If the template ever needs a different home, keep the new one equally unloadable.

**The template's numbered sections name no skill, and that is deliberate — keep it that way when you edit them.** The file is copied wholesale into an adopter's `~/.claude/CLAUDE.md`, so a skill named inside a *rule* dangles for a reader who installed none of this collection — which is precisely what the template's own §14 tells them not to do ("list only what the reader can actually run"). Skill names belong below the horizontal rule, under **Companion skills in this repo**, where the heading scopes them. Neither this file nor the root delta has that constraint: both are copied nowhere, so naming a skill in either is fine.

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
4. The maintainer merges the version-bump pull request to `main`. The merge is the
   delivery event — changed cards reach installed users when a version bump merges to
   `main`, not when a tag is pushed. There is no auto-release CI: the maintainer runs
   `npm run version` to roll pending changesets into a version bump and a `CHANGELOG.md`
   update, then runs `python scripts/release_gate.py --write` to stamp every plugin
   version from `package.json` and report release fitness. The gate lists every stale
   surface in one run rather than failing at the first. Commit the result and merge
   only when the gate is green. Release immutability is enabled on this repository, and
   a tag name cannot be reused once spent, so a botched release spends a version number
   permanently and the gate blocks before the merge rather than reporting after it.
   [ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) records the decision and
   the narrow surface a version promises.

   **`npm run version` fails closed without a `GITHUB_TOKEN` in the environment.** The
   changelog generator is `@changesets/changelog-github`, which resolves pull-request and author
   links through the GitHub API, so a run with no token stops partway through a release rather
   than at its start. Nothing stated this until 2026-08-24 and the next person to cut a release
   discovered it mid-run. Export a token with `public_repo` scope before running it.

**Promotion of a new skill** (private → published):

1. Author and prove the skill privately. It must pass the [admission policy](ADMISSION.md) and
   clear the collection's transformative-value bar — would a current frontier model still get
   this wrong without it? — before it is eligible.
2. Copy it into the correct bucket, **de-personalize** (the gate blocks residue), flatten to the
   per-skill flat layout, and add `EVIDENCE.md` + `gotchas.md`.
2a. **Normalize the frontmatter, because `_quarantine/` and `skills/` do not use the same
   keys.** Rewrite the `description` to the published bar in the same pass: ≤ 200 characters,
   written as a router. Measured 2026-08-24, every one of the 22 candidates was over it, from 285
   to 1272 characters, while every published card sat between 123 and 200. **The 200 bar is
   now CHECKED — `validate_card_files.py` refuses a published card over it**, so a promotion that
   skips this step reds the build instead of shipping. It stopped being enforced by the edit on
   2026-08-24, after three of six promoted cards shipped over the bar at 210, 226 and 235 in a
   pass that did not run the authoring skill. The spec gate is not this check: it enforces the
   specification's own 1024 limit, which all three breaches were comfortably inside. Published cards carry `name` + `description`, plus `disable-model-invocation` where
   the topology rule above calls for it — nothing else. Candidates carry four different
   dialects: measured 2026-08-23, 12 of 22 held `author` / `version` / `date`, 6 held a
   `metadata: type:` block over an undeclared vocabulary (`pattern`, `trap`, `workaround`,
   `discipline`), 4 held neither. Strip the extras on promotion. **`validate_spec_conformance.py`
   now catches a leftover `author` / `date` / `version` on a PUBLISHED card** — that allowance is
   scoped to `_quarantine/` only, so a candidate promoted without step 2a reds the build. It does
   NOT catch a leftover `metadata:` block, which is spec-legal; for that key this step is still the
   whole enforcement.
3. PR → gate → merge (with a changeset).
4. **Then** replace the maintainer's local real dir with a symlink to the repo copy
   (`link-skills.ps1`), so from that point the published skill has exactly one copy and cannot
   drift.

## Authoring conventions

- **Frontmatter** — `name:` + `description:` only. Description ≤ 200 chars, written as a *router* ("Use when X, Y, Z") not a summary. Topology (`disable-model-invocation`) is set per the rule below.
- **Topology is a choice, not a default** — this one presumes a card is the right artifact at all; [Choosing the control surface](#choosing-the-control-surface) below settles that first. Decide per skill: model-invocable (a *background reference* safe to auto-pull) vs **procedure** (`disable-model-invocation: true`, human-invoked, zero standing cost). The deciding question is **who does the strategic thinking?** A skill that *dictates strategic work* — planning, what/how, an orchestration swarm, a decision the human should own — is a procedure, not an auto-firing ability, and so is any skill with **side effects**: deploy, commit, send. Default to model-invocable only for background references. When the call is close it is partly a values question rather than a purely technical one, so **surface the standing-cost maths and let the human choose**: a model-invocable description costs ~100 always-on tokens and competes in the skill-list budget (~1% of context, where the least-used descriptions are truncated and then dropped at scale), while a procedure costs zero standing tokens and spends the human's attention instead. Present both sides and ask; auto-deciding this one takes a choice that is not yours.
- **A discipline you *require* to fire cannot live only in the skill layer.** Both topologies rely on model-pull to fire — a model-invocable skill on retrieval, a procedure on the human remembering to invoke it — and model-pull is unreliable. In a proactive/`/loop` context it is not merely unreliable but *absent*: with the human turn removed, retrieval probability goes to zero, a `disable-model-invocation` procedure arrives as inert plain text, and a prompt-triggered nudge never fires — only a **PreToolUse/PostToolUse hook**, which fires on the tool call itself, still runs. So if an adopter *depends on* a discipline firing, back it with a deterministic hook (a UserPromptSubmit nudge that surfaces the skill, or a PreToolUse block) **in their own environment**; the published skill stays the model-invocable reference. Ask "does this discipline survive the loop?" — if its firing depends on retrieval or on a prompt arriving, it needs a hook, not just a skill.
- **Naming** — `UPPERCASE-NAMED.md` for documents/templates/formats (e.g., `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`). `lowercase-named.md` for concepts/aspects/principles (e.g., `transition.md`, `mocking.md`). `SKILL.md` is always uppercase.
- **Sizes** — `SKILL.md` 400 bytes to ~7 KB. Aux files 400 B to ~3 KB each. If `SKILL.md` is over 5 KB, split.
- **Open by saying what the card does, then show why it is worth having.** A reader who cannot tell what they get will not reach for the card, and a card nobody reaches for costs its description tokens and returns nothing. In the first 150 words of `SKILL.md`: what an agent running this card actually does and what comes back, then one concrete thing it caught. Show, do not assert — "improves code quality" is a claim about the card, "a loose test helper let a list match the string `"1"`" is a reason to install it. Take the example from the card's own evidence and state its limits in the same breath: *"one session, not a measured verdict"* is a stronger pitch than a confident generality, because a reader can check it. A card whose evidence is thin says so here rather than reaching for adjectives.
- **Write it plainly, for a tired reader.** Short sentences, ordinary words, one idea each. Prefer the common word to the formal one. Break up stacked abstractions: *"an auditable count of qualifying unaided occurrences"* is four nouns deep and means *"how many times this happened on its own"*. Put whoever acts at the front of the sentence. If a sentence must be read twice, split it. This governs every prose surface a person reads — `SKILL.md`, `EVIDENCE.md`, `gotchas.md`, `README.md`, and a disposition — and it does not license vagueness: every fact and every honest gap survives the simplification unchanged. You are changing how it reads, not what it says. [operator-lodged 2026-09-06] **Where this rule meets the append-only `gotchas.md` rule below, append-only wins: entries already written stay exactly as written, and this rule governs entries added from now on.** Read literally, "every prose surface" would order a rewrite of an immutable log, and the two rules cannot both be obeyed on an existing entry. A rewritten log entry is no longer the record of what was observed, which is the property the log exists for. Do not report a card's prose as compliant because a readable summary was added beside dense historical entries; say which surfaces were rewritten and which were left as history. [clarification 2026-09-06, entailed by the append-only rule below, not a new constraint]
- **Cross-references** — inline at moment-of-need. No trailing "Related" / "See also" section.
- **Invoking a skill from any agent-executed instruction** — write the exact phrase *"Call the Skill tool with `skill-name`."* (Pocock, verbatim, X, 2026-08-24). The phrase belongs everywhere an agent reads an instruction to reach for a skill: inside a card, in a slash command, in an `AGENTS.md` line, in a subagent dispatch. A bare "run X" or "use X" leaves the invocation to inference; naming the tool and its argument is what makes the call fire reliably. **Composing skills this way is endorsed practice** — a card needing a discipline another card already carries should delegate to it rather than restate it, which keeps one meaning in one place and keeps both cards inside the size bounds above.
- **`gotchas.md` is required** — append-only log of OBSERVED + ANTICIPATED failure modes. Seed with `[ANTICIPATED]` entries; replace or supplement with observed gotchas. Never delete entries — gotchas are stress-test signal, not failure evidence.
- **Discipline vs implementation** — make explicit in `SKILL.md` which parts of the skill are the stable contract vs. illustrative. Adopters need to know what they can swap.
- **Factual claims are dated and checkable — verify them before shipping AND before correcting.** A skill that asserts platform behavior (a flag, a hook payload, an API) rots when the platform changes. Verify against live docs or an empirical repro before you ship a claim, and again before you "fix" one — a wrong correction to an evidence-first repo is worse than the original error. Record the check (version, date) wherever the claim is relied on.

### Choosing the control surface

[`ADMISSION.md`](ADMISSION.md) criterion 3 asks whether a skill is the correct **control surface** for a failure. It lists what a skill is competing against and stops there, which is the right size for a policy and too small to decide with. This section is how that criterion gets answered. It is guidance for applying the policy, not an amendment to it — the four questions are unchanged and this text binds nothing they do not.

Answer it **before** the frontmatter question above. That one presumes a card; this one decides whether there should be one.

Return exactly one primary disposition:

| Disposition | The capability is |
|---|---|
| `STANDALONE_SKILL` | a reusable method owning its own trigger and terminal outcome |
| `PARENT_ORCHESTRATOR` | the owner of scope, sequencing, synthesis and the final write, recruiting specialists |
| `NESTED_SPECIALIST` | bounded advice or work supplied to a parent, with no independent write authority |
| `SHARED_PRIMITIVE` | a schema, interview or validator several skills consume, rarely invoked directly |
| `HOOK_ENFORCEMENT` | behaviour that must fire deterministically rather than on retrieval |
| `MCP_ACCESS` | external reach, state or tools; the method lives elsewhere |
| `PROJECT_RULE` | a constraint on one repository, belonging in its `CLAUDE.md` or equivalent |
| `PRP_OR_BUILD_ARTIFACT` | an execution packet for one build, discarded after it |
| `OUTPUT_STYLE` | a standing voice or register rather than a task method |
| `SCRIPT_OR_CHECK` | a deterministic operation needing no agent reasoning around it |
| `COMPOSITION_EDGE` | an invocation contract between capabilities that already exist |
| `NO_ARTIFACT` | ordinary model capability, a one-off instruction, or machinery with no case behind it |

The questions that discriminate them:

1. Does it own a distinct trigger **and** a terminal outcome? Missing either points away from `STANDALONE_SKILL`.
2. Is it a specialist an existing parent recruits, rather than something a user reaches for?
3. Must it fire deterministically, or does it merely benefit from retrieval? A discipline you depend on needs a hook; a card's firing rests on retrieval and a procedure's on the human remembering.
4. Is the missing element method, project context, access, enforcement, or temporary execution state? Each answer names a different row.
5. Can an existing skill consume it through a compact input and output contract? Then it is an edge, not an identity.
6. Which component owns writes, adjudication, failure handling and receipts?
7. What happens when it is unavailable? A capability with no graceful degradation is a dependency, and should say so.
8. What cycle, nesting-depth, latency and standing-cost risks does it add?

**A second identity for an existing trigger surface creates ambiguous routing.** When a capability shares another card's trigger, protected interfaces and repository identity, it is a version of that card or an edge into it. Two cards answering the same request is a routing defect that no evidence record fixes.

**This rubric decides layer. It does not decide worth, and it cannot admit anything.** Admission is [`ADMISSION.md`](ADMISSION.md)'s four questions on recorded evidence, and criterion 1 wants an observed failure. A capability can sort cleanly into `STANDALONE_SKILL` here and still be refused there for want of an occurrence — which is what happened to the card this rubric came from. Reaching a disposition is not progress toward admission.

**Do not cite this section, or any card, as evidence that its own output is right.** See [No self-authority](#no-self-authority) — the standing that makes an instrument feel authoritative is exactly what that rule refuses as proof.

## Where this repository diverges from the Agent Skills specification, on purpose

The published [Agent Skills specification](https://agentskills.io/specification) ships a
reference validator, `skills-ref`. CI runs it over both trees
(`scripts/validate_spec_conformance.py`). It is the only conformance instrument here that its
maintainer did not write, which is the entire reason for adopting it — every other gate can be
wrong in the same direction as the cards it grades.

**It rejected two published cards on its first run**, both for an unquoted YAML description
scalar containing a `: ` or a `{`. Claude Code's parser tolerates them; a spec-conformant reader
cannot load them. No gate here saw it because **no gate here reads frontmatter**. Quote any
description containing `:`, `{`, `[`, `#` or a leading `*`.

The conventions above predate the specification. Where they still differ, each difference is a
decision, recorded so it reads as a choice rather than as ignorance of the document:

| This repository | The specification | Why the difference stands |
|---|---|---|
| Frontmatter is `name` + `description` only, plus `disable-model-invocation` | also permits `license`, `compatibility`, `metadata`, `allowed-tools` | Narrower on purpose. The extra keys are legal and unused; adding them would widen the dialect spread step 2a exists to close. **`disable-model-invocation` goes the other way** — it is outside the spec vocabulary and is a real Claude Code key that changes behaviour: it is what stops a procedure card auto-firing. It stays, and the spec gate carries a named allowance for it. |
| `description` capped at 200 characters | permits 1024 | Stricter on purpose. An installed card's description is loaded at startup whether or not the card fires, so length is paid for by every session. |
| Flat per-skill layout | recommends `references/`, `scripts/`, `assets/` | A card here is small enough that a subdirectory adds a hop without adding structure. Revisit per skill if one genuinely needs multiple domains. |
| `evals/` per card | not in the specification | This repository's own convention, checked by `validate_eval_corpora.py`. It is an addition, not a divergence — nothing in the spec forbids it. |

**The `metadata:` blocks stripped from candidates on promotion are spec-LEGAL.** Step 2a is a
house rule narrowing the vocabulary, not a correction of a non-conforming card. Say it that way
when explaining the step.

**Tolerated divergences are printed on every run of the spec gate.** A silent allowance is a
silent gate, and the allowance list is scoped per tree: the published tree tolerates exactly one
error class, the candidate tree tolerates the three that promotion already closes. Anything else
fails, in either tree.

## Vocabulary of record

`CONTEXT.md` at the repo root fixes what each governed term means; use its terms and respect
its Avoid-notes on every surface. Which words may appear in public *asset* copy is the
narrower `assets/tokens.json` question. When code or a validator disagrees with the glossary,
the enforced artifact is the primary source — fix the glossary.

## Bucket README discipline

Every bucket folder must have a `README.md` that lists every skill in the bucket, one line each, with the skill name linked to its `SKILL.md`.

## Top-level README

The top-level `README.md` must list every shipped skill under its bucket. Skills not in any bucket README are not shipped — move them to an `in-progress/` bucket or remove them.

## The plugin manifest is the machine-readable source of truth

`.claude-plugin/marketplace.json` states what this collection ships, in the form Claude Code's own
plugin mechanism reads. It groups the published cards **one plugin per bucket** — `engineering`,
`orchestration`, `meta` — which makes the membership check a pure derivation from the tree with no
judgement in it. Any other grouping needs a hand-maintained card-to-plugin mapping, which is a
second census to keep in sync.

**Two surfaces, two jobs, and the tie-break is fixed.** The manifest is the machine-readable
statement; the bucket READMEs are the human-readable one. **Where they disagree, the manifest wins
and the README is reconciled to it** — the manifest is what an installer executes, so a README that
disagrees is a stale description of something already shipping.

`validate_conformance.py` obligation **O7** checks both directions on every run: a path the
manifest names with no card at it, and a published card no plugin names. One direction is not
enough, and this repository has the receipt — the occasions check ran forward-only and an
undercount stayed green until August 2026. **A promotion or a retirement edits the manifest in the
same commit as the `git mv`,** or O7 reds the pull request.

**Do not hand-type the `skills` arrays.** Derive them from `git ls-files 'skills/**/SKILL.md'`.
A hand-typed path that is one character wrong is caught by O7, but a hand-typed list that is merely
*stale* is the failure this section exists to prevent, and it is cheaper to never author it.

## An issue you did not create

An issue filed by someone outside this repository arrives raw — it is not agent-ready, and
handing it to a build agent as filed skips the verification that makes tickets here safe to
build from. Route it:

1. **Triage before building.** Categorise it and verify the claim. For a defect report,
   that means a reproduction you ran, not a description you believed: the factory's defect
   contract requires reproduction evidence before an implement run, and an issue without one
   is not buildable yet.
2. **A confirmed report about a published card is an occurrence.** The reporter did the
   field work; the incident is real recurrence evidence. Record and count it under
   "Recording a new occurrence" below **before** any fix lands, so the evidence survives
   even if the fix stalls.
3. **Only a verified, self-contained leaf ticket gets `ready-for-agent`** — with its
   blocking edges declared, like every ticket the spec pipeline produces.
4. **Never re-triage pipeline tickets.** Tickets produced from a spec are already
   agent-ready; triage is only for what arrived raw.

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
   elsewhere in the card's own **`.md` files** — so a count cannot rise without the record that
   justifies it. The row's dated references *are* its occasions: a dated link to anything else (a triage
   record, a release) does not belong in that row.

   **The check runs in both directions (added 2026-08-24).** The rule above stops a count
   rising without a record. The reverse rule stops a record sitting uncounted: a line in any
   **`.md` file** under the card that carries **both a date and the word `occurrence` or
   `occurrences`** is an occurrence record, and its date must be cited in the `Occasions
   counted` row. So step 1 above is not optional bookkeeping you can do and forget — writing
   the dated entry now obliges the row, and CI says so.

   **Both directions scan `card.rglob("*.md")` and nothing else.** A dated occurrence recorded
   in a `.py`, `.txt` or `.json` file inside the card is invisible to the check — it will neither
   satisfy a count nor oblige one. Record occurrences in markdown, or the guard cannot help you.

   Two consequences worth knowing before you write the entry. First, the trigger is the
   collection's own term of art, not any date: screen dates, methodology pins and verification
   dates are dated lines that are not occurrence records, and they stay uncited. Second, the
   pattern is `(?<![\w-])occurrences?\b`: it matches singular and plural, and the lookbehind
   excludes a **preceding** hyphen only. So `co-occurrences` and `re-occurrence` do not trip it
   — the first is a correlational term one live card uses in a row that explicitly disclaims
   being an occurrence record — but a **trailing** hyphen does not protect anything, and
   `occurrence-record (2026-08-24)` **does** trip it. If a dated line genuinely is not an
   occurrence, **reword it**; do not add its date to the row to silence the check, because that
   inflates the count the row exists to keep honest.
3. **Fan-out is not recurrence.** Two symptoms of one task, a design session, and a fixture
   proving a validator rejects something are one occasion or none — ADMISSION.md criterion 2's
   own words: "not inflated by fan-out from a single run."
4. **The label tracks the count in both directions.** Under two counted occasions the card
   states `RECURRENCE-THIN` in its `EVIDENCE.md`; at two it comes off, because a stale honesty
   label is its own kind of dishonest. The check matches the token, so removing the token is
   the whole edit — a card that argues about the label in prose keeps tripping it.
5. **Dated disposition records are snapshots and are not rewritten.** A card that later leaves
   the thin tier says so in its own file and in the changeset; the triage record
   that found it thin keeps saying what it found on the day it ran.

## No self-authority

A card's name, its role in this repository, its prior use, and the decisions it produced are
not evidence for a verdict it reaches. An outcome an instrument produced cannot serve as
independent proof that the instrument works. Cite first-hand evidence for each load-bearing
claim, and name the result that would reverse the verdict.

This binds every published card, and it binds hardest where a card sits in the repository's own
machinery — the standing that makes a card feel authoritative is the same standing this rule
refuses as evidence. Two records from the collection's own history state the cost of ignoring
it: an architecture review that treated a card as an ironclad classifier "because it was called
a gate, was referenced by repository policy, and had processed prior candidates" reached its
conclusions before any first-hand repository evidence was read; and, stated generally,
"rejection count cannot prove rejection quality, and a gate cannot validate itself by applying
its own criteria."

## Retirement

Retirement is a first-class event, not an afterthought — the collection's credibility comes
from shrinking honestly. A skill leaves three ways:

- **Harness cut** — a current receipt carries `CUT` with its `cut_sub_reason`; nothing is
  left for the skill to improve.
- **Pre-registered platform-fix** — the skill's `EVIDENCE.md` re-screen trigger names a
  specific platform change that would make the underlying failure impossible; when that change
  ships, the skill retires against its own stated criterion, no screen required.
- **Withdrawn on the policy** — a published card is removed because it cannot satisfy the
  admission policy it is measured against. The card's own `EVIDENCE.md` supplies the proof, and
  no screen is required, because the failing criterion is a record of occurrences rather than a
  measurement of lift. This route is deliberately narrow: it fires only on a criterion the
  card's own evidence record demonstrably fails, and the changeset must quote the failing row.
  An owner who has cooled on a card has not met this bar; a card whose `Occasions counted` row
  reads `0` against a policy criterion requiring an observed failure has.

Execute a retirement as: remove the skill directory; drop it from its bucket README and the
top-level README; add a row + a short narrative to
`RETIRED.md` with the cause stated plainly; and link the evidence at the **last release tag**
(`blob/<tag>/…`) and the receipt at the harness commit, so "record intact" survives the
file's removal. If a general lesson outlives the skill, name it in the retirement note as
ordinary hygiene rather than resurrecting the card.

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
on purpose) and `DISTILLED` (written from research, no triggering incident). An Origin field
opening with a word outside the vocabulary is refused rather than guessed at, on the same rule as
the controlled fields: a card that has not said which tier it is cannot be counted into either.

**The page states no tally of cards, of tiers, or of anything else that tracks repository
state. Owner ruling 2026-08-24: do not add one back.** The rule now reads in one direction only —
any tally the page *does* state must agree with the records, and zero tallies is the expected
case. An earlier edition required `README.md` to state the tiering in exactly two places, which
made the page's arithmetic mandatory: every admission and every retirement turned the build red
until someone re-derived two numbers by hand, in prose no reader had asked for. That is the same
maintenance tax the banner's counts were retired for on 2026-08-23, and the same one that had
pinned `9 published card(s)` inside `scripts/test_validate_card_files.py`. Prose that must be
re-checked whenever a card moves is a liability, not a receipt; the receipts live in the cards.

A miss turns the build red; do not treat any single prose line as the checklist.

## The rotation and harvest pass

When the maintainer asks for a rotation, hygiene, weeding, or TLC pass over this collection,
this section is the procedure. It is written so a cold session can run the whole pass from
this repository plus two maintainer-supplied evidence locations — session records and usage
telemetry. The maintainer's private trigger skill only names those locations and points here;
if a cold session cannot run the pass from this section, the defect is in this section.

**Two triggers.** The pass fires on two occasions. On arrival: the session that commits a
receipt for a published card — a controlled row rewritten with a Receipt clause — runs the
disposition for that card in the same working unit. At the rotation pass: the "Read existing
verdicts read-only" step (step 4) sweeps every receipt whose `skill_id` matches a published
card, using the receipt files under the harness's `docs/sers/receipts/` at the named harness
commit declared in the Inputs table.

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
| Harness release (declared per pass) | Authoritative — the harness version the collection judges receipts against, re-dated at each pass. |
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
   from the log entirely is a discriminator candidate, and there are **three** diagnoses, not
   two. Take them in this order, because the first one disqualifies the card from branch 3 and
   a pass that skips it will confidently mis-file the card as insurance:

   1. **Unobservable.** The card fires through a mechanism the platform's dispatch counter
      cannot see — a hook, a trap, an always-loaded carrier. Its absence from the log is not
      **dispositive** about retrieval, and is no evidence at all about worth; it is a limit of
      the instrument. Note the precise scope: the counter still observes the model-invocation
      path, and a zero there is weak but real evidence that the card's description was never
      picked. The counter is blind to the enforcing path only, so the absence caps how much
      that zero can carry — it does not erase it. Measured 2026-08-24, two of the fifteen
      published cards are in this case — `git-pull-rebase-trap` and
      `github-pages-deploy-verification` — and both say so in their own `Dispatches recorded`
      row, which is why that row's zero must read `No recorded dispatch` and never `0`.

      **The evidence behind those two differs in kind, and this branch does not make them
      equal.** `git-pull-rebase-trap` has a dedicated PreToolUse guard with a test beside it, in
      the maintainer's private environment; the mechanism demonstrably exists.
      `github-pages-deploy-verification` has **no dedicated guard** — only a prompt-router
      nudge, and a nudge is not a hook firing: if the model acts on a nudge by calling the Skill
      tool, the counter *would* see it. So for that card the absence is equally consistent with
      the nudge never firing and with the nudge firing and being ignored. Do not file a card
      here on a router nudge alone; either name the guard, or record the absence as
      undiagnosed. **Check this branch before searching the records**, because the search below
      cannot distinguish an unobservable card from insurance: both return "no occasions found".
   2. **Retrieval defect.** The records show occasions where the card's trap occurred and the
      card did not fire. The description never matches how the situation gets phrased — fix
      the description. **Branch 1 does not close this one.** A hook-fired card has its own
      version of this failure — the trap occurred and the hook did not fire — and it is
      detectable from the session records without the counter. Run branch 2 on an unobservable
      card too; only branch 3 is foreclosed.
   3. **Insurance.** No such occasion in the records, and the card is observable. The trap
      never came up; consistent with `CANT_TELL_YET`.

   Invocation is retrieval evidence, never an occasion count and never a measure of worth.
   Done when every published card has a row and every never-fired card carries one of the
   three diagnoses above or a dated "discriminator unrun".

   **Scan the pointer surface in the same step, because no gate does.** Eight validators now
   run in CI — file presence and the `EVIDENCE.md` controlled rows (`validate_card_files.py`),
   the banner line and the derived counts (`validate_scoreboard.py`), skill-file formats
   (`validate_skill_formats.py`), voice provenance (`validate_voice_provenance.py`), the eval
   corpora (`validate_eval_corpora.py`), the brand kit (`validate_brand_kit.py`), the
   scheduled conformance sweep (`validate_conformance.py`), and the official Agent Skills spec
   validator (`validate_spec_conformance.py`) — plus the link check and the residue gate.

   **Not one of them reads a card's `description` AS A ROUTER**, which is the only thing that
   decides whether a model-invocable card is ever reached. Three of them touch the field and
   none answers that question. `validate_card_files.py` measures its LENGTH against the published
   200 bar. `validate_eval_corpora.py` parses frontmatter, but only the
   `name` key, and only to refuse a corpus whose `skill_name` has drifted from the card it
   claims. `validate_spec_conformance.py` reads the description's SHAPE — that it is valid YAML
   and inside the specification's 1024-character limit — and neither length nor shape is
   reachability: a well-formed 200-character description naming none of the words a user types
   passes every gate cleanly. **Length is checked now; WORDING is not, and wording is what
   decides retrieval.** Check that before concluding the gates
   have grown to cover retrieval: they have not, and the count rising from four to eight is
   exactly the kind of change that makes a reader assume they have. A card's `description` is
   the only thing that decides
   whether a model-invocable card is ever reached, so the collection currently validates its
   receipts and not its retrieval surface: a card can carry a perfect evidence record, derive
   correctly into every count, pass all eight gates, and be permanently unreachable. Read each
   card's `description` against how the situation actually gets phrased, and treat a
   never-fired card's pointer as a suspect before concluding insurance. Note also which cards
   *cannot* fire by construction — `disable-model-invocation: true`, or sitting in
   `_quarantine/` and therefore not installed at all — and do not read their zero as evidence
   about their worth.

   This is the same defect one layer up from the router bug of 2026-08-23: a test suite that
   checked everything except the predicate deciding whether anything fires. Recognising the
   shape is the point — the apparatus that grades a thing tends to grade what is easy to
   assert, and the trigger is never the easy part.
3. **Repair gate — run BEFORE screening, and before any admission or retirement call.**
   A card whose text is wrong is the wrong artifact to measure: a screen on a stale card
   produces a real number about a document you are replacing. Repair first, then screen the
   repaired card.

   A card enters repair when **any** of these is true. The list is the criterion; "it reads
   fine" is not a disposition:
   - **A harvested occurrence falsified its own procedure or remedy.** The occurrence is not
     merely a tally mark — read what it says about the card's instructions.
   - **Its `description` does not name a branch the new evidence added.** The description is
     the retrieval surface, so a card that gains a case and not a trigger is unreachable on
     exactly the case that just occurred.
   - **It asserts library, API, framework or platform behaviour, and the claim is undated or
     older than the current release.** Authoring conventions above already require dated,
     checkable factual claims. **Check them through Context7** — resolve the library, query
     the current docs, and re-date the claim or correct it. Do this before shipping the card
     AND before "fixing" a claim, per the same rule: a wrong correction to an evidence-first
     collection is worse than the original error. A claim Context7 cannot confirm is marked
     unverified rather than quietly kept.
   - **Its frontmatter drifted** — see 2a. On repair, if the card already carries `version`
     and `date`, bump the version (minor for a content change) and set the date to the day of
     the repair, so it does not claim a revision it no longer matches. **If the card carries
     neither, leave it that way.** Adding those keys to a card that never had them widens the
     dialect spread 2a exists to close, and the published tree strips them on promotion
     regardless — so the fields are a candidate-side convenience, never a requirement.

   **Repair is skill authoring, so stack the skill that does it.** Do not edit a card
   freehand. Run the repair through `writing-for-agents` (Pocock plugin,
   `productivity/writing-for-agents`) and apply its levers by name: the `description` is a
   **context pointer** carrying one trigger per branch; keep each meaning in a **single
   source of truth**, because the same finding written into both `SKILL.md` and `gotchas.md`
   is duplication rather than thoroughness; prune **no-ops**.

   Done when every card touched by this pass is either repaired, or recorded as needing no
   repair against the four criteria above.

4. **Route the worth question — and know that the measurement instrument is NOT in this
   loop.** The collection does not decide a card's worth in its own prose. It also does not
   send every card to the measurement harness, and that is a settled decision rather than an
   omission.

   **The binding constraint on this collection is admission criterion 2, recurrence — not
   measurement.** The harness measures with-and-without lift, which is a different question,
   and its own record is zero production KEEPs across 26 screens because production skills
   ceiling at a Null-arm pass rate of 1.00. A ceiling converts to `CUT` only for a
   transformative-lift skill; for any other class it means the trap did not arise in that
   screen, so the verdict is `CANT_TELL_YET`, never `CUT`. Running the mill over cards that
   will all ceiling costs a great deal and returns nothing this pass can act on. Steps 1 and
   2 — reading the session records — are the cheapest real evidence in the system, and they
   are where this pass does its real work.

   So the routing is narrow and stated:
   - **Default: no screen.** A card stays `UNMEASURED` or `CANT_TELL_YET` and says so. That
     is an honest label, not a gap to close.
   - **Screen only a candidate carrying a frozen empirical contract** — a fixture AND a
     counterfixture — because that is the only shape the harness can return a real verdict
     on. Two candidates qualify today: `mock-masked-stub-trap` and
     `walk-the-recipe-as-target-user`.
   - **Read existing verdicts read-only** rather than running anything, from two sources.
     First, the harness's evidence store: `python -m skill_harness screen verdict
     --evidence-db <path>/evidence.db`. Checked 2026-08-23: that store answered "No
     admissible screens in the store", so no published card's label can currently be
     sourced from it. Second, the receipt files under the harness's `docs/sers/receipts/`
     at the named harness commit declared in the Inputs table — sweep every receipt whose
     `skill_id` matches a published card.
   - **Never manufacture a number.** The vocabulary is closed — `KEEP`, `CUT` (`subsumed` |
     `no_lift` | `harmful`), `CANT_TELL_YET` — and a missing number is a typed refusal. **A
     passing acceptance test is not a screen result**; see Hard stops.

   Done when every card the pass proposes to admit or retire either carries a screen verdict,
   or carries a dated statement of why no screen applies to it.

5. **Currency gate — run on every receipt before any disposition.** A receipt that is not
   current disposes nothing: its row reads `CANT_TELL_YET (stale receipt: <reason>)` and
   keeps the receipt link as history. The four checks run fail-closed with typed reasons:

   - **Card content:** `no_skill_id` (receipt lacks `subject_identity.skill_id`),
     `card_hash_mismatch` (receipt's `skill_id` differs from `sha256(SKILL.md)`).
   - **Harness identity:** `no_harness_version` (receipt lacks
     `subject_identity.harness_version`), `harness_mismatch` (receipt's harness version
     differs from the declared pass harness), `oracle_stale` (receipt's
     `instrument_identity` differs from the declared pass oracle), `model_drift` (receipt's
     `instrument_identity.extractor_model` differs from the declared pass model).
   - **Trigger attestation:** `no_trigger_row` (card lacks a `Re-screen trigger` row),
     `attestation_missing` (trigger row present but no attestation clause),
     `attestation_expired` (attestation date precedes the receipt's `source.date`, or
     precedes the newest `skills` release tag),
     `trigger_fired` (attestation names a trigger that has already shipped).

     **This step writes the attestation.** The attestation is a clause on the card's
     `Re-screen trigger` row, in this shape, fixed by the current-receipt rule of 2026-08-29
     in the maintainer's decision record:

     `Attested <YYYY-MM-DD>: no named trigger has fired since <receipt source.date>; checked
     <what was read, named>.`

     Write it in the same working unit as the check, the first time a receipt is gated for a
     card, after reading the sources the triggers name (a release list, a tag list, a model
     roster) and finding no event since the receipt's `source.date`. Re-date it at every later
     pass that gates a receipt for that card. A card with no receipt to gate carries no
     attestation, and that is not a defect. The clause is prose a pass writes after looking, not
     a validator output, and it expires at every `skills` release tag: a receipt cannot stay
     current by nobody looking. Between 2026-08-30 and 2026-09-04 this step required the clause
     while only step 6 named a writer, so `attestation_missing` failed for every published card
     and no receipt could reach step 6. The gate's first run (`skills#219`) found that, and the
     writer was restored here from the decision record.
   - **Arm coverage:** `arm_coverage` (receipt's `subject_identity.arms` does not include
     both `null` and `full` for a two-arm receipt, or does not include `null` for a
     Null-only receipt).

   A not-current receipt's verdict is not applied and the `Re-screen trigger` attestation is
   not re-dated. Done when every receipt swept in step 4 has been currency-checked: current
   receipts proceed to the record step; not-current receipts carry
   `CANT_TELL_YET (stale receipt: <reason>)` on the controlled row and are not disposed.
6. **Record step — rewrite the controlled row with the receipt clause.** For each current
   receipt (passed the currency gate), rewrite the controlled row (`Screen result` for a
   Null-only receipt, `Paired verdict` for two-arm) to the row shape: `<VERDICT>. Receipt:
   [<file>.json](<harness blob URL pinned to a commit, never main>), dated <source.date>,
   harness <harness_version>. <reason and caveats>`. For `CANT_TELL_YET` the prose names
   the typed reason. The `Re-screen trigger` attestation was written or re-dated at step 5;
   this step does not touch it. The clause is a convention; the three required rows are
   unchanged.
7. **Dispose step — route by verdict.** `KEEP` and `CANT_TELL_YET` stop at the row; a
   `CANT_TELL_YET` card stays published with its typed reason. `CUT` fires Retirement
   through its first route (see "Retirement" above), widened from "Screen null" to
   **"Harness cut — a current receipt carries `CUT` with its `cut_sub_reason`"**; the
   `RETIRED.md` "What made it unnecessary" cell opens with the `cut_sub_reason` word. The
   route's evidence is the receipt.
8. **Reconcile, then validate.** Propagate each count or label change to every derived
   surface, walking the consequence chain before the edit — a one-integer change
   legitimately breaks several pins at once, and each break is the guard working: fix the
   surface, keep the pin. Then run the whole gate set with `PYTHONUTF8=1` — eight validators
   and their eight suites:


   | Validator | Suite | What a pass most often breaks here |
   |---|---|---|
   | `scripts/validate_card_files.py` | `scripts/test_validate_card_files.py` | the three contract rows, and the occasions check in both directions |
   | `scripts/validate_scoreboard.py` | `scripts/test_readme_admission_lead.py` | derived counts, the banner line, origin tiering |
   | `scripts/validate_eval_corpora.py` | `scripts/test_validate_eval_corpora.py` | a renamed card breaks its corpus's `skill_name` |
   | `scripts/validate_skill_formats.py` | `scripts/test_validate_skill_formats.py` | a card file whose extension is outside `.md`/`.txt`/`.py`/`.json`, or a `__pycache__` bytecode file with no source beside it. **No size check exists** — the size guidance under "Authoring conventions" is unenforced |
    | `scripts/validate_voice_provenance.py` | `scripts/test_validate_voice_provenance.py` | a quotation in `BRAND.md` section `## Voice` with no `Source:` line citing `VERBATIM.md`, or a first-person line on a scanned surface (README.md today) that is not a recorded `VERBATIM.md` line |
   | `scripts/validate_brand_kit.py` | `scripts/test_validate_brand_kit.py` | declared colours, banned words, asset hash pairs |
   | `scripts/validate_conformance.py --root .` | `scripts/test_validate_conformance.py` | governance surfaces (the scheduled job's own pair), and O7's manifest-vs-tree check |
   | `scripts/validate_spec_conformance.py` | `scripts/test_validate_spec_conformance.py` | the OFFICIAL spec validator over both trees. **Needs `npx`.** Its suite tests the allowance classifier only and says so; the live run is CI's |

   **Run all eight, not the ones the pass thinks it touched.** The reconciliation step exists
   because a one-integer change propagates further than the editor expects; a gate list trimmed
   by expectation defeats the same property. This table was four validators until 2026-08-24,
   became seven the same day and eight before the day ended, and shipped stale at four — if it disagrees with CI, CI is right and this table is the bug. Re-derive
   the roster with:

   ```
   grep -rnE 'python3? +[^ ]*(validate_|test_)' .github/workflows/
   ```

   **Use that form, not a `scripts/`-scoped grep.** Three CI gates do not live in `scripts/` —
   both session-boundary parity suites and the stale-packet poison control, all under
   `skills/engineering/im-{down,up}/`. A `scripts/`-scoped grep returns a clean confirmation
   while those three are still unrun, which is a re-derivation that certifies its own blind spot.

   **If the pass touched either session-boundary card, parity is a gate, and here are the
   commands.** `im-up` and `im-down` share eight files, and each card's suite verifies the pair
   against its sibling. Run both from inside the card directory — the suites locate their sibling
   by relative path:

   ```
   cd skills/engineering/im-down && python test_validate_packet.py
   cd skills/engineering/im-up   && python test_validate_packet.py
   ```

   Each must print `, no-drift` in its pass roster. The suite reports parity NOT VERIFIED **and
   still exits 0** when it cannot find its sibling, so CI greps the roster for that token rather
   than trusting the exit code, and so must you. A rename or a move that hides one card from the
   other turns the parity gate off silently while every suite stays green — read the roster line,
   not the exit status. The third off-`scripts/` gate is the poison control, which asserts the
   gate can still fail:

   ```
   cd skills/engineering/im-down
   python validate_packet.py fixture-stale.md --mode produce --repo-root <repo root>
   ```

   It must exit **non-zero** and print `REJECTED`. Note the mode is `produce`, not `receive` —
   the control asserts the producer refuses to emit a packet against a HEAD that has moved.

   **One further gate is scheduled, not per-PR, and a rotation pass should know it exists.**
   `conformance-schedule.yml` runs an **Outgrown-rotation guard** before its sweep: it fails the
   scheduled run if the published card count exceeds `MAX_CARDS_PER_RUN` (40) or equals zero. It
   is a rotation tripwire, not a conformance result. Measured 2026-08-24 the count is 15, so it
   cannot fire today; a pass that admits past 40 must decide on rotation rather than raise the
   ceiling.

   Done when **all eight validators, all eight suites, and — if a session-boundary card was
   touched — both parity suites and the poison control** pass, AND a re-run of the whole pass
   with no new evidence would produce zero diff: the pass re-derives from current records every
   time, keeps no incremental state, and is safe to run twice.
9. **Adjudicate.** Four dispositions, not two: admit, retire, **repair** (step 3), or a dated
   deferral. New candidates enter through the [admission policy](ADMISSION.md), whose four
   questions are answered directly; retirement candidates leave through "Retirement" above. `_quarantine/`
   promotion is `git mv`, so the card carries its history. Open a candidate's
   `PROVENANCE.md` before diagnosing drift or duplication — one candidate is a staged patch
   to an already-promoted card, and it has been misread as version drift once already. Done
   when every surfaced candidate carries a disposition or a dated deferral.
10. **O5 step — run with `--harness-root`.** The pass runs O5 with `--harness-root` as a
    named step and records its output line in the pass note. Done when every published card
    whose `skill_id` matches a receipt carries that receipt's verdict or a typed not-current
    reason on its controlled row.
11. **Ship.** Branch → PR with a changeset. Merge authority is the maintainer's to hold or to
   delegate, and this file does not fix which — it fixes the gates, which hold either way: CI
   green, and the PR head SHA matching the branch ref before the button is pressed. That second
   gate is not ceremony. A PR merged while later commits were still being pushed froze its head
   at the merged SHA while the branch ref moved on, stranding the follow-on commit on a closed
   PR, and `gh pr checks` reported green for the older head throughout. Compare `git ls-remote`
   against the PR's `headRefOid`. **Publication is a separate authority and stays the
   maintainer's regardless**: a release tag, a new published asset, the repository's social
   preview or About settings. The PR body reports
   every disposition, flattering or not.

**The ordering is a constraint, not a preference.** Harvest before repair, because the
occurrence tells you what to repair. Repair before screen, because a screen measures the text
in front of it. Screen before adjudicate, because admission and retirement are verdicts and
this collection does not author verdicts in prose. A pass that reorders these produces a
number about the wrong artifact, or a disposition with no measurement under it.

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

<!-- vale Taste.Register = NO -->
Syntax: short sentences, concrete nouns, direct verbs, active voice, one step per
sentence. Never: euphemism after the underlying action is known; "perhaps",
"possibly", or "arguably" as cushioning for a supported claim; "readers may
conclude"; sarcasm or victory laps; passive voice that hides the responsible
component; abstractions that erase the person affected.
<!-- vale Taste.Register = YES -->

## License

MIT. See `LICENSE`.
