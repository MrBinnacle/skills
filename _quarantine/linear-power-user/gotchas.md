# gotchas — linear-power-user (append-only)

- [OBSERVED 2026-10-19] Initial reconnaissance showed long project descriptions can be truncated and batched tool calls can fail when query complexity exceeds a server limit. Partial payload is not the full specification. Retry focused reads and report coverage gaps.
- [RISK] A mutation response may not prove every requested relationship or preserved field. Read the changed object back.
- [RISK] Empty search results do not prove absence when pagination, permissions, indexing or query coverage is unknown.
- [RISK] addTeams and setTeams express different update intent. Inspect schema and current memberships before choosing.
- [RISK] A status can be valid for one team and invalid for another. Resolve it against the target team's workflow immediately before mutation.
- [RISK] Project, issue and initiative labels are distinct types.
- [RISK] Templates may create prefilled fields or sub-issues server-side. Inspect before use and verify afterward.
- [RISK] Missing acceptance evidence does not prove work is incomplete; Done does not prove the outcome was achieved.
- [OBSERVED 2026-10-23] An issue label description longer than 255 characters fails with `400 invalid_request: description must be shorter than or equal to 255 characters`. Count characters before saving one that carries instructions.
- [OBSERVED 2026-10-23] Do not send a comment that announces a status change in the same parallel batch as the change. In Claude Code auto mode, `save_comment` went through while `save_issue` (state Canceled) was denied twice as an external write, including once after the operator had granted permission. The comment then said "Closed" on an open issue. Make the mutation first, read it back, then write the comment.
