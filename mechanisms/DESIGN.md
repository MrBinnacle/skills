# Mechanisms: shared contract

Three Pi extensions that enforce what can be observed, instead of cards asking the model to
remember it. [README.md](README.md) names the card each one enforces. Pi loads each
subdirectory's `index.ts` from this directory (settings
`extensions: ["<worktree>/mechanisms"]`). Files without `index.ts` (like `shared/`) are not
loaded as extensions; tests (`*.test.ts`) live inside subdirectories so Pi never loads them.

| Extension | Directory | Pi surface |
|---|---|---|
| Verification gate | `verify-gate/` | `session_start` (config load), `before_agent_start`, `tool_result`, `agent_before_settle` |
| In-process reviewer | `reviewer/` | `/review` command, `review_diff` tool, `createAgentSession()` |
| Session-boundary packet | `session-packet/` | `/packet-close`, `/packet-open` commands, `agent_before_settle` (fill validation), `session_start` check |

## Layout rule: pure core, thin adapter

Each extension keeps its logic in pure modules (no Pi imports, no process state) with
`bun test` suites beside them, and an `index.ts` adapter that only wires Pi events to the core.
Pi supplies `@earendil-works/pi-coding-agent` and `typebox` at runtime. **Never install a
physical copy of either next to this code** (a duplicate `typebox` can break schema handling).
Adapters use `import type` from Pi where they can. There is no `package.json` and no
`node_modules` here.

Run all tests: `bun test mechanisms` from the worktree root.

## Project config: `.pi/engineering-env.json`

One file per project, read directly by the extensions (`shared/config.ts`). It is not in
`.pi/settings.json` because Pi does not load project settings for an untrusted project
(observed: `-p` mode, `isProjectTrusted() === false`, project keys absent from
`getSettings()`), and Pi's `Settings` type has no slot for extension keys. The file holds only
patterns and paths; nothing in it is executed except commands the operator lists in
`sessionPacket.receiverChecks` / `trustedProbeCommands`, which the packet runs only on an
explicit command.

```json
{
  "checkCommands": ["\\bbun test\\b", "\\bpytest\\b"],
  "sessionPacket": {
    "dir": ".pi/session-packets",
    "receiverChecks": [{ "name": "clean-tree", "command": "git diff --quiet && git diff --cached --quiet" }],
    "trustedProbeCommands": [],
    "closeCommit": { "contains": "RITUAL:" },
    "wakeConditions": ["A load-bearing claim fails its probe."]
  }
}
```

## Observed Pi 1.1.0 behavior these extensions rely on

- A continuation requested from `agent_before_settle` fires `agent_start`/`agent_end` again but
  not `input` or `before_agent_start`. The gate resets per-run state on `before_agent_start`, so
  its one-nudge limit holds across the continuation. `context.canContinue` read `false` and the
  continuation still ran; the gate does not consult it.
- A user prompt typed while the agent is busy is queued, and the loop drains queued messages
  **before** `agent_before_settle` fires (`agent-session.js`, `_dispatchTurnEndBoundary` returns
  `hasQueuedMessages()`). So two user prompts can form one run: observed 2026-10-10 in
  interactive session `<session>`, an `edit` in prompt N got its nudge at the settle after prompt
  N+1 (queued 26 ms after N's final message). The same two prompts sent sequentially over RPC
  (`rpc_drive.py`, haiku, 2026-10-10) nudged in-run. A "run" for the gate is Pi's run, not one
  user prompt.
- In `--mode json`, the gate's nudge appears as an `entry_appended` event with a
  `custom_message` entry (`customType: "verify-gate"`).
- `createAgentSession({ tools })` is an allowlist over custom tools too: a `customTools` entry
  not named in `tools` is inactive. The reviewer names `submit_review` explicitly.
- Git Bash rewrites a leading `/word` argument into a Windows path. Run slash commands through
  `pi -p` with `MSYS_NO_PATHCONV=1`.
- Per `extensions.md`, JSON and print modes have no UI, so adapters report through
  `console.error` when `ctx.hasUI` is false instead of relying on `ctx.ui.notify`.

## Live proofs (scratch repo, 2026-10-10)

- Gate fires: edit with no check → `verify-gate` entry → continuation ran `bun test` → settled
  with no second nudge. Gate quiet: edit then `bun test` → no entry.
- Reviewer: planted off-by-one in an untracked `sum.ts`; `/review` returned two typed findings
  (`R…-F1` critical at `sum.ts:3` with the exact line as evidence; `R…-F2` missing test), status
  `nominal`, active tools `read, grep, find, ls, submit_review`, cost $0.03.

Missing file: every extension uses its defaults. Malformed file: the extension reports the
error (notification, or the gate's continuation text) and does not guess.
