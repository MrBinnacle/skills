---
name: linear-power-user
description: Product planning and safe workspace operations in Linear. Use when creating projects, structuring issues, inspecting conventions, or reporting project health.
---

# Linear power user

Inspect before mutating. Read the current workspace and relevant objects, model the outcome and smallest useful structure, plan consequential changes, execute with validated references, read changes back, and report verified results and partial failures.

Use [object-model.md](object-model.md) for object semantics and tool limitations, [project-method.md](project-method.md) for project and issue design, and [gotchas.md](gotchas.md) when a write fails or evidence is incomplete.

Do not invent IDs, statuses, labels, assignees, dates, or dependencies. Reuse existing objects and conventions. Preserve unrelated fields. Do not delete, archive, bulk-reassign, or change broad configuration without explicit authorization. Missing evidence is not proof of absence, non-use, or completion. Stop dependent writes when a prerequisite fails. Do not claim success until the tool confirms it and a read-back verifies important fields and relationships.

For broad work, use DISCOVER → MODEL → PLAN → EXECUTE → VERIFY → REPORT. For small edits, keep this proportionate. Ask one targeted question when consequential ambiguity cannot be resolved from the workspace; otherwise execute.

Workspace reconnaissance on 2026-10-19 observed a workspace named mrbinnacle and one team Mrbinnacle (MRB), plus initiatives and projects for skills, skill-harness, and company internals. The visible project-template query returned none. These are snapshots; always re-read live state. The candidate is quarantined because no empirical unaided-failure and recurrence evidence supports admission.
