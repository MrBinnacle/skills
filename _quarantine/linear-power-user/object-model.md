# Linear object model and tool contract

Official references: [MCP](https://linear.app/docs/mcp), [Projects](https://linear.app/docs/projects), [Initiatives](https://linear.app/docs/initiatives), [Cycles](https://linear.app/docs/use-cycles), [Issue relations](https://linear.app/docs/issue-relations), [Project milestones](https://linear.app/docs/project-milestones), [Issue templates](https://linear.app/docs/issue-templates), [Project templates](https://linear.app/docs/project-templates). Workspace data establishes current configuration; docs establish product semantics.

| Object | Use | Avoid | Relationships / constraints |
|---|---|---|---|
| Workspace | Organization boundary and shared configuration | A workstream | Contains teams, users, labels, initiatives, projects, documents, issues visible to the account |
| Team | Ownership boundary and team-specific workflow | Generic label or phase | Has key, members, statuses, cycles, and possibly team-scoped labels; projects can span teams |
| Initiative | Strategic outcome spanning projects | Project-sized task or catch-all folder | Groups projects and may have parent initiatives |
| Project | Coordinated work with outcome, lead, status, timeframe | Single task or permanent category | Belongs to one or more teams; may link initiatives, issues, milestones, docs, members and updates |
| Milestone | Meaningful checkpoint within a project | Arbitrary phase taxonomy | Belongs to a project; target date and issue associations depend on available operations |
| Issue | Actionable work, defect, decision, question or deliverable | Vague observation without next action | Belongs to a team; may have status, priority, assignee, labels, cycle, project, parent/child and relations |
| Sub-issue | Decomposition of a parent issue's result | Merely related peer issue | Parent-child relation; useful when child completion explains parent completion |
| Issue relation | Typed relationship such as blocks, blocked by, duplicates, relates to | Invented dependency | Direction matters; mutate only when evidence supports it and tools allow it |
| Cycle | Team-specific timebox | Milestone or due date | Assign only when genuinely committed to the interval |
| Status | Current workflow state | Proof of outcome quality | Team-configured; resolve against target team's workflow |
| Priority | Relative urgency/importance | Substitute for scope | Use available scale and evidence; omit if unknown |
| Assignee / lead | Execution owner / project leadership | Guessed default | Resolve real workspace user; assign only when grounded |
| Label | Reusable classification/filter | Status or dependency | Issue, project and initiative labels are distinct classes and may differ in scope |
| Project summary | Short statement of intent | Full specification or progress report | Keep concise and consistent with scope |
| Project description | Durable scope and working context | Duplicate of every issue and update | Understand patch versus replacement semantics before updating |
| Document | Specification, decision record, research or knowledge | Dated status update | Inspected create tool requires exactly one parent: project, issue, initiative, cycle or team |
| Status update | Dated progress, risks and next steps | Permanent project definition | Ground it in evidence available at update time |
| Template | Reusable prefilled issue/project/document structure | Agent policy or proof of correctness | Inspect type, fields, content, IDs and sub-issues before applying |
| Agent skill | Agent behavior instructions | Linear object | Repo skills differ from Linear Agent skills; do not assume they are interchangeable |

## Tool surface inspected

Observed families include workspace/team and user lookup; project, initiative, milestone and issue list/get/save; team status and label lookup; cycles; documents; templates; search/fetch; status updates; comments; and Linear Agent skill list/get. Tool names are discovery hints, not permission to assume parameters.

Schema facts observed: project creation requires name and at least one team via addTeams or setTeams; templates apply on project create; partial description patches may be supported. Issue creation requires team and title unless a template is supplied; the assignee field is named assignee, not assigneeId. Milestone creation requires project and name. Document creation requires exactly one parent. Inspect the full live schema before each operation and resolve references before mutation.

## Common modeling errors

- Initiative for a small project: hierarchy without portfolio value.
- Project for one issue: overhead without coordinated outcome tracking.
- Milestones for every phase: noisy checkpoints obscure meaningful gates.
- One issue per sentence: backlog noise instead of actionable work.
- Parent issue used as project: loses project-level health and timeline reporting where those matter.
- Duplicating content in project description, document and status update: competing sources of truth.
- Speculative cycle or dependency: apparent commitment or false critical path.
- Missing acceptance criteria: subjective completion.
