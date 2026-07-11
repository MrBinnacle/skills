---
name: claude-code-stop-hook-envelope
description: Claude Code Stop/SubagentStop hooks receive a JSON envelope on stdin, NOT the response text — a hook that greps stdin never fires and never errors. Read transcript_path for the last assistant turn.
---

# Claude Code Stop Hook Envelope

## Problem

You write a Claude Code Stop hook to react to the assistant's response — e.g., fire a marker when the response contains `[values decision]`, or flag novel vocabulary, or continue a loop. The naive shape is:

```bash
response=$(cat)                       # WRONG for Stop hooks
if echo "$response" | grep -qF '[values decision]'; then
  echo "TRIGGER"
fi
```

This **silently never fires**. The hook exits 0, settings.json shows it wired, every gate looks green — and the control does nothing. This is the worst failure class: a present-but-dead control that manufactures false assurance. In the origin incident this exact bug left two discipline-hook predicates dead from the day they were wired, with every gate reading green, until an audit asked whether they had ever fired.

## Context / Trigger Conditions

Use this skill when **any** hold:

- A `Stop` or `SubagentStop` hook does `$(cat)` / reads stdin and greps it for text you know was in the assistant's response, but the hook never triggers.
- A hook is wired in `.claude/settings.json` under `"Stop"`, exits cleanly, but has had **no observable effect** over many sessions ("dead-but-nominal").
- You ported a PreToolUse/PostToolUse hook (which *does* get the data inline) to a Stop event and it stopped working.
- You need to match a string in, or tokenize, the **last assistant turn** from a Stop hook.

## Root cause: the stdin schema is event-specific

Claude Code hooks all receive JSON on stdin, but **the schema depends on the event**:

| Event | stdin payload (relevant keys) | Where is the assistant text? |
|---|---|---|
| `PreToolUse` | `tool_name`, `tool_input` | n/a (no response yet) |
| `PostToolUse` | `tool_name`, `tool_input`, `tool_response` | in `tool_response` |
| `Stop` / `SubagentStop` | `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active` | **NOT in the envelope — read `transcript_path`** |
| `UserPromptSubmit` | `prompt` | n/a |

A Stop hook's stdin is roughly:

```json
{"session_id":"66fc0458-…","transcript_path":"/…/<uuid>.jsonl","cwd":"/…","hook_event_name":"Stop","stop_hook_active":false}
```

So `response=$(cat)` gives you *that JSON*, not the response. Greping it for a marker that lives in the assistant's prose matches nothing → exits 0 → looks fine → does nothing.

## Solution

Read the envelope, resolve `transcript_path`, extract the last assistant message's text, then run your check against THAT.

```bash
#!/usr/bin/env bash
set -euo pipefail

HOOK_INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // empty')

# Missing/unreadable transcript: no-op rather than block.
[ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ] || exit 0

# Transcript is JSONL (one event per line). The last assistant turn's text
# lives under .message.content[] (type=="text") in current builds; older/
# variant builds put role/content at top level. Handle both with --slurp.
LAST_OUTPUT=$(jq -rs '
  [ .[] | select(.role == "assistant" or (.message // empty | .role) == "assistant") ]
  | if length == 0 then ""
    else last
      | (if .message then .message else . end)
      | .content | map(select(.type == "text")) | map(.text) | join("\n")
    end
' "$TRANSCRIPT_PATH" 2>/dev/null || echo "")

# NOW run your real check against the assistant text:
if echo "$LAST_OUTPUT" | grep -qF '[values decision]'; then
  echo "TRIGGER: values-decision-marker"
fi
```

Key points:
- `jq -rs` (`--slurp`) reads the whole JSONL file into an array so you can pick `last`.
- The `(if .message then .message else . end)` branch handles both transcript shapes (nested `.message` vs top-level) without assuming one.
- Guard with `|| exit 0` / `2>/dev/null` so a missing or malformed transcript no-ops instead of blocking the Stop event.
- Filtering to `.type == "text"` drops tool-use/thinking blocks so you grep prose only.

## Verification

The decisive test is the **negative-looking-positive**: feed a realistic envelope and confirm the OLD shape fails while the NEW shape works.

```bash
# Simulate the envelope a Stop hook actually receives:
TRANSCRIPT=$(mktemp --suffix=.jsonl)
printf '%s\n' '{"message":{"role":"assistant","content":[{"type":"text","text":"I recommend X. [values decision] on scope."}]}}' > "$TRANSCRIPT"
ENVELOPE=$(jq -nc --arg t "$TRANSCRIPT" '{session_id:"test",transcript_path:$t,hook_event_name:"Stop",stop_hook_active:false}')

# OLD (broken) hook: greps the envelope → no match → silent.
echo "$ENVELOPE" | bash old-hook.sh        # expected: (nothing) — the bug

# NEW (fixed) hook: resolves transcript → matches.
echo "$ENVELOPE" | bash new-hook.sh        # expected: TRIGGER: values-decision-marker
rm -f "$TRANSCRIPT"
```

If the OLD hook prints nothing here but you *believed* it was working in production, you have just reproduced the dead-but-nominal failure.

## Example

The origin project's review automation had two Stop-hook predicates: a values-decision marker detector (`response=$(cat); grep -qF '[values decision]'`) and a vocabulary-novelty detector (tokenized `$(cat)` against a curated term corpus). Both greped the JSON envelope. Neither fired once between deployment and the audit that caught them — not because any error surfaced, but because none existed to surface. `.claude/settings.json` showed both wired; every gate read green. The audit question that found them: "has this control *ever* fired?"

The contrast case in the same repo was a **PreToolUse** hook reading `.tool_input.file_path` — correct precisely because that event *does* deliver its data inline, which is what makes the Stop-event difference so easy to miss when porting.

## Notes

- **`stop_hook_active`** guards against infinite loops: if your hook emits `{"decision":"block",...}` to continue the agent, that re-invocation sets `stop_hook_active:true`. Check it before blocking again.
- **Transcript format is not a stable contract.** It's JSONL today and the assistant-message shape has varied across builds (`.message.content` vs top-level `.content`). The dual-branch `jq` above is defensive on purpose. Re-verify against `transcript_path` on a real run if a future build changes it.
- **Don't grep the whole transcript** for your marker — that matches *any* turn in the session, including ones quoting the marker in documentation. Extract the **last** assistant turn first (`last`), then match.
- **Fail open for discipline hooks, fail closed only deliberately.** Missing transcript → `exit 0` (no-op) is right for a *supplemental* trigger. If the hook is a hard gate, decide explicitly and emit a blocking decision instead of silently passing.
- **The general audit rule this belongs to:** "is this control alive?" must be answered by *exercising* the control — never by its presence in config.

## References

- Claude Code Hooks documentation (event input schemas): https://docs.claude.com/en/docs/claude-code/hooks
- Verified-correct reference implementation: Trail of Bits' public [`skill-improver` plugin stop hook](https://github.com/trailofbits/skills) (`plugins/skill-improver/hooks/stop-hook.sh` — reads `HOOK_INPUT=$(cat)` → `jq -r '.transcript_path'` → `jq -rs` last-assistant extraction).
- Origin incident: [EVIDENCE.md](EVIDENCE.md) — two dead discipline predicates in a personal production project, audit dated 2026-06-03. A narrower variant of the same bug (a vocabulary-corpus Stop hook greping the envelope) was the second dead predicate; its portable lessons are in [gotchas.md](gotchas.md).
