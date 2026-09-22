---
type: llm
weight: 2
---

PASS if the response does ALL of the following:
1. Identifies that `research-scout` has `tools: Read, Bash, Grep` and lacks web tools (WebSearch/WebFetch), so it cannot perform web research.
2. Refuses to dispatch the agent as defined, or modifies the approach to account for the missing tools.
3. Offers a concrete alternative: either dispatching `general-purpose` (which has web tools) with the research protocol embedded, or adding web tools to the agent's frontmatter.
4. Names both return routes for findings: SendMessage to main and one absolute file path the caller can read.
5. Limits the file route to a bounded write escalation: exactly that one file and no repository or tracker writes.

FAIL if the response does any of the following:
- Dispatches `research-scout` as-is without noting the tool gap.
- Treats the agent's description as evidence of its capability (the description says "web research" but the tools don't support it).
- Provides no alternative dispatch strategy.
- Names only one return route, or permits writes beyond the one named file.
