---
name: subagent-handback-brief
description: About to dispatch a subagent, asked for its brief rather than its prompt. Paraphrase variant of subagent-handback-dispatch (#609).
expected_outcome: The agent invokes mrbinnacle-orchestration:subagent-handback. The card's description opens "Use when prompting, briefing or dispatching a research subagent", and the user asks for the brief of a read-only research sweep that the user will dispatch, without the word prompt. ../MANIFEST.md records why this case exists.
tags: [variant, should-fire, mrbinnacle-orchestration]
plugins: ["../.."]
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

I am about to send a background agent through the `payments/` package to find
every place we catch an exception and then carry on without logging it. It runs
while I do something else and I will not be watching it.

Write me a brief for it.
