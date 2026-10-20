# Project method

Choose the smallest useful structure. Before creating an initiative, milestone, label, template, cycle or project, name the capability that deleting it would destroy. If the answer is a future benefit ("could", "might", "for later"), put the content in an existing issue or an existing project's description instead. [object-model.md](object-model.md) states what each object is for. When you create or change work, treat facts the request asserts about the workspace ("X already has a milestone", "Y is a duplicate") as premises, and read each one before planning against it.

## Diagnose before choosing an intervention

Treat "What should I do with this project?" as a diagnosis request, not permission to reorganize it. Resolve the target project, then inspect proportionate evidence: project description and current status/update; target and start dates; milestones; linked issues and their states; available blockers/dependencies; recent activity; initiative context when portfolio alignment matters. Check pagination, truncation, access errors and tool limits before making claims about coverage.

Classify the user's intent as one or more of: understand/diagnose, plan, execute, monitor, report, troubleshoot, or coordinate. User intent determines the requested outcome; project evidence determines what is worth addressing. A detected risk does not itself authorize a mutation. Do not change health, status, dates, scope, ownership or assignments only because evidence indicates risk.

Evaluate these dimensions independently; do not collapse them into an invented numeric health score:
- **Outcome clarity:** intended result and observable acceptance are explicit.
- **Execution readiness:** actionable scope, ownership, next steps and genuine dependencies are clear.
- **Schedule credibility:** dates and forecasts are supported by current scope and progress evidence.
- **Delivery condition:** work is progressing, stalled, blocked, overdue, or otherwise at risk.
- **Observability:** the intended audience can detect meaningful change and knows what action follows.

For each relevant dimension, record one state: **adequate**, **deficient**, **unknown**, **conflicting**, or **not applicable**. Unknown is not deficient. Conflicting means sources disagree and must be reconciled. State the evidence and coverage behind a diagnosis. A project or issue status is a signal, not proof of delivery; an issue marked Done does not alone prove the intended outcome was achieved.

## Select the smallest useful intervention

Use the diagnosed problem and requested outcome to choose the intervention. Do not select a Linear feature first and retrofit a justification.

- **Explain** when existing evidence answers the question.
- **Investigate** when a relevant fact is missing or sources conflict; make focused reads and report remaining gaps.
- **Recommend** when evidence supports a change but execution is not requested or authorized.
- **Prepare** a before/after plan or draft first when the change is broad or consequential, or publishing intent is ambiguous.
- **Execute and verify** only when the action is authorized, references are validated, and the available tools support it. Verify with the fresh read-back in [Change existing work](#change-existing-work).

Choose a view or reporting mechanism by the question it answers:

| Question | Mechanism | Limit |
|---|---|---|
| Compare or filter a portfolio of projects by status, lead, target date or health | Project list / custom project view | |
| A stable recurring query, such as a work queue or at-risk projects | Custom (saved) view: a filtered issue, project or initiative view that is saved, shared at workspace or team scope, and favorited. An issue view can also carry personal or Slack subscriptions for issues added to it or completed in it. Initiative views need the Enterprise plan. See [Linear custom views](https://linear.app/docs/custom-views). | Saving the filter of any list or board creates one, so creating, sharing or subscribing is a persistent change that needs authorization. Check existing views first; do not duplicate one. |
| Project scheduling, milestones, date overlap and dependencies | Project timeline | Do not confuse it with an issue execution board. |
| Manage actionable work by status, owner, priority or other issue fields | Issue list / board | |
| Meaningful project checkpoints | Milestones | Not every phase or arbitrary progress marker. |
| Point-in-time narrative progress, risks, decisions and next actions | Project status updates | |
| Issue-level trends or distributions | Insights | Only when the underlying data answers a defined question. |
| Recurring metrics, charts and tables for an audience that needs a consolidated reporting surface | Dashboard | Do not default to a dashboard for a one-off question. |
| Group genuinely related projects around a strategic outcome | Initiative | Not a generic folder. |
| Retain durable specifications, decisions or research | Document | Do not duplicate a status update. |

For ongoing monitoring, first identify the audience, decision to support, signals, cadence/trigger, and action threshold. Inspect existing views and reports before recommending another. Do not promise alerts, automation, or refresh behavior unless a verified available tool or integration supports it. Recommend the least-complex mechanism that closes the actual observability gap.

For a project described as at risk, overdue, or blocked, validate the signal and inspect its likely causes before recommending a correction. Distinguish a confirmed dependency from an overdue issue or suspected risk. If the project is adequate and no material deficiency is established, recommend preserving its current setup.

## Create work

Search for existing work before creating anything. Inspect the target team, statuses, labels, templates, cycles, milestones, issues and relationships. Define outcome, problem evidence, scope, exclusions, observable acceptance criteria, dependencies and ownership. Keep unknown product intent explicit.

For a project, create issues only for actionable deliverables. Add milestones only for meaningful gates and dependencies only when one task must finish before another can proceed. Set dates, owners, priority, labels and cycles only when supported by the request or workspace evidence.

For issue descriptions, capture problem/evidence, intended outcome, scope/exclusions, observable acceptance criteria, true blockers and unresolved questions. Do not convert every observation into a ticket.

## Change existing work

When changing an existing project, read it and its related work first. Where the plan holds a genuine choice, such as which structure, which owner or whether to merge duplicates, name the options and their trade-off rather than asking the reader to confirm a finished answer. For each planned write, name the read-back that would show the write did nothing: the field still holds its old value, the relation is absent, the status update does not appear on the project. Run that read-back after the write, as a fresh query against the workspace, not from the write call's own response. A write tool's success message is the write reporting on itself.

## Report

Report progress evidenced, work in flight, blockers, risks, decisions needed and next actions. List a decision as needed only when the request, the workspace and recorded rulings leave it open. Test each one: could a competent practitioner with less context settle it? If yes, state it as your call, and say what would change it. Give every count or health figure its coverage: the objects read, and the objects whose read failed, was truncated or stopped before the last page. A failed read is a counted gap, never an empty value. Mark each unknown either as not yet checked, naming the read that would settle it, or as not checkable with the available tools. In every diagnosis or report, separate verified facts, inferences, recommendations and unsupported claims.
