## Core Observation

Humans already perform closure reasoning naturally.

In enterprise environments, this responsibility is distributed across roles such as QA, UX, security, and operations.

Existing tooling partially approximates these behaviors, but no unified system consistently implements them as:

- explicit
- context-aware
- phase-triggered
- lightweight at runtime

---

## Engineering Skills

Workflow disciplines for shipping software. Each skill represents a focused decision or execution discipline that activates under specific conditions.

### Skills

- [**git-pull-rebase-trap**](git-pull-rebase-trap/SKILL.md)
  `git pull --no-ff` is silently ignored when `pull.rebase=true` — the rebase proceeds
  and rewrites every local SHA. Pre-flight config check, explicit fetch+merge
  alternative, and the SHA-backfill recovery protocol. Born from an observed
  22-commit rewrite incident ([EVIDENCE.md](git-pull-rebase-trap/EVIDENCE.md)).

- **closure-mode-at-boundaries**  
  Discipline applied at sprint or lifecycle boundaries. Triggers a structured closure phase that:
  - activates parallel SME-style review perspectives
  - surfaces high-impact omissions and risks
  - executes a consolidated remediation or adjustment list
  - produces a revised final frame before completion

