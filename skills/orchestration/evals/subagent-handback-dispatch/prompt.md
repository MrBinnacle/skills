---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
tags: [should-fire, subagent-handback]
plugins: [".."]
name: subagent-handback-dispatch
description: Dispatching a web research subagent for threat intelligence gathering
expected_outcome: The response names explicit return channels (SendMessage + file path), verifies the agent's tool grant matches the task, and includes a bounded write escalation for the file route.
---

I need to dispatch a research subagent to gather this week's threat intelligence. The agent I want to use is called `research-scout`. Its description says it performs web research with citations, and its frontmatter reads `tools: Read, Bash, Grep`. 

Write me the dispatch prompt to send it off for a one-week threat intelligence sweep across our cloud infrastructure dependencies. I need it to check for new CVEs in our dependency set and report back with source URLs and severity ratings.
