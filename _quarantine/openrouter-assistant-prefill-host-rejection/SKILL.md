---
name: openrouter-assistant-prefill-host-rejection
description: |
  Diagnose and fix "This model does not support assistant message prefill. The
  conversation must end with a user message." errors when running Anthropic models
  through OpenRouter (opencode, agent harnesses, any client that sometimes ends a
  request on an assistant turn). Use when: (1) that exact error kills a run, branded
  [Azure], [Amazon Bedrock], [Google], or [Anthropic]; (2) the failure is intermittent
  across otherwise-identical runs; (3) a provider routing pin "fixed" it and it came
  back. Covers why pins cannot fix it, why intermittent green runs prove nothing, the
  behavioral probe that actually tests a candidate model, and the model-family change
  that resolves it.
author: Claude Code
version: 1.0.0
date: 2026-08-17
---

# OpenRouter Assistant-Prefill Host Rejection

## Problem

A client (observed: opencode driving an agent loop) sometimes sends a request whose
`messages` array ends on an `assistant` turn — assistant prefill. OpenRouter hosts
serving Anthropic models reject that shape with:

```
This model does not support assistant message prefill. The conversation must end with a user message.
```

The run dies mid-conversation. Because the client only produces the prefill shape on
SOME turns (continuation after truncation, certain compaction states), the failure is
intermittent, which invites two wrong fixes: retrying, and pinning providers.

## Context / Trigger Conditions

- The exact error above, prefixed with a host name: `[Azure]`, `[Amazon Bedrock]`,
  `[Google]` (Vertex), or `[Anthropic]`.
- Model id is an Anthropic model via OpenRouter (`openrouter/anthropic/...`).
- Same pipeline succeeded on other runs with no config change.
- A `provider.only` / `provider.ignore` routing pin was added and the error recurred
  from a different (or eventually the same) host.

## Why the obvious fixes fail (measured, one project, 4 host families)

1. **Ignore-listing the failing host** grows one corpse at a time: Azure, then
   "Claude Platform on AWS", then Anthropic first-party each rejected identically.
2. **Positively pinning the one host not yet observed rejecting** (Vertex) held for
   two runs, then rejected too. The green runs were conversation-shape luck — those
   conversations never happened to end a request on an assistant turn. N green runs
   is a claim about those runs' shapes, not about the host.
3. **Advertisement surfaces carry no signal**: no endpoint lists prefill in
   `supported_parameters` (`/api/v1/models/<id>/endpoints`), so you cannot select a
   safe host by reading metadata.

## Solution

Change the MODEL FAMILY for the affected seat; select the replacement with a live
behavioral probe, not metadata.

The probe — a minimal prefill-shaped request per candidate:

```bash
curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"<candidate>","max_tokens":16,"messages":[
       {"role":"user","content":"Complete this sentence."},
       {"role":"assistant","content":"The capital of France is"}]}'
```

Read the result on two axes:
- **Crash-safe**: returns 200 instead of the prefill error (this is the axis that
  kills the failure class).
- **Semantically correct**: the completion CONTINUES the prefilled text ("Paris")
  rather than answering as a fresh turn. Measured 2026-08-17: deepseek-chat-v3.1 and
  gemini-3.1-pro-preview continued correctly; grok-4.5 returned 200 but ignored the
  prefill content. A crash-safe-but-ignoring model survives the loop with occasional
  confused turns; weigh that against capability for the seat.

Also: remove any provider pin keyed to the old model. If the pin is keyed
dynamically off the model constant, changing the model silently re-aims the pin at a
host that does not serve the new model.

## Verification

The previously-dying pipeline stage completes end-to-end on the new seat, including
runs long enough to hit the conversation shapes that produced prefill before.
(Observed: two full agent review stages green after the change, at ~1/3 the token
price of the Opus seat they replaced.)

## Notes

- Anthropic's NATIVE API supports assistant prefill; the rejection is an
  OpenRouter-host normalization behavior. Going direct-to-Anthropic (not via
  OpenRouter) is an alternative fix when credentials allow.
- Avoid pinning standing infrastructure to `-preview` model ids even when they probe
  best — a retired id fails at the first model call later.
- If the client grows a config to stop emitting prefill, the Anthropic seat becomes
  eligible again; pre-register that as the revisit condition.

See also: `anthropic-sdk-via-openrouter` (same OpenRouter domain, different problem:
env-var credential fallback).

## References

- OpenRouter model endpoints API: https://openrouter.ai/docs (endpoints,
  supported_parameters — verified to carry no prefill flag as of 2026-08-17)
