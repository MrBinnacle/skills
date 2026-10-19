# gotchas — linear-power-user (append-only)

- [OBSERVED 2026-10-19] Initial reconnaissance showed long project descriptions can be truncated and batched tool calls can fail when query complexity exceeds a server limit. Partial payload is not the full specification. Retry focused reads and report coverage gaps.
- [RISK] A mutation response may not prove every requested relationship or preserved field. Read the changed object back.
- [RISK] Empty search results do not prove absence when pagination, permissions, indexing or query coverage is unknown.
- [RISK] addTeams and setTeams express different update intent. Inspect schema and current memberships before choosing.
- [RISK] A status can be valid for one team and invalid for another. Resolve it against the target team's workflow immediately before mutation.
- [RISK] Project, issue and initiative labels are distinct types.
- [RISK] Templates may create prefilled fields or sub-issues server-side. Inspect before use and verify afterward.
- [RISK] Missing acceptance evidence does not prove work is incomplete; Done does not prove the outcome was achieved.
