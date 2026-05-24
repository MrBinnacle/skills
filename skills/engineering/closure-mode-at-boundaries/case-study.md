# Case Study — Closure→Build Transition Collapse

A worked example showing both the failure case and the correct execution of closure mode at a sprint boundary. Drawn from one project's incident in 2026; identifiers simplified for portability. The failure shape is what matters.

## Setup

A sprint had just LOCKED clean (all completion gates green). The project's "next step" queue listed four candidate forks:

1. **Fork A — security migration with schema constraints.** Mandatory attribution constraints at the database level. Estimated 3h substrate + 1h test inversion. ADR-class.
2. **Fork B — supply-chain audit step.** Native-binary integrity verification in CI. Unscoped CI work.
3. **Fork C — lint-strictness promotion.** Widen warnings-as-errors across all build targets. Under one hour estimated. ADR-class governance.
4. **Fork D — UI parity migration.** Migrate a sibling view to a recently-shipped cockpit pattern. Sprint-sized UI work.

The user invoked "the entire product team should be consulted." Five SMEs were dispatched in parallel: Architect, Security, Planner, Critic, Domain SME (a UI designer in this case).

## The swarm output (action list, not menu)

The substantive output was a list of actions to execute, not opinions to forward:

- **Critic**: the dependency named in Fork B is NOT in the project's dependency manifests — verifiable via grep in seconds.
- **Critic**: the symbol Fork A's migration touches appears in 11 files (Fork A actual cost is 6-8h, not 3h+1h) — verifiable via grep plus an audit in minutes.
- **Critic**: a named-but-missing feature lives in project memory as "next planned" — propose as Fork E.
- **Security**: Fork A schema constraints against existing rows require a pressure-test pre-flight on backfill policy (structurally different from prior add-column migrations).
- **Architect**: Fork A must sequence BEFORE Fork C to avoid governance friction on a security ship.
- **Domain SME**: Fork D affordance migrates as an additive panel, not a removal.

## Failure case (what actually happened)

The agent synthesized the SME output into an A/B/C menu and handed it back to the user. Specifically:

- The dependency-manifest grep was NEVER run.
- The 11-site symbol audit was NEVER run.
- The pre-flight on Fork A backfill was NEVER run.
- The missing-feature Fork E was NEVER sized.

The "revised frame" presented was the original frame with team commentary attached. This is escalated sequencing dressed up as choice — the exact pathology closure mode exists to prevent.

## Correct case (what the transition step requires)

A correct closure→build transition would have:

1. **Verification** — grep dependency manifests (seconds) → confirm phantom → DROP Fork B outright.
2. **Scope correction** — grep affected symbol across source (minutes) → confirm 11 sites → rescope Fork A to 6-8h.
3. **Pre-flight scheduling** — either run the backfill-policy pressure-test on Fork A OR mark Fork A as "pre-flight required, not shovel-ready."
4. **Frame addition** — surface a sizing question or run a quick scope pass to add Fork E as a sized candidate.
5. **Revised frame presented** — Fork A (rescoped, pre-flight required), Fork C (deferred to a governance cycle), Fork D (with additive-panel design), Fork E (sized). Three to four candidates, NONE phantom, EACH with verified scope.

The first three steps are minutes of mechanical work that eliminate weeks of misframed implementation.

## Lesson

The SME swarm worked. The transition failed. Closure mode lives in the transition — the discipline that the swarm's output is an action list to execute against the frame, NOT a multi-voice menu to forward.
