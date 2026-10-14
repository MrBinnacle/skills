# Product contract: capability, context, runtime and evidence

**Status:** Proposed internal product contract, 2026-10-14. This is architecture for review, not approved public copy, a frozen cross-repository API, or a claim that the full product exists today.

## 1. Purpose

Help an operator determine which control, if any, fits a real workflow; deliver it through a supported runtime; and retain enough evidence to know what was delivered, what happened, and what can be claimed.

A skill is one capability type and current distribution format. It is not the product boundary.

Keep five contracts distinct:
1. **Capability behavior:** purpose, trigger, inputs, steps, output, stop conditions and failure behavior.
2. **Knowledge/context:** source, status, scope, freshness, relations and conflict rules for information used by selection and execution.
3. **Runtime delivery:** discovery, loading, settings, actual delivery evidence and runtime-specific limits.
4. **Evaluation:** claim, mechanism, arm contrast, fixture, subject/runtime, detector, oracle, qualification and admissibility.
5. **Lifecycle/release:** canonical source, artifact identity, derived-package refresh, re-check and retirement.

Share identifiers and links across these layers. Do not force them into a single schema or implementation.

## 2. Responsibility boundaries

| Surface | Owns | Does not prove |
| --- | --- | --- |
| This repository | Canonical published capability files, admission/retirement records, and release content | Efficacy of a published capability |
| Notion knowledge base | Structured context, source references, working hypotheses, accepted decisions and cross-links | Current installed files, runtime state, code or measurement results |
| `skill-harness` | Runtime adapters, capture/parsing, qualification, oracles, receipts, admissibility and scientific dispositions | The public capability catalog or equality of runtime behavior |
| Pi | First selected implementation of the owner's direction to own the agent layer and keep models/providers replaceable | Scientific authority or proof that every distribution adapter exists |
| Claude Code | Current compatibility and distribution target, including its plugin/runtime behavior | Governing architecture for every future runtime |
| Pi distribution surface, referred to here as `skills-pi` | Future packaging/configuration route if this is the intended target | A second independently edited copy of capability behavior |

The Pi subject adapter already exists in `skill-harness` and was apparatus-verified. That does not establish that a separate `skills-pi` package, installer, or distribution repository is complete. Its owner-controlled repository/path is **not verified in the currently accessible repository inventory**. Locate the intended destination before editing or creating packaging artifacts. Do not substitute a similarly named third-party project.

### Source-of-truth rules

- Edit canonical capability content in its owning repository. A runtime package may point to, package or deterministically derive from it, but must not silently become another authoring source.
- Repository HEAD, release files, tests and receipts own current shipped/implemented/measured facts.
- Notion carries broader context that should not be loaded wholesale into every session. Each knowledge item that informs a decision must retain source, status and scope.
- If GitHub, Notion, a local install or runtime capture disagree, preserve the disagreement and resolve it deliberately. Do not overwrite the newest-looking surface just to make them agree.
- Admission, applicability, delivery, invocation and efficacy are different states.

## 3. Capability behavior contract

Use detail proportional to consequence and side effects.

| Field | Meaning |
| --- | --- |
| **Identity** | Stable capability ID/name, owning repository/path, canonical content digest, version/release when one exists |
| **Trigger** | The job and situation in which the capability should be considered |
| **Applicability** | Preconditions, exclusions, and evidence needed to establish fit |
| **Inputs** | Minimum required information, separating required from optional |
| **Procedure** | Steps, authority boundaries and stop conditions |
| **Output** | Concrete result shape and any status, path or receipt required |
| **Failure mode** | Exact behavior for missing input, stale context, conflict, refusal or incomplete execution |
| **Source authority** | Governing rule/source and conflict precedence |
| **Effects and permissions** | Files, settings, commands, APIs and user-visible changes the capability may affect |
| **Cost** | Standing context cost, invocation cost where measured, setup/update costs and unknowns |
| **Verification** | Positive case, negative/countercase, unknown/failure case, expected output and dated test/receipt |
| **Lifecycle** | Conditions for re-check, supersession, disablement or retirement |

`ADMISSION.md` remains binding for **skill cards**, with “not admitted” as the default. It does not automatically govern hooks, setup tooling, runtime adapters or other control types. A non-skill control needs a named owner, scope, failure contract and verification path.

A simple one-shot transform may use a light trigger/constraints/output contract. Routing, side effects, refusal or cross-session work require the fuller contract. Do not fill irrelevant fields merely to satisfy a checklist. The existing Notion “Skill Contract Template” is historical design input, not this cross-runtime product contract; reuse its fields where they fit and add runtime, identity, cost and provenance requirements.

## 4. Knowledge/context contract

The knowledge base is a context plane, not execution truth or an unbounded prompt dump.

Each item used to justify a recommendation/action should have:

- **Identity:** stable page/item ID and canonical source URL or repository path.
- **Type/status:** observed fact, source excerpt, accepted decision, hypothesis, proposal, implementation status or superseded material.
- **Scope:** projects, runtimes, environment or capability types it applies to.
- **Authority:** source of record and precedence when sources conflict.
- **Provenance:** origin and supporting artifact/quotation/receipt.
- **Freshness:** last checked date or an event that triggers re-check; page edit time alone does not prove current validity.
- **Relations:** links to capability, project, runtime, decision, evaluation or receipt.
- **Access boundary:** whether the item can be surfaced to the current runtime or public repository.
- **Conflict behavior:** report unresolved conflicts; do not average incompatible claims or select the newest text by default.

Retrieval rules:
1. Retrieve the smallest context set that can settle the current decision.
2. Carry sources and status into the result or handoff.
3. Missing, inaccessible, stale or contradictory required context yields an explicit unknown/refusal and states what evidence is missing.
4. Separate global operating rules, project facts, reusable procedures and task-specific scope.
5. When implementation or an accepted decision changes, reconcile the corresponding knowledge record and links. The record does not create the implementation.

The current Notion “Skills Library and Global Context” database already has separate skill and global-context data sources and a relation between them. Preserve that separation. Audit real relation coverage, duplication and freshness before changing its schema; do not assume that a relation field means the links are complete.

## 5. Cross-runtime delivery contract

### Architecture

The durable decision is to own the agent layer and keep models/providers replaceable. Pi is the first implementation, not the principle itself. If Pi proves inadequate, replace it without surrendering the ownership principle.

Claude Code remains a current compatibility/distribution route, not the governing architecture for every runtime.

The [Agent Skills specification](https://agentskills.io/specification) defines a shared `SKILL.md` package convention. [Pi's skill docs](https://pi.dev/docs/latest/skills) state that Pi implements the specification; [Pi package docs](https://pi.dev/docs/latest/packages) and [Pi configuration docs](https://pi.dev/docs/latest/configuration) describe its distribution/configuration routes. [Claude's skill docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) describe Claude's format and loading behavior. These pages were checked 2026-10-14. Shared format does **not** prove identical discovery, settings, activation, permissions, loading, invocation or behavior.

**Documented route differences (not yet a product compatibility claim):**

| Runtime | Documented discovery/delivery options | Product implication |
| --- | --- | --- |
| Pi | User skill directories `~/.pi/agent/skills/` and `~/.agents/skills/`; project `.pi/skills/` and `.agents/skills/`; package, settings and explicit CLI skill paths. Pi packages can be installed from npm, Git or a local path and can expose skill resources. | A future `skills-pi` route could be a thin Pi package or shared-directory config. Choose only after locating the intended owned target and proving the actual loaded context. |
| Claude Code | Personal `~/.claude/skills/`, project `.claude/skills/`, and plugin-based distribution. This collection currently documents Claude Code plugin installation and the `npx skills add` route in its [README](https://github.com/MrBinnacle/skills/blob/main/README.md). | Preserve the current supported distribution route. Plugin install/cache/version semantics are distinct from Pi package installation and need their own proof. |

These docs establish the available mechanisms at the platform level. They do not establish which route has been tested for every capability in this collection or whether the model received the expected capability description/body in a given run.

### Required declaration per supported route

| Field | Required evidence |
| --- | --- |
| Runtime identity | Runtime/version and executable or package that actually ran |
| Distribution route | Exact plugin, Pi package, shared directory, configured path, or launch route |
| Canonical source | Repository/path, content digest, and derived package revision if any |
| Adapter identity | Adapter/package version and digest if code transforms or mediates the source |
| Discovery | Configured paths and capabilities the runtime actually found |
| Effective availability | Names/descriptions or equivalent capability index actually supplied to the model |
| Content delivery | Evidence that full instructions and referenced resources were accessible at the runtime boundary |
| Invocation | Observable event/tool behavior plus declared coverage limits |
| Model/provider epoch | Actual model/provider, relevant settings and any identity change during the run |
| Environment | Working directory, isolation, allowed tools and other settings that affect behavior |
| Capture identity | Observation surface/channel, version, raw content hash and semantic digest |
| Result | Delivered, not delivered or unknown, with evidence and reason |

Not every ordinary use needs a scientific receipt. Every efficacy claim does. Do not invent evidence a host runtime does not expose.

### Canonical content and derived packages

- Keep one canonical editable source for each capability.
- Prefer adapters that point to or package source unchanged. Any transformation must be deterministic, tested, identified and attributable to the canonical digest.
- Do not fork Pi and Claude Code copies merely because discovery paths differ.
- Material runtime-specific behavior must have its own explicit variant, identity and verification. Different content must not be labelled the same artifact.
- Exercise actual installation/discovery from a clean setup, including failure and rollback. A file on disk, green build or installer exit code does not prove delivery to the model.
- Untested routes are unknown/unsupported, not “probably compatible.”

## 6. Applicability, delivery, behavior and efficacy

| Question | Example state | Evidence |
| --- | --- | --- |
| Does it apply here? | `APPLICABLE`, `NOT_APPLICABLE`, `APPLICABILITY_UNKNOWN` | Environment facts and stated preconditions |
| Was it delivered? | `DELIVERED`, `NOT_DELIVERED`, `DELIVERY_UNKNOWN` | Runtime-bound discovery/context evidence |
| Was it invoked or did its mechanism activate? | Runtime event or existing typed activation state | Declared observer, detector validity and coverage |
| Did the consequence occur? | Oracle/consequence result | Pre-registered task/fixture and valid oracle |
| Did the intervention change the result? | Registered scientific disposition | Admissible experiment for the named estimand |

These are descriptive distinctions, not a mandate to add new enums to `skill-harness`. Reuse existing typed states. Applicability unknown must not be recoded as `UNMEASURED` or `CANT_TELL_YET`, which concern efficacy evidence, not environment fit.

An installed or delivered skill is not thereby effective. Under a delivery-verified treatment-policy contrast, a skill may be exposed even if it is not invoked. A task finishing does not prove that the target hazard occurred or was prevented.

## 7. Evaluation/evidence contract

The existing measurement instrument owns the experiment, admissibility and scientific verdicts. Product selection and runtime adapters provide accurate inputs rather than cloning this machinery.

Before a sized experiment can spend, its registered claim must match:

- **Estimand and target:** the intended effect and its permitted interpretation.
- **Production mechanism:** the actual control responsible for the claimed behavior.
- **Arm contrast:** the mechanism that differs between arms.
- **Task/fixture:** a world where the target condition is reachable, with valid consequence/oracle.
- **Subject/runtime:** actual runtime/version, model/provider epoch, settings and relevant configuration.
- **Delivery/activation observer:** capture surface, detector identity and evidence it distinguishes target activation from lookalikes.
- **Qualification receipt:** admissible evidence matched to task/fixture and subject/runtime, meeting the registered hazard-entry floor.
- **Spend authorization:** ratified budget and projected cost.
- **Receipt chain:** registration, task/fixture, content, adapter, capture/parser and oracle identities.

Missing, stale, mismatched, below-floor or invalid qualification evidence must refuse spend before the first paid model call. The proposed pre-spend contract remains pending its required independent review and landing; this is the intended product requirement, not a claim that the current launch gate enforces every condition.

The Pi adapter already implemented in `skill-harness` translates Pi-native evidence into the existing `ParsedEvalLog` / `ParsedSample` seam; shared admissibility, oracle, storage and aggregation remain downstream. Apparatus verification does not establish a sized Pi efficacy result. See [the Pi adapter](https://github.com/MrBinnacle/skill-harness/tree/main/src/skill_harness/subject/pi), [#421](https://github.com/MrBinnacle/skill-harness/issues/421), [#438](https://github.com/MrBinnacle/skill-harness/issues/438), [#620](https://github.com/MrBinnacle/skill-harness/issues/620) and [#621](https://github.com/MrBinnacle/skill-harness/issues/621).

Pi and Claude Code can implement the same scientific contract while remaining different apparatuses. Report runtime-stratified results unless a registered equivalence measurement supports pooling. Same model, same `SKILL.md` or similar scores alone do not establish equivalence.

## 8. Release, freshness and retirement

- Adapter release records the exact canonical content revision and supported runtime versions.
- Changed source bytes invalidate dependent packages/tests until they are refreshed or re-verified.
- Runtime, parser, capture, discovery, packaging, model-delivery or oracle changes trigger the relevant scope-specific re-check.
- Retain origin, applicability, cost, evidence status, limits and re-check/retirement trigger for every capability.
- Disable or retire when preconditions cease to hold, delivery no longer works, a registered platform change removes the failure, or the owning policy supports removal.
- Preserve historic receipts; do not rewrite old results to match current code.

## 9. Acceptance gates

This becomes governing policy only after independent review and concrete tests for each boundary.

1. Review against current `PRODUCT.md`, `ADMISSION.md`, runtime docs/code, measurement implementation and Notion schema.
2. Inventory actual delivery paths for canonical Skills content, Pi, Claude Code and the intended `skills-pi` surface. Record owner/path/version or mark unknown.
3. Prove canonical artifact identity across supported routes; equal names do not suffice.
4. From clean setups, prove runtime discovery and actual effective context with positive, negative and unknown cases. No efficacy spend.
5. Map canonical capabilities to Notion Global Context and Capability Menu read-only first. Check source, status, scope, freshness and conflicts before schema changes or automated writes.
6. Connect evaluation through the current instrument's adapter/capture/receipt/oracle/admissibility path; do not create a second scientific engine.
7. Only then choose whether a dedicated `skills-pi` package exists, needs to be created, or should remain a thin route into canonical content.

Acceptance scenarios must include: known applicable, known inapplicable and missing-context selection; delivery verification under Pi and Claude Code or an explicit incompatibility; refusal for missing/stale/mismatched observation; adapter/capture identity drift detection; a task that completes without entering the target hazard; and both a refusal path and a valid matched positive path. No applicability state may be presented as an efficacy verdict.

## 10. Open items and revisit conditions

The intended owner-controlled location for `skills-pi` is unverified; discover it before creating/editing packaging artifacts. Supported version matrices and clean-install procedures for Pi and Claude Code must be specified from current sources and tested. Notion relation coverage/freshness needs an audit before schema changes. Public name, audience and commercial model remain undecided and unvalidated.

Revisit this contract if the specification or runtime discovery semantics change, if a runtime cannot expose required evidence, if the knowledge base cannot carry provenance/freshness without a justified schema change, or if a live prototype shows the identity/delivery model duplicates existing machinery.
