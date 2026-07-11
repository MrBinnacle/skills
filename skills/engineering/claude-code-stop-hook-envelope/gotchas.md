# gotchas — claude-code-stop-hook-envelope

## [ANTICIPATED]

- **The transcript format is not a stable contract.** JSONL today; the assistant-message shape has varied across builds (`.message.content` vs top-level `.content`). Keep the dual-branch `jq`; re-verify against a real `transcript_path` after Claude Code updates.

- **A missing `jq` reproduces the exact failure this skill fixes.** Stop hooks are commonly wired with a `... 2>&1 || true` tail so a hook failure can't block the session — which means on a machine without `jq`, the hook dies silently and reads as healthy: dead-but-nominal again, via a different door. Check `command -v jq` and decide loud-vs-quiet deliberately.

- **Grepping the whole transcript instead of the last turn.** Earlier turns may quote your marker — documentation, or the session discussing the hook itself — producing false fires. Extract the LAST assistant turn first, then match.

- **Re-fire loops via `{"decision":"block"}`.** If your hook continues the agent, the re-invocation arrives with `stop_hook_active:true`. Check it before blocking again or you loop.

- **Path handling is a fresh way to silently no-op.** `transcript_path` arrives as a native absolute path. The `[ -f "$TRANSCRIPT_PATH" ] || exit 0` guard means any path-shape mismatch (Windows drive letters under a POSIX shell, home-dir munging) doesn't error — it exits 0 and the hook is dead again. Test with one real envelope on the target OS before trusting it.

## [OBSERVED]

*(Append observed gotchas here as they surface. Do not delete entries — gotchas are stress-test signal.)*

- **2026-06-03 / a personal production project:** two Stop-hook discipline predicates — a `[values decision]`-marker detector and a vocabulary-novelty corpus check — greped the stdin envelope for response text. Wired 2026-05-26; zero fires ever; every gate green. Surfaced only by an audit asking "has this control *ever* fired?" — there was no error to notice, so nothing bounded how long it would have persisted. Direct trigger that produced this skill.

- **2026-05-26 / same project — counting-pipeline pipefail trap:** under `set -euo pipefail`, a `count=$( ... | grep ... | wc -l)` pipeline exits 1 whenever the greps filter out every line — i.e., the hook fails on exactly the inputs where `count=0` is the correct answer. Append `|| count=0` to the whole assignment. Found while trial-firing the vocabulary predicate above.
