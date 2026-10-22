---
name: subagent-handback-self-dispatch
description: About to dispatch a subagent, where the agent under test dispatches it. Variant of subagent-handback-dispatch for issue 609.
expected_outcome: The agent invokes mrbinnacle-orchestration:subagent-handback before it calls Agent. The card's description opens "Use before dispatching a subagent for research", and here the agent under test is the one about to dispatch a read-only research sweep. The task is the one in subagent-handback-dispatch; only the dispatcher differs.
tags: [variant, should-fire, mrbinnacle-orchestration]
plugins: ["../.."]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Agent]
---

Send a background agent through the `payments/` package to find every place we
catch an exception and then carry on without logging it. It runs while I do
something else and I will not be watching it.

Dispatch it now.
