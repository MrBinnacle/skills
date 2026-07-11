# Orchestration Skills

Disciplines for multi-agent work: dispatching parallel subagents, keeping isolated
outputs joinable, and synthesizing them into one decision without groupthink or
false agreement. Ordered by how soon the failure is likely to bite you.

### Skills

- [**downstream-instruction-framing**](downstream-instruction-framing/SKILL.md) — when one
  session writes instructions for a downstream reader (handoff, plan, subagent prompt), command
  framing strips the judgment of the better-informed executor. Frame prior decisions as
  informed proposals from a less-informed reviewer, with a per-decision "Revisit if:" clause
  ([the receipt](downstream-instruction-framing/EVIDENCE.md)).

- [**subagent-research-reliability**](subagent-research-reliability/SKILL.md) — web-research
  subagents fail silently two ways: the agent's tool grant can't actually search (it no-ops or
  fabricates), or the search returns hallucinated citations. Pre-dispatch tool-grant check +
  post-return citation-verification pass; both failure modes observed and caught in one session
  ([the receipt](subagent-research-reliability/EVIDENCE.md)).

- [**parallel-review-disposition-schema**](parallel-review-disposition-schema/SKILL.md) —
  dispatch discipline for 3+ parallel agents adjudicating a shared finding-set: a fixed
  decision-vocabulary enum, a shared per-item output block, explicit item ownership, and
  a mandatory status line, so isolated outputs JOIN at synthesis instead of returning
  N strong reviews that don't compose. Includes the adversarial-verify seat template.
