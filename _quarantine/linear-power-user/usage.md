# Usage guide

Use this candidate with an agent that has Linear MCP tools available. It is an operating procedure, not a replacement for tools or permissions.

## Example prompts

- “Inspect Linear and propose a project structure for the payments product. Do not mutate anything until you show me workstreams, milestones, dependencies and unresolved decisions.”
- “Create a small project for this isolated deliverable. Skip an initiative or milestones unless they add real value.”
- “Audit the existing project before restructuring it. Preserve useful issues and relationships; show the before/after plan first.”
- “Turn this feature request into one actionable issue with acceptance criteria. Search for duplicates first.”
- “Report project health from issue evidence, milestones and status updates. Separate outcomes, claims, blockers, risks and unknowns.”
- “Check whether a label or workflow change is justified by actual usage. Do not modify configuration.”

## Validation

evals/evals.json defines 12 structural cases and their expected sequences, mutation boundaries, postconditions and failure conditions. This is a specification, not a model benchmark. Use a mocked adapter or isolated test workspace, never disposable production objects. Before promotion, follow ADMISSION.md and AGENTS.md, measure skill cost, run controlled with/without-skill evaluations, and record independent failure occasions.
