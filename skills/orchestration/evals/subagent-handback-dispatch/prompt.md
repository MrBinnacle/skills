---
name: subagent-handback-dispatch
description: About to dispatch a subagent. Seed case 4 of five from 2026-09-12.
expected_outcome: The agent invokes mrbinnacle-orchestration:subagent-handback. Description coverage is strong; the card's first words are "Pre-dispatch, name the return channel", and this prompt is a pre-dispatch moment.
tags: [seed, should-fire, mrbinnacle-orchestration]
plugins: ["../.."]
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

I am about to send a background agent through the `payments/` package to find
every place we catch an exception and then carry on without logging it. It runs
while I do something else and I will not be watching it.

Write me the prompt I should send it.
