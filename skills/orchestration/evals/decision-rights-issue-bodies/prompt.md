---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
tags: [should-fire, decision-rights]
plugins: ["../.."]
name: decision-rights-issue-bodies
description: Writing an issue body for a downstream team with mixed evidence-sensitive and non-negotiable decisions
expected_outcome: The response includes a framing block acknowledging evidence asymmetry, classifies decisions as revisable or non-negotiable, and attaches specific Revisit if clauses only where evidence can change the outcome.
---

I am drafting an issue body for the platform team to implement a new API gateway. The issue mixes decisions I made based on prior research with constraints the security team set. Please write the issue body with these decisions:

1. We chose Envoy Proxy over NGINX based on a performance benchmark from last quarter. The benchmark tested throughput under load but did not test WebSocket upgrade latency, which matters for our real-time features.
2. Rate limiting should use a token-bucket algorithm with a 1000 req/min default per API key. This was agreed with the product team.
3. All API keys must be stored in Vault, not in environment variables. This is a hard security constraint from the security team.
4. The migration should use a blue-green deployment pattern to avoid downtime. I chose this based on research into zero-downtime patterns.
5. Logging should output structured JSON to stdout. This matches our existing observability stack.

Write the issue so the platform team knows which decisions they can challenge if their implementation context differs from mine.
