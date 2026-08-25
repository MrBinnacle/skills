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

- [**subagent-research-reliability**](subagent-research-reliability/SKILL.md) — subagent
  research fails three ways silently: a dead letter (plain text never reaches the main session),
  a tool grant that can't actually search, and post-return claims that don't hold. Pre-dispatch:
  name the return channel and verify tool grants. Post-return: verify every claim, negatives first
  ([the receipt](subagent-research-reliability/EVIDENCE.md)).

- [**parallel-review-disposition-schema**](parallel-review-disposition-schema/SKILL.md) —
  dispatch discipline for 3+ parallel agents adjudicating a shared finding-set: a fixed
  decision-vocabulary enum, a shared per-item output block, explicit item ownership, and
  a mandatory status line, so isolated outputs JOIN at synthesis instead of returning
  N strong reviews that don't compose. Includes the adversarial-verify seat template.
