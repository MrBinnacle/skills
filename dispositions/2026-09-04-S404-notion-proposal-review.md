# Disposition record — 2026-09-04 Notion proposal review

Date: 2026-09-04. Source: twelve rows of the maintainer's private Skills Library registry,
reviewed against this repository at `main` = `8e3c2a6`.

Method: the registry supplied candidate architecture and proposed annotations. This repository
supplied executable truth. Where the two disagreed, the repository decided. No skill was renamed,
no published artifact was overwritten, no `EVIDENCE.md` field was changed, and no public trigger
was broadened. Every version, path, byte count and character count below was measured in the
working tree, not quoted from the registry.

Scope of authority: this record adjudicates admission and repair against
[`ADMISSION.md`](../ADMISSION.md) (`admission-policy v1`) and the rituals in
[`AGENTS.md`](../AGENTS.md). It authorises one changeset. Everything else it converts into a
ticket or refuses.

## Headline findings

1. **The registry asserts a published card that this repository deleted five days earlier.** The
   `skill-necessity-gate` row reads `Lifecycle: Published`, `Status: Active`, `Version: 1.2.0`,
   with a `Source URL` pointing at `blob/main/skills/meta/skill-necessity-gate/SKILL.md`. That
   path is absent from `main`. Commit `ef5adf5` (pull request #202) removed the directory on
   2026-08-31. The proposal to extend that card therefore has no artifact to extend.
2. **The registry records a per-card version number that published cards do not carry.** Two rows
   read `Version: 1.4.0`. Measured: the frontmatter of every published card holds exactly two
   keys, `name` and `description`. `1.4.0` is the collection version in `package.json`, not a
   property of either card. A per-card semantic version recorded against a published row is a
   number the artifact does not have.
3. **One changeset is justified against this repository today**, and its justification comes from
   an `[OBSERVED]` entry already in the tree, not from any registry annotation. Two proposals
   are refused as framed. Five candidates are deferred. Six exclusions are confirmed.
4. **Three of the five addition candidates hold no repository artifact at all.** They cannot be
   promoted by `git mv`, which is the only promotion route
   [`_quarantine/README.md`](../_quarantine/README.md) endorses, because promotion across a
   repository boundary lands the card as one fresh commit with no history.

---

## 1. `skill-necessity-gate` — REJECT as framed; relocate the content

| Field | Finding |
|---|---|
| **Disposition** | REJECT the update. The card is retired. Relocate the useful content to `AGENTS.md`. |
| **Current repository artifact and exact version** | None. `skills/meta/` holds one card, `router-skill-predicate-gap`. The directory was removed by `ef5adf5` on 2026-08-31. The last version that shipped is reachable at `blob/v1.3.0/skills/meta/skill-necessity-gate/`. |
| **Demonstrated defect or unmet need** | The unmet need is real and is not the one the proposal names. A twelve-way packaging decision (standalone, parent, nested specialist, shared primitive, hook, access provider, repository rule, output style, script, composition edge, build artifact, no artifact) is a better instrument than the binary the repository currently carries. The defect the proposal does not address is the one that retired the card: `Occasions counted` read `0` across the card's whole life. |
| **Smallest proposed changeset** | Expand the existing topology rule in `AGENTS.md` → "Authoring conventions" from a two-way choice (model-invocable against procedure) to the twelve-way disposition list, keeping the deciding question ("who does the strategic thinking?"), the side-effects rule, and the standing-cost disclosure. One file, one section. |
| **Files added, modified, preserved, retired** | Modified: `AGENTS.md`. Added: none. Preserved: `RETIRED.md`'s narrative, unedited. Retired: nothing further. |
| **Identity and version impact** | None. No skill identity is created, restored or renamed. The collection version takes a patch bump through a changeset for the convention change. |
| **Provider/dependency contract** | None. |
| **Deterministic versus subjective authority** | Wholly subjective. No validator reads the topology rule; it governs an authoring judgement. State it as guidance, never as a gate. |
| **Required evals and ablations** | None, and this is the point: a rule in `AGENTS.md` makes no public claim and needs no receipt. A card would need both. |
| **Failure and rollback path** | Revert the `AGENTS.md` section. No installed user is affected, because `AGENTS.md` ships to nobody. |
| **Evidence ceiling** | Not applicable to a convention. For the card, the ceiling is hard: re-admission requires `ADMISSION.md` criterion 1, an unaided failure **observed** rather than predicted, and criterion 2, independent recurrence. A richer rubric does not supply an occurrence. Occurrences are found, not designed. |
| **Is a changeset justified?** | Yes for the `AGENTS.md` edit. No for any card. |

Two further observations, because they bear on how this proposal should be read.

The registry page's own callout states "Current authority: GitHub v1.2.0 remains the published
executable artifact." That sentence was false when it was written. Treat every "current
authority" line in the registry as a cache of a repository lookup, and re-measure it.

The proposal instructs: "Do not let the gate validate itself through its name, policy status, or
prior decisions." That instruction is correct, and it is the **No self-authority** rule this
repository adopted *from* this card's retirement. `RETIRED.md` records the argument the card
could not answer: its stated outcome evidence was that four candidates "were processed under this
gate and none were admitted", and a gate agreeing with an outcome it produced is not independent
evidence that the gate works. Restoring the card on the strength of the discipline that removed
it would reproduce the circularity in one move.

## 2. `parallel-review-disposition-schema` — UPDATE, narrower than proposed

| Field | Finding |
|---|---|
| **Disposition** | UPDATE. This is the one justified changeset. |
| **Current repository artifact and exact version** | `skills/orchestration/parallel-review-disposition-schema/`. `SKILL.md` 5,888 bytes, description 196 characters. Sibling `ADVERSARIAL-VERIFY-SEAT.md` 2,928 bytes. Card frontmatter carries `name` and `description` only; it has no version of its own. Last shipped in collection `1.4.0`. |
| **Demonstrated defect or unmet need** | Measured in the tree, not proposed. `gotchas.md` carries an `[OBSERVED]` entry dated 2026-08-17: two reviewers each numbered findings M1–M5 locally, the consolidator renumbered, and one real finding was silently dropped and stayed dropped across four commits. The entry names three mitigations, the first being globally-unique IDs at source. **`SKILL.md`'s prescribed four-part schema carries none of them.** A mitigation for an observed failure sits in the append-only log and never reached the instructions the card gives. That is the defect. The provider envelope's `run_id` / `stage_id` / `provider_id` namespacing is exactly its fix. |
| **Smallest proposed changeset** | (a) Add a fifth element to `SKILL.md` → Solution: **namespaced finding identity**, one short paragraph requiring seat-of-origin prefixes assigned at dispatch and pasted through consolidation unchanged. (b) Add one sibling file, `PROVIDER-ENVELOPE.md`, carrying the envelope fields, one-writer authority, cycle detection, declared maximum nesting depth, the failure and abstention states, and the raw-return preservation rule. (c) Point to it from `SKILL.md` at moment of need, per the repository's cross-reference convention. |
| **Files added, modified, preserved, retired** | Added: `PROVIDER-ENVELOPE.md`. Modified: `SKILL.md` (one paragraph plus one pointer), `gotchas.md` (append only). Preserved unchanged: `description`, `EVIDENCE.md`, `ADVERSARIAL-VERIFY-SEAT.md`, `evals/evals.json`. Retired: nothing. |
| **Identity and version impact** | Identity unchanged. Description unchanged — and it cannot change much: at 196 characters it holds four characters of headroom against `DESCRIPTION_LIMIT = 200` in `scripts/validate_card_files.py`. The validator enforces the instruction to keep the public trigger narrow. Collection takes a patch bump. |
| **Provider/dependency contract** | The envelope declares provider identity and type across model, skill, access-server, agent, peer-session and human returns. It imposes no runtime dependency: it is a document describing a return shape, and a parent that ignores it loses comparability, not function. |
| **Deterministic versus subjective authority** | Split, and the split must be written down. Envelope **shape** is machine-checkable and a hook may verify it. Envelope **content** — findings, dispositions, conflicts — is reviewer judgement and no hook may adjudicate it. One caveat to record in the file: `writes_performed: false` is a provider's assertion about itself, not a check. Record it as claimed, and let the parent verify it by tool grant — a reviewer holding no write tools cannot write, and that is evidence; a reviewer stating it did not write is not. |
| **Required evals and ablations** | The registry proposes a no-schema / current / reduced-schema comparison extended across serial, nested and parallel dispatch, measuring join errors, lost findings, identifier collisions, hidden provider failures and context cost. That is a sound design and it is not a precondition for this changeset, because the changeset closes an observed drop rather than claiming lift. Add the eval case to `evals/evals.json` asserting that a dispatch without namespaced identity is flagged. |
| **Failure and rollback path** | Revert the commit. The four-part schema is untouched by construction, so rollback restores the current behaviour exactly. If synthesis ambiguity rises after the change, the added element is one paragraph and removable in isolation. |
| **Evidence ceiling** | `UNMEASURED`, and it stays there. `EVIDENCE.md` states the reason structurally: the card's home domain has no deterministic sandbox oracle, so the Full-against-Null protocol does not apply. No annotation, and no amount of envelope design, converts that into a measured verdict. Do not let the changeset appear to raise the evidence tier. |
| **Is a changeset justified?** | Yes. It is the only one this review authorises against a published card. |

## 3. `subagent-research-reliability` — NO CHANGE; the compatibility question resolves against consuming the envelope

| Field | Finding |
|---|---|
| **Disposition** | NO CHANGE to this card. One cross-reference lands in `parallel-review-disposition-schema` instead. |
| **Current repository artifact and exact version** | `skills/orchestration/subagent-research-reliability/`. Description 166 characters. `EVIDENCE.md`: five counted occasions, four recorded dispatches, `Screen result` and `Paired verdict` both `UNMEASURED`. Last shipped in collection `1.4.0`. |
| **Demonstrated defect or unmet need** | None found. The stated condition for updating was that the shared envelope reduce missing-provider and lost-return failures without weakening the verification role. It does not meet the first half, and the reason is structural: **a dead letter produces no envelope.** This card's Check 0 exists because an agent that answers in plain text emits nothing the caller receives; a return contract cannot describe a return that never happens. The envelope's `status: unavailable \| failed` fields require a provider that reported. So consuming the envelope would add fields to returns that already arrive, and change nothing about the returns that do not. |
| **Smallest proposed changeset** | Zero lines in this card. In `PROVIDER-ENVELOPE.md`, one sentence stating that a provider which never returns produces no envelope, and directing the reader to this card's Check 0 for the delivery control, using the repository's invocation phrase. |
| **Files added, modified, preserved, retired** | This card: nothing modified. All five files preserved. |
| **Identity and version impact** | None. |
| **Provider/dependency contract** | The two cards keep separate responsibilities and that separation is the finding. This card owns **delivery and truth**: return-channel declaration, batching for large returns, licensed partial returns, tool-grant verification, citation verification, negatives verified first, locator validation. The schema card owns **comparability**: joinable shape across reviewers. They are different layers of one dispatch, not competing schemas, and writing the envelope into this card would create the second schema the review was told to avoid. |
| **Deterministic versus subjective authority** | Deterministic where it matters. Check 1 reads a frontmatter `tools:` list. Check 2 re-runs a command, fetches a URL, opens a locator. None of that is judgement, which is why the card is worth its standing cost. |
| **Required evals and ablations** | None for a no-change disposition. The registry's own suggested test — verify the current agent return path and tool-grant surface under the current runtime, then plant a tool-deficient researcher and a false citation — is a **repair-gate** item under `AGENTS.md` step 3, because the card asserts platform behaviour. File it; do not bundle it with envelope work. |
| **Failure and rollback path** | Not applicable. |
| **Evidence ceiling** | `UNMEASURED`, with a named path upward that the collection has already registered: the candidate screen task in `EVIDENCE.md` (a dispatch config containing a web-toolless research agent, with a deterministic oracle on whether the gap is detected before dispatch) is oracle-compatible. This card is screenable in principle. That is worth more than an envelope. |
| **Is a changeset justified?** | Not against this card. |

---

## Addition candidates

### 4. `self-documenting-code` — DEFER; land the baseline as a candidate first

| Field | Finding |
|---|---|
| **Disposition** | DEFER. Not admissible today, and the next step is not the one proposed. |
| **Current repository artifact and exact version** | **None.** Measured with `git ls-files`: the name appears nowhere in the tree, neither under `skills/` nor under `_quarantine/`. It exists as a registry row at `0.1.0` with an attached package, SHA-256 `2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`, and as a local install on the maintainer's machine. |
| **Demonstrated defect or unmet need** | The registry's own page states it: "No live Claude Code evaluation ran in this session" and "Static package validity is not an efficacy result." Against `ADMISSION.md` this fails criterion 1 (no observed unaided failure), criterion 2 (no occasions counted anywhere), and criterion 4 (no `EVIDENCE.md` exists). Three of four. |
| **Smallest proposed changeset** | Not a `0.2.0-rc.1` build. Land `0.1.0` into `_quarantine/self-documenting-code/` with a `PROVENANCE.md`, so that every later version accrues history inside the repository and promotion stays a `git mv`. Build the candidate afterwards, on top of that history. |
| **Files added, modified, preserved, retired** | Added under `_quarantine/`: the `0.1.0` card, flattened to the per-skill flat layout, plus `PROVENANCE.md` and an append-only `gotchas.md`. Preserved: the `0.1.0` package as the frozen executable baseline, exactly as instructed. Retired: nothing. |
| **Identity and version impact** | One identity, versioned forward — correct, and it avoids the routing ambiguity a second row would create. Note that on promotion the published tree strips `version` and `date` from frontmatter; per-version identity lives in the candidate tree and the changelog, not on a published card. |
| **Provider/dependency contract** | Parent and sole writer by default. `design-taste-frontend` is an optional, isolated, read-only specialist for eligible frontend surfaces only, returning a compact contract. The published card must describe a **provider interface** and degrade gracefully when no provider is installed. It must not require an external installation, and it must not reproduce that provider's doctrine inline. |
| **Deterministic versus subjective authority** | The hard floor is deterministic: behaviour, public interfaces, serialization, side effects and repository checks equivalent before and after. The design objective is subjective and must stay advisory. A hook may route and may require a receipt; a hook may not decide that code is beautiful. |
| **Required evals and ablations** | The current evals carry **no fixture files**, so they cannot demonstrate anything. Replace them with executable contrasting fixtures across genuinely different ecosystems, then run the five-way ablation: repository rules alone; this skill alone; plus architecture and language specialists; plus the frontend specialist on eligible cases; and the full chain. Include restraint cases where no change should win, and an anti-monoculture case that fails a candidate importing one ecosystem's aesthetic into another. Treat a specialist invocation on backend code as a routing failure. |
| **Failure and rollback path** | A candidate in `_quarantine/` ships to nobody, so the rollback is `git rm` of a directory no installer reads. That is precisely why the baseline should land there rather than waiting on the repository's edge. |
| **Evidence ceiling** | Today: nothing. `UNMEASURED` is not available to a card with no `EVIDENCE.md`, and `scripts/validate_scoreboard.py` refuses a card whose controlled fields are missing rather than counting it as unmeasured. With executable contrasting fixtures the card gains a frozen empirical contract and becomes screenable, which is the single lever that raises this ceiling. Without them the ceiling is fixed regardless of how good the treatment is. |
| **Is a changeset justified?** | Yes, but only the `_quarantine/` landing. No publication. |

One warning, stated plainly because the shape is familiar. This candidate is a rich, well-argued
rubric with zero counted occurrences. That is the exact profile of the card this repository
retired on 2026-08-31. The quality of the theory is not the binding constraint; the absence of an
observed failure is.

### 5. `anti-slop-frontend-secure` — DEFER; the deterministic mechanism does not exist

| Field | Finding |
|---|---|
| **Disposition** | DEFER. The condition for admission is a mechanism that is not built. |
| **Current repository artifact and exact version** | `_quarantine/anti-slop-frontend-secure/SKILL.md`, 3,088 bytes, and nothing else — no `EVIDENCE.md`, no `gotchas.md`, no scripts, no fixtures. Registry version `1.3.0-rc.1`. |
| **Demonstrated defect or unmet need** | The card's own provenance comment records the blocking fact: the deliverables table names four scanner scripts in a package "that is NOT attached", and the card is "a faithful transcription of the page's Core Execution Flow; not re-authored". The gate sequence A–E is therefore a checklist a model performs by reading, with no oracle behind it. An instrument is described on both surfaces and implemented on neither. |
| **Smallest proposed changeset** | Build the oracle before touching admission: `scripts/audit_frontend.mjs` and `scripts/emit_csp.mjs`, parser-backed fixtures for each gate, and structured receipts. Then write `EVIDENCE.md` and `gotchas.md` against a real incident. |
| **Files added, modified, preserved, retired** | Added under `_quarantine/`: the two scripts, a fixture set, `EVIDENCE.md`, `gotchas.md`. Modified: `SKILL.md` — the description must be rewritten to the published bar. Retired: nothing. |
| **Identity and version impact** | Identity stable. **The description is 285 characters against the published 200-character bar**, so promotion without a rewrite reds the build at `validate_card_files.py`. Rewrite it as a router, not a summary. |
| **Provider/dependency contract** | Security stays inside this card and stays deterministic: safe DOM construction, network allowlists, content-security policy, secret exclusion. The frontend taste provider is optional, scoped to eligible surfaces, and advisory. The authority split is the stable contract and belongs in `SKILL.md` in one line: **security may block completion; subjective beauty may not.** |
| **Deterministic versus subjective authority** | Cleanly separable, which is what makes this candidate strong once built. Gates A, B, C and E are parser-checkable. Gate D (iconography) and the anti-slop posture are judgement. |
| **Required evals and ablations** | Five arms: with the taste provider, without it, an out-of-scope routing case that must be refused, a provider-failure case that must degrade rather than block, and an unsafe-aesthetic-advice case where the security gate must override the provider. Fixtures must be parser-backed, not string-matched. |
| **Failure and rollback path** | Contained: nothing ships until promotion, and the scripts are new files with no existing caller. |
| **Evidence ceiling** | **The highest of the three addition candidates.** A deterministic document-object-model, policy and network check is a tier-1 oracle shape, and `AGENTS.md` step 4 states that a frozen empirical contract — fixture and counterfixture — is the only shape the measurement harness returns a real verdict on. Built properly, this card can earn a measured verdict rather than an honest `UNMEASURED`. |
| **Is a changeset justified?** | Not yet. File the build as a ticket. |

### 6. `walk-the-recipe-as-target-user` — DEFER; rebuild, and note it is already screenable

| Field | Finding |
|---|---|
| **Disposition** | DEFER. Rebuild against the stated conditions, then promote. |
| **Current repository artifact and exact version** | `_quarantine/walk-the-recipe-as-target-user/SKILL.md`, 11,495 bytes. No `EVIDENCE.md`, no `gotchas.md`. Registry version `1.1.0-rc.1`. |
| **Demonstrated defect or unmet need** | The discipline is sound and the card is well written. It fails admission on record, not on content: no occasions counted, no evidence file, and no clean-environment replay has been run. |
| **Smallest proposed changeset** | Add recipe and environment hashes, clean-state replay, prompt-injection isolation, secret and network boundaries, destructive-action gates, and tamper-evident receipts. Then run one actual fresh-environment rerun and record it. |
| **Files added, modified, preserved, retired** | Added: `EVIDENCE.md`, `gotchas.md`, a receipt schema and fixtures. Modified: `SKILL.md`, substantially. |
| **Identity and version impact** | Identity stable. Three promotion-blocking properties measured here, all mechanical: the **description is 1,151 characters** against the 200-character bar; the frontmatter carries a **`metadata:` block** which `AGENTS.md` step 2a records as *not* caught by `validate_spec_conformance.py` because it is specification-legal, so stripping it is manual and easy to miss; and `SKILL.md` at 11,495 bytes is well over the ~7 KB authoring ceiling, which `AGENTS.md` states plainly is **unenforced** — a convention breach, not a gate failure, and it should be reported as such rather than as a blocker. |
| **Provider/dependency contract** | None required. Isolation is the dependency: the replay needs a declared clean environment, and the card must refuse rather than guess when it cannot get one. |
| **Deterministic versus subjective authority** | Strongly deterministic. Hashes, replay, receipts and command output are all checkable. The judgement is confined to naming the target-user profile. |
| **Required evals and ablations** | The publication test is already stated correctly: it must find hidden assumptions **without** misclassifying an environment the recipe explicitly declared unsupported. That negative case is the one that decides it, and it must be in the fixture set. |
| **Failure and rollback path** | Contained in `_quarantine/`. |
| **Evidence ceiling** | High, and higher than the registry row implies. `AGENTS.md` step 4 names this candidate **by name** as one of exactly two in the collection that carry a frozen empirical contract and therefore qualify for a screen today. The registry does not carry that fact. It raises this candidate's priority relative to `self-documenting-code`, which is not screenable at all until its fixtures exist. |
| **Is a changeset justified?** | Not yet. File the rebuild as a ticket, and note the screen eligibility on it. |

### 7. `t1-review` — DEFER; later, and declare two exposures before it ships

| Field | Finding |
|---|---|
| **Disposition** | DEFER. Correctly ordered behind the two candidates above. |
| **Current repository artifact and exact version** | None in this repository. It exists as a local operator-invoked install and a registry row at `1.0.0-rc.1`. |
| **Demonstrated defect or unmet need** | The need is the collection's own independence doctrine, which is real. The blocker as filed is that the predecessor workflow prompts for refutation in a way that biases the panel, and that provider handling, abstention, retry, cost and cycle states are unhandled. |
| **Smallest proposed changeset** | None against this repository until the rebuild exists. When it does: consume `PROVIDER-ENVELOPE.md` rather than inventing a second protocol, and keep challenge generation separate from source adjudication and repair disposition. |
| **Files added, modified, preserved, retired** | None yet. |
| **Identity and version impact** | Keep it a separate identity from the disposition schema. The two answer different questions — one shapes returns so they join, the other generates and adjudicates challenges — and merging them would create the composition-orchestrator identity this review is instructed to refuse. |
| **Provider/dependency contract** | **This is the admission problem the filed blocker does not name.** Execution requires an external paid model gateway and a user-supplied key with a spend cap. Under `ADMISSION.md` criterion 3 that is partly an access-layer concern, not purely a skill one. Not fatal — a card may carry the method and declare the provider — but the card must state that a reader without a key and without spend authorisation cannot run it, and it must not present provider labels as independence. |
| **Deterministic versus subjective authority** | Almost wholly subjective, and that must be labelled. A cross-family objection is a candidate falsification, never a verdict. Aesthetic and value findings stay labelled as such. Agreement across providers is not truth. |
| **Required evals and ablations** | Verified catches must exceed false-objection burden and incorrect reversals, measured, not asserted. Record empty, failed, unavailable, retry, abstention, cost and latency states, and preserve raw responses before normalization. |
| **Failure and rollback path** | Not yet applicable. |
| **Evidence ceiling** | Constrained by a governance exposure that should be declared in `EVIDENCE.md` rather than discovered later: this is the instrument that adjudicates the collection's own contestable value judgments. `AGENTS.md` states the **No self-authority** rule binds hardest where a card sits in the repository's own machinery. Publishing it makes the adjudicator a subject of the collection it adjudicates. Declarable, not disqualifying. |
| **Is a changeset justified?** | No. |

### 8. `anti-vibe-codex` — DEFER; the presumptive disposition is confirmed, and the prior is unfavourable

| Field | Finding |
|---|---|
| **Disposition** | DEFER until comparative evidence exists. Confirmed as filed. |
| **Current repository artifact and exact version** | None. Registry row at `1.1.0-rc.1`. |
| **Demonstrated defect or unmet need** | None recorded. The hazards named — silent scope expansion, unnecessary questions, over-stopping, unrequested tests, unrelated cleanup, irreversible actions — are plausible and uncounted. |
| **Smallest proposed changeset** | None. Run the comparison first: the card against the current model's ordinary scope instruction, on hazard-present tasks. |
| **Files added, modified, preserved, retired** | None. |
| **Identity and version impact** | None. |
| **Provider/dependency contract** | None. |
| **Deterministic versus subjective authority** | Mixed and awkward: "did it stop at the boundary" is checkable; "did it stop too early" needs a judge. The evaluation cost is therefore higher than it looks. |
| **Required evals and ablations** | Exactly the filed set, plus the completion-rate and latency counter-measures, so that a card which buys control by refusing work is caught rather than credited. |
| **Failure and rollback path** | Not applicable. |
| **Evidence ceiling** | **Low, and this is worth stating before anyone spends on it.** The comparison it must win is a transformative-lift screen against a frontier model's own scope instruction. This collection's record across 26 screens is zero production keeps, because production skills ceiling at a null-arm pass rate of 1.00. A scope-discipline card measured against built-in scope discipline is a high-probability ceiling, which returns `CANT_TELL_YET`, not a verdict. Run the cheap comparison **before** building the card, not after. |
| **Is a changeset justified?** | No. |

---

## Exclusions confirmed

Each was checked against this repository rather than accepted on the filing.

| Candidate | Confirmed | The rule that settles it |
|---|---|---|
| `design-taste-frontend` | REJECT as a published card | Upstream-owned external work. This repository already consumes it correctly — commit `d45d59d` vendored and hash-pinned it as a **style**, scoped. Compose it; do not republish another author's skill under this collection's identity. |
| `quick-note-router` | REJECT | Registry `Platform` reads Notion AI. `.claude-plugin/marketplace.json` ships cards into a Claude Code plugin mechanism that cannot install a card for a different runtime. Wrong platform, not a wrong idea. |
| `epistemic-cultivation` | REJECT | Same, and additionally an active instruction source in its own workspace rather than a portable card. |
| `session-close` | REJECT — subsumed | This repository already ships **both halves**: `skills/engineering/im-down` and `skills/engineering/im-up`, sharing eight files under a parity gate, with a poison control asserting the producer refuses a stale packet. The row's own blocker asks to "resolve overlap with im-down and choose one canonical producer contract". The repository chose. A third identity would break the parity pair, and the parity suite reports NOT VERIFIED **while still exiting zero**, so the breakage would be quiet. |
| A generic dynamic-skill, taste-wrapper, or composition-orchestrator identity | REJECT | No independent trigger, no terminal outcome, no occurrence. Fails all four admission questions. These are architecture patterns and shared contracts; the contract belongs in `PROVIDER-ENVELOPE.md`, which is where this record puts it. |
| Prompt-only revisions to narrow trap skills | REJECT | `AGENTS.md` step 3 lists four criteria that put a card into repair and states that "it reads fine" is not a disposition. The inverse holds equally: mentioning composition is not one of the four criteria. Leave the trap cards narrow until a concrete failure requires a change. |

## What this record authorises

1. **One changeset against a published card**: the namespaced-identity rule and
   `PROVIDER-ENVELOPE.md` in `parallel-review-disposition-schema`, justified by that card's own
   `[OBSERVED]` gotcha of 2026-08-17.
2. **One convention change**: the expanded topology list in `AGENTS.md`, as the correct home for
   the retired gate card's remaining useful content.
3. **One candidate landing**: `self-documenting-code` `0.1.0` into `_quarantine/` with provenance,
   so later versions accrue history here.
4. **Four tickets, no code**: the `anti-slop-frontend-secure` oracle build; the
   `walk-the-recipe-as-target-user` rebuild, flagged as screen-eligible; the
   `subagent-research-reliability` platform-claim re-verification under the repair gate; and the
   `anti-vibe-codex` cheap comparison, to be run before anything is built.

It authorises no rename, no overwrite of a published artifact, no `EVIDENCE.md` change, no
trigger broadening, and no publication.

## Registry reconciliation

Four registry properties disagree with this repository and should be corrected at the source,
which is the maintainer's call:

- `skill-necessity-gate`: `Lifecycle` should read Retired, `Status` Deprecated, and the
  `Source URL` should be re-pointed at `blob/v1.3.0/` or cleared. It currently points at a path
  that does not exist on `main`.
- `Version` on published rows: `1.4.0` is the collection version, not a card property. Published
  cards carry no version key. Read the field as "the collection release in which the card last
  changed", or leave it empty.
- `Lifecycle` and `Source URL` on every published row should be derived from
  `git ls-files 'skills/**/SKILL.md'` rather than maintained by hand. A hand-maintained mirror of
  a tree drifts silently, and this review found the drift only because it read the tree first.
- `subagent-research-reliability` and `parallel-review-disposition-schema` rows record standing
  costs of 40 and 100 tokens respectively, which match the cards' own `EVIDENCE.md`. These agree;
  they are noted so the disagreements above are not read as a general indictment.
