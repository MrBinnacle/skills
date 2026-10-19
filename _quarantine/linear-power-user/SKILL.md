---
name: linear-power-user
description: Use when planning, creating, restructuring, or auditing Linear projects, initiatives, milestones, issues, workflows, and workspace conventions.
disable-model-invocation: true
---

# Linear Power User

Turn a natural-language product request into a coherent Linear model, execute supported changes safely, and verify the persisted result. Return the decision, changed objects, verification evidence, and unresolved gaps. Do not confuse API success with a well-modeled product plan.

## Operating contract

Follow **DISCOVER → MODEL → PLAN → EXECUTE → VERIFY → REPORT**. Scale the ceremony to the change. A simple field edit needs a short read/check/write/read-back. A multi-workstream project needs a concise proposed structure before mutation when material choices remain.

1. **Discover.** Search for duplicates and inspect the target object, related issues, project/initiative links, milestones, status history where available, team workflow, labels, cycles, templates, documents, and relevant workspace patterns. Use actual IDs/names returned by tools. Check pagination.
2. **Model.** State the outcome, user/customer or operational problem, scope, exclusions, dependencies, measurable acceptance criteria, and evidence needed to claim completion. Separate committed work from options.
3. **Plan.** Choose the smallest structure that supports execution and accountability. Reuse existing objects and conventions. Identify each intended mutation and its blast radius. Ask one targeted question or present the plan for approval only when a consequential ambiguity cannot be safely resolved from evidence.
4. **Execute.** Validate every reference immediately before use. Apply changes in dependency order. Stop if a prerequisite fails; do not continue as though it succeeded.
5. **Verify.** Read changed objects back. Confirm IDs, team, project/initiative membership, description, status, milestone assignments, labels, priority, dates, and relations that matter to the request. Verify relationships from both sides when the tools expose both.
6. **Report.** Separate confirmed changes, failed/partial changes, assumptions, and remaining unknowns. Never claim success from a tool call that failed or from an object merely appearing in a draft.

## Object-selection rules

- **Workspace** contains teams and shared objects. **Team** owns issues and a team-specific workflow and planning configuration. Do not invent teams or assume every team shares statuses, labels, or cycles.
- **Initiative** expresses a strategic outcome across one or more projects. Use only when the work contributes to a larger strategic effort; do not create one for every project.
- **Project** groups coordinated work around a shared deliverable/outcome. Use when multiple related issues need shared context, coordination, progress visibility, or stakeholder reporting. Do not create a project for a single small issue.
- **Milestone** marks a meaningful checkpoint inside one project. Assign relevant project issues to it. Do not create milestones as decorative phases or duplicate issue statuses.
- **Issue** is an actionable unit of work and belongs to one team. Use sub-issues for genuine parent/child decomposition, not merely because tasks are related. Use issue relations for blocking, blocked-by, related, or duplicate semantics; do not encode dependency only in prose when a supported relation can represent it.
- **Cycle** is a team planning period, not a project phase or deadline. Set it only when there is a real near-term commitment and the appropriate cycle exists.
- **Status** is a team workflow state. **Priority** expresses relative urgency/importance. **Assignee/lead/owner** are distinct fields on their respective objects. Never substitute one for another.
- **Project overview/description** gives durable project context. A **document** is a separate knowledge artifact that may be linked to a project or initiative. A specification belongs in the description or a document according to length, collaboration needs, and existing practice; do not assume a project document is the project description.
- **Template** is a reusable starting configuration/content; applying it can prefill fields and create sub-issues. An **agent skill** is reusable operating instruction. Neither is a substitute for a well-modeled live project.

See `object-model.md` and `project-method.md` when detailed decisions are needed.

## Project setup

Before creating anything, search project names, issues, initiatives, documents, and team configuration. Compare the closest existing structures and determine whether the request is new work, continuation, release tracking, or a restructure.

A sound project brief usually includes:
- **Outcome:** what changes for whom and why.
- **Problem / context:** evidence, current state, and why now.
- **In scope / out of scope:** explicit boundaries.
- **Success and acceptance criteria:** observable conditions, not activities.
- **Workstreams / dependencies:** only independently actionable units that need tracking.
- **Risks / decisions:** unknowns with an owner or decision point where known.
- **Completion evidence:** what must be observed before calling the work done.

Create only fields supported by evidence and useful to the plan. Dates, priority, owners, labels, cycles, and initiative membership are not decoration. If a field is unknown, leave it unset and report the gap rather than inventing a value. Use milestones only when they communicate meaningful checkpoints. Issues should be small enough to own, sequence, and verify; acceptance criteria should describe outcomes.

For an existing project, fetch the full project and inspect its issues, milestones, documents, initiative, and current fields before editing. Prefer narrow patches or omitted fields over resending whole descriptions or replacement arrays. Preserve unrelated fields and relations. Do not duplicate existing issues because their titles differ slightly; compare intent, description, identifiers, and links.

## Tool discipline

Use the connected Linear tools' current schemas as the contract. In this environment:
- `search` finds issues, projects, initiatives, and documents; `fetch` or entity-specific getters retrieve details.
- `list_teams`, `get_team`, `list_issue_statuses`, `list_issue_labels`, `list_project_labels`, `list_initiative_labels`, `list_cycles`, `list_templates` / `get_template`, and the corresponding list/get tools are discovery surfaces.
- `save_project`, `save_initiative`, `save_milestone`, `save_issue`, `save_document`, and `save_status_update` are writes. Their semantics differ. Inspect the schema before use; do not infer omitted fields, replacement behavior, or relation support.
- For `save_issue`, `labels` replaces the full label set; `addLabels` and `removeLabels` are incremental. For `save_project`, `labels` replaces the set; `addTeams` / `removeTeams` are incremental and `setTeams` replaces team membership; initiative fields have separate add/remove/set forms. Do not combine mutually exclusive forms.
- On create, `save_project` needs a name and at least one team; `save_issue` needs a team and title unless a template supplies it. Applying a template is create-only. A supplied issue description replaces template body; an empty description keeps it. Verify template-created sub-issues and fields after creation.
- Resolve milestones within the target project. Statuses must belong to the intended team. Validate names against returned lists; never fabricate IDs.
- If a needed operation (such as a specific relation mutation) is absent from the exposed tools, say so and do not claim it was performed. Use documentation search for product semantics, not as proof that this connector exposes the corresponding mutation.

Do not delete, archive, bulk-reassign, or make broad workspace configuration changes without explicit authorization. Do not create labels, statuses, cycles, templates, or custom conventions unless inspection shows a concrete gap and the change is authorized.

## Evidence and health

A status label is not proof of progress. Inspect issue-level work, completion evidence, blockers, stale ownership, milestone state, and recent updates. Distinguish:
- **Verified:** supported by a tool result or cited authoritative source.
- **Inference:** best explanation of observed evidence, explicitly labeled.
- **Unknown:** unavailable or not established by this connector.
- **Recommendation:** proposed action, not an existing workspace fact.

Do not infer that something is unused, absent, or complete from missing search results alone. Check pagination, archived filters, tool scope, and known limitations. A mutation response confirms that a write was accepted, not that every intended relationship is correct; read it back.

## Evaluation and limitations

Use `evals/evals.json` as the behavioral contract. Tests are scenarios and expected assertions, not a measured model score. The candidate remains unmeasured until run against an unaided baseline and with-skill arm in a suitable harness. See `USAGE.md` for invocation and safe evaluation guidance.
