# Product thesis: an evidence-governed reliability system for delegated AI work

**Status:** Strategic direction authorized by the owner on 2026-10-13. This is an internal product-design artifact, not approved public copy. It establishes a direction to test; it does not establish market demand, external adoption, or efficacy.

## Decision

Do not define the product by the file format currently used to ship it.

Build toward a system that helps an operator determine which control, if any, is appropriate for a real agent workflow; provide that control at the correct layer; establish that it addresses the intended failure mechanism; and keep its scope, cost, evidence, and retirement conditions visible as the workflow changes.

Skill cards remain a core deliverable. They are one intervention format inside the product, not the boundary of the product.

## The operator's job

When an agent performs work outside the operator's direct observation, the operator needs to decide:

- What can go wrong in this workflow and under which conditions?
- Is the workflow actually exposed to that failure?
- Is a control warranted, and which layer should own it?
- What does the control change, what does it leave unchanged, and what will it cost?
- What evidence says that the control's intended mechanism was exercised and the result supports the claim?
- What would make the control irrelevant, stale, too expensive, or worth removing?

The product should reduce the distance between a reported problem and a justified control decision. A larger catalog is not, by itself, progress.

## The product loop

The intended operator journey is:

1. **Describe or inspect the actual environment.** Identify the runtime, project setup, relevant configuration, workflow and constraints from checkable sources wherever possible. Missing or inaccessible information returns `APPLICABILITY_UNKNOWN`, not a guess presented as fact.
2. **Classify the failure and exposure.** Separate a failure that occurred from a hypothetical risk. Identify the condition that makes the failure reachable, and distinguish exposure from a card invocation or a final outcome.
3. **Choose the control layer.** The answer may be no intervention, a standing instruction, a project rule, a skill, a hook or guard, a deterministic test or validator, a setup change, or a workflow procedure. Do not force every problem into a skill.
4. **Deliver the appropriate intervention.** State the actual behavior, prerequisites, scope, delivery route, side effects and costs. Do not infer support for a platform or install route that has not been checked.
5. **Qualify before evaluating.** Bind the claimed effect to the production mechanism and the intervention varied by the experiment. Establish that the target condition is reachable, the activation detector is valid, and the oracle can distinguish non-engagement from successful prevention before spending on a sized evaluation.
6. **Observe and adjudicate.** Keep activation, consequence, task completion, treatment exposure and invocation distinct. Use the relevant instrument for the claim. When the evidence does not identify the claim, preserve `UNMEASURED` or `CANT_TELL_YET`.
7. **Maintain the control.** Preserve origin, version, applicability, evidence, known limits, standing cost, dependencies and the condition that triggers re-check, replacement or retirement.
8. **Make the operator's next action explicit.** The result should say what to install, configure, test, leave alone, revisit or remove, and the evidence for that choice.

Every transition is a potential failure point. The product is incomplete if it records the correct process but does not establish that the required process actually ran.

## Product components

These are functional roles, not a commitment to place every component in this repository.

| Component | User-facing job | Required evidence boundary |
| --- | --- | --- |
| Environment and exposure profile | Establish which conditions apply to this user's real workflow | Facts from inspectable sources; explicit unknowns; scope and timestamp |
| Control catalog | Show what each candidate changes and where it belongs | Stable identity, prerequisites, control layer, cost, scope and evidence state |
| Delivery and setup | Apply only the chosen controls through a supported install/configuration path | Verified route, user approval for changes, observable result and rollback path |
| Control specification | State what the intervention is intended to prevent or change | Target failure, active preconditions, activation definition, consequence and claim boundary |
| Evaluation and receipts | Determine whether the claim can be measured and what was observed | Matched task/fixture and subject/runtime, valid detector and oracle, provenance and typed outcome |
| Lifecycle management | Keep useful controls current and remove stale or unnecessary ones | Re-check triggers, supersession rules, version identity and recorded disposition |
| Reader verification | Let someone outside the authoring process check the claim | Reproducible evidence path; no claim stronger than the artifact supports |

A candidate does not become valid merely by fitting one of these rows. Each component must address a real operator decision and have an explicit way to check its own claims.

## The control catalog is broader than cards, but not unbounded

The catalog should represent the **right control**, not merely the available card. Initial control types to consider are:

- **Instructional:** skill cards, standing instructions and project-specific rules.
- **Deterministic:** hooks, guards, validators, tests and other controls whose decisions can be checked without an LLM judge.
- **Procedural:** handoffs, session boundaries, recovery recipes and other workflows that coordinate people or agents.
- **Selection and setup:** environment-aware recommendations and configuration that install or enable only what applies.
- **Evaluation:** task/fixture contracts, activation detectors, consequence checks, oracles and evidence receipts.

These types have different risk, deployment and evidence requirements. They should not be forced into a shared card schema merely for uniformity. The admission policy remains authoritative for skill cards. A different intervention type needs a suitable contract and admission path of its own before it becomes a deliverable.

A result of **no control needed** is valid. So are **not applicable** and **cannot tell**. Do not optimize the product to always recommend an intervention.

## Evidence rules carried forward from current work

The current repository already separates several axes. The wider product must preserve them rather than flatten them into a single confidence badge.

- **Origin is not effect.** `OBSERVED`, `DESIGNED` and `DISTILLED` describe where a card came from; they do not rank efficacy.
- **An observed unaided failure is not proof that the intervention fixes it.** Admission and effect are distinct decisions.
- **A successful task may not exercise the target hazard.** In that case the run cannot establish prevention of that hazard.
- **Exposure, invocation and outcome are not synonyms.** A description or other treatment surface may affect behavior without the card body being invoked.
- **The experimental contrast must vary the claimed mechanism.** An ablation of skill text does not establish the effect of a production guard active in both arms.
- **An activation detector must detect activation.** Lexical lookalikes or explicit safe variants must not count as the target event.
- **Qualification is not efficacy.** A valid preflight establishes that the planned claim may be identifiable; it does not establish the claim's truth.
- **A review procedure is not a completed review.** The required independent seat, actual invocation, output and adjudication record must exist before the work is said to have passed review.
- **A green check proves only the property that check actually measures.** An unobserved surface, unchecked assumption, or failed-to-run process must remain visible.

The currently proposed intervention-mechanism preflight RCA in the sibling research workspace proposes a pre-spend qualification requirement and mechanism binding. It remains a proposed research finding until its prescribed independent review and landing conditions are met. No new control or efficacy conclusion should be inferred from the proposal alone.

The supporting implementation history is in [skill-harness #421](https://github.com/MrBinnacle/skill-harness/issues/421), [#438](https://github.com/MrBinnacle/skill-harness/issues/438), [#620](https://github.com/MrBinnacle/skill-harness/issues/620), and [#621](https://github.com/MrBinnacle/skill-harness/issues/621). The product work here should consume those controls and accepted contracts, not create duplicate machinery.

## Repository and system boundaries

Product unity should come from the operator journey and explicit cross-component contracts, not from merging repositories for cosmetic consistency.

| Surface | Owns | Does not automatically own |
| --- | --- | --- |
| This Skills repository | The intervention catalog, skill cards, portable operating-rules template, admission/retirement record, and operator-facing adoption work | The internals of the measurement instrument or the entire research process |
| Sibling measurement instrument | Evaluation execution, activation detectors, oracles, receipts, statistical dispositions and related validation machinery | The owner-facing product direction or public card inventory |
| Research and decision workspace | Research provenance, method development, cross-repository synthesis, and proposals for changes | Product claims that have not been accepted and implemented at the relevant surface |

Before adding a capability, find the current owner and implementation. Link or wrap an existing capability when that preserves its contract. Duplicate machinery only when there is evidence that a required boundary cannot be met by the existing component.

The Skills repository can become the user-facing catalog and adoption surface for a wider system without absorbing all implementation into it. A future change to that boundary requires a concrete dependency or user-journey reason.

## Runtime stance: Pi first, Claude Code compatible

The durable architectural decision is to own the agent layer and keep model/provider choice replaceable. Pi is the first implementation of that decision, not the decision itself. If the Pi implementation is wrong for the job, replace it without surrendering the ownership principle.

Claude Code remains a supported compatibility and distribution target because the existing collection ships through its skill/plugin ecosystem. It is not the governing architecture for every runtime.

The open [Agent Skills specification](https://agentskills.io/specification) provides a shared `SKILL.md` format. [Pi documents that it implements the specification](https://pi.dev/docs/latest/skills); [Claude documents its own format and loading behavior](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). A shared format allows canonical capability content to be reused, but it does not establish identical discovery, activation, settings, permissions, loading, invocation, or behavior. Each supported route needs an adapter declaration and evidence of actual delivery.

The Pi subject adapter already implemented in [skill-harness](https://github.com/MrBinnacle/skill-harness/tree/main/src/skill_harness/subject/pi) is the scientific execution adapter. It captures Pi-native evidence, normalizes it to the existing `ParsedEvalLog` seam, and leaves shared admissibility/oracle/aggregation authority downstream. That apparatus work does not mean a separate `skills-pi` package, installer, or repository is complete. The intended owned distribution path is unverified and must be located before packaging work is started. No sized Pi efficacy result is established by adapter validation.

## Knowledge base: context, not execution truth

The existing Notion Skills Library and Global Context data sources should become an explicit context plane, not another copy of runtime files or a large block of always-loaded instructions.

Notion can retain durable context, source references, working hypotheses, accepted decisions and relationships between capabilities and global knowledge. The canonical GitHub files determine current published capability bytes; runtime observations determine what was actually discovered or delivered; tests and measurement receipts determine what was measured. A Notion project description cannot override those sources.

The integration must retain item identity, kind/status, scope, source authority, provenance, freshness or re-check trigger, relationships and access boundaries. Retrieval should return the smallest relevant context set. Missing, stale or conflicting context must produce an explicit unknown state instead of a guess. Audit existing relation coverage and data quality before expanding the Notion schema or automating writes.

## The cross-layer contract

The [product contract](product-contract.md) separates five interfaces: capability behavior, knowledge/context, runtime delivery, evaluation, and lifecycle/release. The shared artifact identity is not the delivery receipt; the delivery receipt is not invocation evidence; invocation is not an efficacy verdict.

The contract gives each piece a clear owner and a testable boundary. It does not authorize a duplicate experiment engine or make new runtime and efficacy claims. Product unity comes from shared identity, provenance and handoffs across the components.

## Existing assets that make this direction plausible

The current repository already contains building blocks beyond a set of `SKILL.md` files:

- A base operating-rules template for the global behavior layer.
- An admission policy that can reject a proposed skill because a skill is not the correct control surface or the unaided failure is absent.
- Evidence records, a retirement register, a glossary and rules for preserving claim provenance.
- Deterministic validators and repository-level release and conformance checks.
- Multiple delivery routes with distinct install, enablement and update behavior.
- A live but unresolved proposal in [#407](https://github.com/MrBinnacle/skills/issues/407) to inspect a user's setup and recommend which controls to enable.

This establishes that there are candidate assets for a wider product loop. It does not establish that the loop already works end to end, or that a user wants every proposed component.

## First work sequence

### 1. Establish and independently review the product contract

Use [the product contract](product-contract.md) as the proposed cross-layer boundary and this thesis as its product rationale. Review both against `PRODUCT.md`, `ADMISSION.md`, `BRAND.md`, `DESIGN.md`, current runtime documentation/code, `skill-harness`, and the existing Notion schema. Resolve duplicate and conflicting rules before implementation. The public product surfaces remain unchanged in this step.

### 2. Resolve the existing setup idea within the full journey

Use [#407](https://github.com/MrBinnacle/skills/issues/407) as the starting point rather than opening a competing setup ticket. Re-verify the live install and settings documentation for each supported route. Determine what can be observed and changed, at what granularity, and with what user authorization. If only plugin-level configuration is available on one route, the recommendation must say plugin-level.

### 3. Prototype one small environment-aware selector

Use a small, throwaway prototype before building a general configurator. Start with a limited set of candidate controls and a real clean installation. Require evidence-backed outputs such as `APPLICABLE`, `NOT_APPLICABLE` and `APPLICABILITY_UNKNOWN`, with rationale, evidence source, per-control context cost, and the exact unit that can be enabled or disabled. These are proposed selector states, not a measurement verdict enum: `APPLICABILITY_UNKNOWN` must remain distinct from `CANT_TELL_YET` (an unresolved efficacy disposition) and `UNMEASURED` (no admissible measurement).

Include positive and negative controls: one setup that should trigger a recommendation, another that should not, and a case with missing evidence. A polished screen is not evidence that the recommendation is correct.

### 4. Join selection to valid evaluation

After the cross-repository pre-spend qualification and mechanism-binding work is accepted in its source repository, connect the product contract to those existing mechanisms. The setup flow must not claim a control works merely because it is applicable or was installed.

### 5. Test the whole operator journey

Use a clean install and real, representative project profiles. Observe the path from discovery through setup, invocation, verification, update and removal. Treat install failures, unsupported configuration and missing evidence as product failures or explicit unknown states. Reuse live reference products and primary platform documentation to learn from actual behavior rather than choosing an interface by taste alone.

### 6. Generalize only after the narrow path works

Only after the prototype can correctly select and explain controls should the project widen runtime support, regroup plugins, generalize control schemas, or add a broader setup interface. Each expansion should be tied to a demonstrated need and a verification strategy.

## Proposed measures of product quality

These are candidates for future validation, not current results or claims:

- Correctness of applicability recommendations on known positive and negative environment fixtures.
- Rate at which the selector returns a guess instead of `APPLICABILITY_UNKNOWN` when relevant evidence is missing.
- Successful cold-install and configuration flows on each explicitly supported route and host environment.
- Accuracy of reported context costs and distinction between enabled, invoked, exposed and measured states.
- Ability of an independent reader to trace a product claim to the exact intervention version, task/fixture, subject/runtime and evidence record.
- Correct handling of superseded controls and the stated retirement/re-check conditions.
- Operator effort required to decide what to install or remove, measured rather than presumed.

Do not optimize a single aggregate score if a subtype split changes the decision. Do not turn a high correct-recommendation rate on synthetic fixtures into a user-success claim.

## What remains open

- The public name, tagline and outward positioning.
- The actual audience beyond the current design hypothesis; no verified external adoption or user-research evidence is present here.
- Whether setup defaults to enabled-and-prune or disabled-and-enable, and which granularity each supported install route affords.
- Which additional control types should be stored and released from this repository versus linked integrations.
- Pi is the first selected owned runtime; Claude Code is a compatibility/distribution target. Exact supported runtime versions and test matrix remain to be established.
- The intended owner-controlled repository/path for the `skills-pi` distribution surface has not been verified; locate it before creating or modifying a package.
- Which runtimes beyond Pi and the currently supported Claude Code routes should be supported next.
- The cost and evidence standard for accepting non-skill interventions.
- Commercial model, willingness to pay, and whether any of these are product requirements at all.

Do not settle these questions by writing them into a release surface. Resolve factual parts from source or prototype; send genuine product-value forks through the existing independent review and owner decision process.

## Non-goals and constraints

- Do not inflate the catalog or add intervention types solely to make the product sound broader.
- Do not treat all agent failures as skill-shaped.
- Do not state public adoption, market demand, user identity, or efficacy without evidence.
- Do not change public landing-page copy, repository descriptions, marketplace metadata, or visual assets as part of this thesis.
- Do not copy unrelated private-project material into this public repository.
- Do not duplicate the sibling measurement instrument or use external panel opinions as measurement evidence.
- Do not spend on a sized experiment before its existing authorization and the accepted pre-spend qualification controls permit it.
- Do not treat an open PR, passing CI, or written procedure as proof that the next stage ran.

## Revisit conditions

Revisit this thesis if a source-level audit shows that its product loop is already provided by existing components with no material integration gap; if the small setup prototype cannot reliably classify applicability from inspectable state; if current platform constraints prevent the promised unit of configuration; or if measured operator behavior shows that the proposed journey does not improve decisions over the current manual workflow.
