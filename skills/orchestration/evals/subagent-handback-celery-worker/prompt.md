---
name: subagent-handback-celery-worker
description: A background worker that runs through the payments package unattended, where the worker is a Celery task and not an agent. Negative control partner for subagent-handback-dispatch.
expected_outcome: The agent does not invoke mrbinnacle-orchestration:subagent-handback. Nothing is dispatched to a model and nothing reports back to one, so the card's pre-dispatch and post-return steps have nothing to act on. The deliverable is Celery task code.
tags: [control, should-not-fire, mrbinnacle-orchestration]
plugins: ["../.."]
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

I am about to deploy a background worker that runs through the `payments/`
queue every night and retries every charge that failed with a transient error.
It runs while I do something else and I will not be watching it.

It is a Celery task on our existing Redis broker. Write me the task definition.
