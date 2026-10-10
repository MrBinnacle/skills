# session-packet

A Pi port of the `im-down` / `im-up` session-boundary packet. The packet format is v1 from
`skills/engineering/im-down/PACKET-FORMAT.md`. The manifest keys stay snake_case. A packet that this
extension produces and fills is `ACCEPTED` by `validate_packet.py` in produce mode and in receive
mode. This was checked once against a real repository. The reverse direction (a Python-produced
packet opened here) was not tested end to end; the Python fixtures pass the structure rules.

## Deliberate deviations from the Python contract

1. **No receiver-check cache and no weekly uncached audit.** `cache_inputs` and
   `receiver_check_cache` are not supported. Every receiver check runs on every open and every close,
   so a check's `status` is only `passed` or `failed`, never `cached`.
2. **No state file and no close commit.** `/packet-close` never commits. It follows the
   `snapshot_state.py` path, where the project owns its own close. The project commits its close
   first. Then `/packet-close` measures that HEAD. The `closeCommit.contains` and unclaimed-HEAD
   refusals enforce this order. Because no state file exists, `/packet-open` does not return a
   `state_read`.
3. **`status_porcelain` is checked.** `validate_packet.py` records it but never compares it. This
   port compares it with the live tree after trimming whitespace, and a mismatch is `status drift`. The
   packet directory is excluded from both the recorded value and the compared value
   (`git status --porcelain -- . ':(exclude)<dir>'`). Without this exclusion, the packet file would
   make its own packet stale.
4. **The fill cannot change the measured facts.** In produce mode, validation of the filled packet
   also refuses a change to `packet_id`, `created_at`, `repository` or `tests`. These are the values
   that `/packet-close` measured.
5. **Receiver checks and trusted command probes run through `sh -c`.** On Windows, `sh` resolves to
   Git's `sh.exe`. `bash` can resolve to WSL's `System32\bash.exe`. Python's `shell=True` uses
   `cmd.exe`.
6. **Receive mode needs a `sessionPacket` section** in `.pi/engineering-env.json`. This replaces
   Python's `--config`. The section may be empty (`{}`). The unclaimed-HEAD check is always on,
   because the packet directory always has a value (default `.pi/session-packets`).
7. **An unreadable packet** (no markers, bad JSON, git failure) returns `{verdict, errors}` only.
   Python behaves the same way.

## Commands

- `/packet-close <objective…>` does these steps in order:
  1. Refuses an empty objective.
  2. Runs every receiver check. If one is red, it refuses and writes no file. The refusal JSON lists
     `failed_receiver_checks` with the output of each failed check.
  3. Refuses when HEAD lacks the `closeCommit` marker or when a prior packet already claims HEAD. It
     makes this check before the agent spends a turn on the fill.
  4. Writes a scaffold to `<dir>/<UTC stamp>-<id8>.md`. The scaffold contains the measured
     repository facts and the `tests[]` entries. `__REQUIRED__` markers stand in for the narrative.
  5. Sends the agent a user message that asks it to fill the scaffold.

  When the agent stops (`agent_before_settle`), the extension validates the file in produce mode. An
  `ACCEPTED` receipt goes to the operator. A `REJECTED` receipt goes back to the agent as a
  continuation, at most twice. After that, the extension gives up and reports the rejection as an
  error.
- `/packet-open [path]` validates the latest packet (or the packet at `path`) in receive mode. It
  notifies the operator with the receipt JSON and also posts the receipt into the session.
- `session_start` (reasons startup, new and resume) runs the same check as `/packet-open`. It runs
  only when the project declares `sessionPacket` and a packet exists. It reports the verdict through
  `ctx.ui.notify`, or through stderr when no UI exists. An exception is reported and never thrown.

### Why two steps for the close

Only the model can write the narrative and the claims, so the close cannot be one mechanical
command. The extension keeps the refusals mechanical. All measurement and refusal happens before the
model is asked to write anything. Validation runs when the agent stops, and nobody needs to remember
to run it. If the agent leaves a scaffold unfinished, that scaffold still claims HEAD, as in Python.
Delete the scaffold, or close again after a new commit.

## Layout

The core modules import nothing from Pi. Process execution is injected as `Exec`, which has the same
shape as `pi.exec`.

| File | Role |
|---|---|
| `packet.ts` | Extracts the manifest. Holds the structure, placeholder and recorded-check rules and the always-zero lint. |
| `repo.ts` | Holds the git assertions (branch, HEAD, porcelain status, path/commit/command probes), the close-commit check, the unclaimed-HEAD check and the shell runner. |
| `validate.ts` | Runs the receiver checks and builds the receipt. |
| `close.ts` | Holds the producer: the snapshot and its refusals, the scaffold, the fill instructions and the fill validation. |
| `settings.ts` | Parses the `sessionPacket` config section. |
| `index.ts` | The Pi adapter. |
| `testkit.ts`, `*.test.ts`, `fixtures/` | The bun tests. They run against real temporary git repositories. |

The adapter tests use a fake `ExtensionAPI`. The `agent_before_settle` continuation path has not been
exercised against a live model.
