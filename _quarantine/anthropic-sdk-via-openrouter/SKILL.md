---
name: anthropic-sdk-via-openrouter
description: |
  Route Anthropic SDK calls through OpenRouter as a fallback when
  ANTHROPIC_API_KEY is absent but OPENROUTER_API_KEY is present.
  Pattern: anthropic.Anthropic(api_key=OPENROUTER_API_KEY,
  base_url="https://openrouter.ai/api/v1") + provider-prefixed model id
  "anthropic/claude-sonnet-4.6" (note dots, not dashes). The Anthropic SDK
  speaks Anthropic Messages API at the base_url; OpenRouter implements that
  contract at /v1/messages, so the same .messages.create(model=..., tools=...,
  tool_choice=...) call works without any code change beyond the constructor.
  Use when: (1) supporting users on Claude Code subscription auth (no direct
  ANTHROPIC_API_KEY but OPENROUTER_API_KEY available), (2) building any
  Python tool that uses the Anthropic SDK and wants to support
  OpenRouter-only environments without rewriting to use the OpenAI SDK or a
  different API contract, (3) implementing the symmetric fallback to a
  similar pattern on the OpenAI SDK side.
metadata:
  type: pattern
---

# Anthropic SDK via OpenRouter (env-var fallback)

## Problem

The Anthropic Python SDK constructor `anthropic.Anthropic()` resolves
`ANTHROPIC_API_KEY` from the environment by default. When that env var is
absent (e.g., on Claude Code subscription auth, on machines where the
operator only has OpenRouter credentials, on CI where only an
OpenRouter token is provisioned), the constructor raises before any call
goes out.

The naive workaround — rewriting the integration to use the OpenAI SDK
against OpenRouter's chat completions endpoint — abandons the Anthropic
Messages API contract (tool_use schema, system blocks, the
content-block response shape, the `stop_reason` taxonomy, the cache
control markers, etc.). For any non-trivial Anthropic integration, the
rewrite cost is high.

There is a much smaller move: keep the Anthropic SDK; just point it at
OpenRouter's Anthropic-compatible endpoint via the `base_url` override.

## Solution

Construct the Anthropic SDK with both `api_key` and `base_url` overrides:

```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)
```

Use a **provider-prefixed model id** with a DOT separator inside the model
name (OpenRouter's slug convention, NOT Anthropic-direct's dash convention):

```python
response = client.messages.create(
    model="anthropic/claude-sonnet-4.6",   # dot before 6, not dash
    max_tokens=8192,
    system=SYSTEM_PROMPT,
    tools=[...],
    tool_choice={"type": "tool", "name": "extract_clauses"},
    messages=[{"role": "user", "content": "..."}],
)
```

Everything else (tool schema, response parsing for `tool_use` blocks,
retry logic, error handling) is identical to direct-Anthropic. OpenRouter
implements the Anthropic Messages API contract at `/v1/messages`; the SDK
sees the same response shape it expects from `api.anthropic.com`.

## The env-var resolver pattern

The cleanest place to put the fallback is a small helper called by the code
that previously constructed the bare client. Don't push the routing
decision down into the SDK wrapper (the SDK is dumb infra) and don't push
it up to the CLI layer (the fallback is a deployment concern, not a
user-facing choice).

```python
import os
import sys
import anthropic

_DIRECT_MODEL = "claude-sonnet-4-6"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_OPENROUTER_MODEL = "anthropic/claude-sonnet-4.6"


def _make_client() -> tuple[anthropic.Anthropic, str]:
    """Return (client, model_id) resolved from env."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic(), _DIRECT_MODEL

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    if openrouter_key:
        print(
            f"[INFO] ANTHROPIC_API_KEY not set; routing via OpenRouter"
            f" (base_url={_OPENROUTER_BASE_URL}) using OPENROUTER_API_KEY."
            " SDK and tool_use contract are unchanged; only the endpoint differs.",
            file=sys.stderr,
        )
        return (
            anthropic.Anthropic(
                api_key=openrouter_key,
                base_url=_OPENROUTER_BASE_URL,
            ),
            _OPENROUTER_MODEL,
        )

    raise RuntimeError(
        "No API key found. Set ANTHROPIC_API_KEY (direct) or"
        " OPENROUTER_API_KEY (OpenRouter fallback) to proceed."
    )
```

The function returns a `(client, model_id)` tuple because the model name
differs between the two paths. Callers thread `model_id` through to
`messages.create(model=model_id, ...)`.

## Trigger conditions

You are writing or modifying Python code that:

1. Imports `anthropic` and constructs `anthropic.Anthropic()` directly,
   AND
2. Needs to also work in environments where only `OPENROUTER_API_KEY` is
   set (Claude Code subscription auth users, CI with OpenRouter-only
   credentials, end-users without direct Anthropic API access),
   AND
3. Uses Anthropic-specific features (tool_use, system blocks, cache
   control markers, the Messages API response shape) that you don't want
   to rewrite for the OpenAI SDK.

## Verification

After implementing the resolver:

1. **Unit-test the resolver matrix** — all four cells of (ANTHROPIC_API_KEY × OPENROUTER_API_KEY):
   - Both unset → raises (with both env-var names in the error message)
   - Only ANTHROPIC_API_KEY → direct path, no `base_url` kwarg, no stderr warning, bare model id
   - Only OPENROUTER_API_KEY → fallback path, `base_url` kwarg set, stderr warning emitted, prefixed model id
   - Both set → ANTHROPIC_API_KEY wins (test the precedence rule explicitly)
2. **Integration test the threading** — patch `anthropic.Anthropic` constructor to capture `base_url` and `api_key`, call your code's entry point under the OpenRouter env-var, assert the constructor received the correct OpenRouter URL + key and that `messages.create` received the provider-prefixed model id.
3. **Use `monkeypatch.setenv` / `monkeypatch.delenv(raising=False)`** in pytest — NOT direct `os.environ` mutation. Test isolation is critical because env-var state leaks across tests.
4. **Optional live verification** — call the resolver with real `OPENROUTER_API_KEY` set, make one real API call, confirm a valid response comes back. The wiring tests above verify the threading is correct; the live call verifies the URL + model-id are themselves correct vs. OpenRouter's current implementation. (Live calls cost money; gate behind a `live` pytest marker.)

## Notes

- **URL provenance**: `https://openrouter.ai/api/v1` is the OpenRouter API
  base URL. Anthropic Messages endpoint is at `/v1/messages` (per
  OpenRouter's OpenAPI spec). The Anthropic SDK appends `/messages` to the
  configured `base_url` automatically for `.messages.create()` calls.
  Verified against OpenRouter docs (`https://openrouter.ai/docs/quickstart`)
  as of 2026-06-09.
- **Model-id slug convention**: OpenRouter uses **dots** in version
  numbers (`claude-sonnet-4.6`), NOT dashes (`claude-sonnet-4-6` which is
  Anthropic-direct's convention). Getting this wrong produces a "model not
  found" error from OpenRouter, not a silent fallback to a different model.
- **The `ANTHROPIC_BASE_URL` env var** (which Claude Code itself uses) is
  set WITHOUT the `/v1` suffix — Claude Code's internal SDK config
  appends `/v1` automatically. When YOU construct
  `anthropic.Anthropic(base_url=...)` directly, you must include `/v1`
  explicitly. Easy to miss when copy-pasting from Claude Code docs.
- **Precedence**: this pattern always prefers direct ANTHROPIC_API_KEY when
  both are set (direct path is cheaper per-token + lower latency since there's
  no intermediary). The opposite precedence (always route via OpenRouter)
  could be useful in some deployment contexts but is not the default.
- **OpenRouter's cost surface**: OpenRouter charges per-call with a small
  margin over the underlying provider's price. The `response.usage.cost`
  field returned by OpenRouter (when present) is the authoritative cost
  for that call; falling back to local pricing estimation if absent.
- **DON'T** put the routing decision inside the SDK wrapper class — that
  couples deployment concerns to library code and makes it harder to test
  the two paths independently.
- **DON'T** introduce a CLI flag for "use OpenRouter" — the env-var
  presence/absence already encodes operator intent, and adding a flag
  creates ambiguous-state cases (env var set + flag set the other way).

## Example (from skill-harness 2026-06-09)

The skill-harness project hit this exact need. The case study author runs
on Claude Code subscription auth; the project's extractor on `skill init`
constructed `anthropic.Anthropic()` directly. The case study explicitly
documented this gap as "HALT 2." Phase B (commits `b5b9fe6` + `7d86687`)
applied this pattern to close the gap.

Full commit history of the implementation:
- `b5b9fe6` — initial implementation with `_make_extractor_client()` helper
- `7d86687` — fix-cycle: remove dead constant + add the "both keys set →
  direct path wins" matrix test for precedence

Test file: `tests/extractor/test_extractor_openrouter_fallback.py`. The
integration test (`test_call_extract_clauses_uses_openrouter_when_anthropic_key_absent`)
patches `anthropic.Anthropic` at the constructor level and asserts both
`base_url` and `api_key` thread through, plus the provider-prefixed
`model` reaches `messages.create`.

## References

- OpenRouter API quickstart: https://openrouter.ai/docs/quickstart
- OpenRouter model registry (Anthropic models): https://openrouter.ai/models?q=anthropic
- Anthropic Python SDK base_url docs: https://github.com/anthropics/anthropic-sdk-python (search `base_url`)
- Skill-harness Phase B commit: see `b5b9fe6` + `7d86687` on `main` for a worked example
