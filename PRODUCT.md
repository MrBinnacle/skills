# Product

**Maintained product intent — updated 2026-10-17.** This file records the owner's
current direction for Skills. The owner decides purpose, audience and priorities;
this document does not ask evidence or another charter to approve those decisions.
Evidence determines what we can claim about delivery and results.

This revision replaces the earlier artifact-derived account, which left the audience
undecided and defined the product by Claude Code skill cards. The owner has since
settled those questions. The direction is tracked in
[#418](https://github.com/MrBinnacle/skills/issues/418); implementation and public
surfaces can lag it. That lag does not reopen the decision.

## Product Purpose

Skills is one product: a knowledge base and practical support for real engineering
work with frontier AI models. It serves the owner's work first and is also intended
for other developers. Pi is the primary runtime direction. Claude Code remains a
compatibility and distribution target, not the definition of the product.

The repository **is itself a knowledge base**. Evidence, explanations, mechanisms,
counterexamples, gotchas and rationale can be useful without becoming a skill card,
executable control or shipped feature. A reader finding an explanation that changes
an engineering decision is a useful outcome to pursue, just as delivering an
appropriate control is. Neither outcome is established merely by publishing a file.

Skill cards remain a deliverable. Depending on the problem, the useful response may
instead be knowledge, a project rule, a deterministic check, a hook, a setup change,
or no added control. Do not turn this range into a requirement to build every form.

## Users

**Intended users:** the owner first, plus other developers doing real engineering
with frontier models. This is an owner decision, not an adoption estimate or a
hypothesis awaiting permission to name an audience.

**Observed use and benefit:** these require their own records. The intended audience
does not establish external adoption, market demand, comparative quality or improved
outcomes. Do not infer those from publication, an install, an invocation, or the
owner's decision to build the product.

Work should start from a concrete engineering task, problem or knowledge need.
Post-incident diagnosis, preparation for a task, and setup or a change of environment
are possible entry points. They are design choices, not a measured user journey.

## Operating Context

**Pi-first does not mean two products.** Runtime-specific delivery should serve one
Skills product with shared canonical knowledge and evidence. A worktree, package or
adapter is not a second authority for what a capability means. Runtime differences
must be stated rather than hidden behind a shared name.

For the setup work in [#407](https://github.com/MrBinnacle/skills/issues/407), the
owner has selected **ship-on, setup-prunes**: plugins stay enabled by default;
setup recommends disabling whole plugins where appropriate. The
[2026-10-15 ruling](https://github.com/MrBinnacle/skills/issues/407#issuecomment-6194414052)
leaves plugin regrouping open. The default policy is settled; applying it to each
runtime still needs implementation evidence. It does not establish per-card switching on every current
install route.

For what exists, open the [runtime delivery matrix](docs/product/runtime-delivery-matrix.md).
Its 2026-10-17 inventory identifies the inspected revisions, installed runtime
versions, content hashes, loader observations and missing receipts. It records
Claude Code plugin delivery and a configured Pi worktree, not a verified clean Pi
package install. It also records differing bytes on some shared card paths. Shared
canonical content is the direction; current byte parity is not established.

Do not copy that inventory into a second maintained table here. A new delivery claim
needs a dated observation at the relevant version. A loader result establishes what
was found or loaded, not that the resulting engineering work improved.

## Working Principles

- **Mission Command:** state the intended outcome, constraints and decision rights.
  Let the implementer choose methods and sequencing within them. Escalate material
  conflicts, not settled owner decisions for another round of approval.
- **TDD for code changes:** observe the relevant failure, make the smallest change
  that passes, then refactor while retaining the check. A phrase-presence assertion
  is not evidence that a product account is coherent or that a capability works.
- **Use the right form for the problem.** Prefer an existing explanation or mechanism
  when it is enough. Do not add a framework, schema or skill identity just to house
  useful knowledge.
- **Keep the admission boundary specific.** [ADMISSION.md](ADMISSION.md) governs
  admission of skill cards. It is not a test every explanation or research note must
  pass to belong in the knowledge base. Retiring a card does not by itself show that
  its underlying knowledge is obsolete.
- **Publication is not validation.** A maintained or installed artifact is not thereby
  effective. Invocation, exposure, activation, outcome and measured benefit are
  different observations. Keep the limits beside each claim.
- **Remove concrete defects, not words by taste.** For code, identify the failed
  behavior and exercise it. For agent-facing language, use the relevant research and
  a concrete ambiguity or counterexample. Generic word bans and smoother prose are
  not substitutes for clearer instructions.

## Sources and Authority

One maintained intent record does not mean one file contains all knowledge.

| Question | Source to use |
| --- | --- |
| What is this product for, who is it for, and what has the owner prioritized? | This file, recording owner decisions |
| What knowledge, mechanism or limitation supports a particular engineering decision? | The relevant explanation, research, counterexample or dated record; retain its scope and uncertainty. What three recorded decisions share is described in [Three decisions, and what they share](docs/explanations/three-decisions.md) |
| What does a published card claim and what evidence supports it? | Its `SKILL.md`, `EVIDENCE.md` and append-only `gotchas.md` |
| What is packaged and what delivery has been observed? | Runtime manifests and the versioned sources and observations linked by the [delivery matrix](docs/product/runtime-delivery-matrix.md) |
| What measured result may be claimed? | The cited receipt and its applicability limits, not product intent or installation success |
| How is work in this repository governed? | [AGENTS.md](AGENTS.md), [ADMISSION.md](ADMISSION.md) for cards, and the applicable [ADRs](docs/adr/) |
| Which terms, public voice and visual rules apply? | [GLOSSARY.md](GLOSSARY.md), [BRAND.md](BRAND.md), [VERBATIM.md](VERBATIM.md) and [DESIGN.md](DESIGN.md) |

External research and planning records may inform this account without becoming a
second normative product source. Keep first-hand evidence and useful reasoning
where they can be read and checked. This file links to them rather than restating
their details as new facts.

The earlier [product thesis](docs/product/agent-reliability-system-thesis.md) and
[product contract](docs/product/product-contract.md) remain historical proposals.
They contain useful questions and rationale, but their architecture, schemas,
sequencing and narrower intervention emphasis are not adopted by this revision.
Use this file for current intent and the delivery matrix for the dated inventory.

## Brand and Public Surfaces

Derive future README and related-surface drafts from this intent and the relevant
knowledge and evidence. A public surface must not imply that every intended
capability already exists. Older card-only or Claude-only descriptions need
reconciliation; they do not override the owner's current direction.

This revision does not approve a broad public-copy rewrite. Follow [BRAND.md](BRAND.md)
for public voice and authorship, and [DESIGN.md](DESIGN.md) for presentation. Preserve
the distinction between inventory and measurement: being kept is not being measured.
Keep provenance and uncertainty visible instead of polishing them away. The existing
accessibility and asset checks remain in force; this record introduces no new
accessibility standard.

## Evidence and Limits

Card evidence, retirement records, delivery observations and measurement receipts
answer different questions. Preserve those distinctions when summarizing them.
A missing result is an honest gap, not permission to invent a number or to assert
that a search proved no evidence exists.

This revision claims no new adoption or efficacy result. It does not establish
runtime parity, a clean Pi package install, or a completed setup experience. It also
does not require every useful piece of knowledge to carry a measured intervention
effect. A claim about an intervention's effect still needs evidence of that effect.

## Next Work

Apply this direction to a concrete own-use engineering workflow and state the
observable outcome before implementation. Continue the setup work under #407's
existing ruling. Name the Claude compatibility scope being delivered rather than
promising parity by implication.

Reconcile the three bucket READMEs through
[#390](https://github.com/MrBinnacle/skills/issues/390), retaining the existing card
repair dependencies. The broader public-surface work is separate from that ticket.
Use the research tracked by
[#421](https://github.com/MrBinnacle/skills/issues/421) where it informs the knowledge
base; do not create another product authority to hold it. These are implementation
and communication tasks, not unanswered questions about audience, product identity
or runtime priority.
