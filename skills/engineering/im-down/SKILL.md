---
name: im-down
description: Use when you are ending a Claude Code work session and the next session must resume from a verified packet instead of from conversational memory.
disable-model-invocation: true
---

# I'm Down

You are signing off. This skill is the producer side of the session-boundary contract. Its receiver is `im-up`.

## Stable contract

The next session must take the correct first action without trust in conversational memory.

The receiver contract in `PACKET-FORMAT.md` defines the producer output.

## Preflight

1. Read `.claude/session-boundary.json`.
2. Stop if the config or packet directory is absent.
3. Treat `$ARGUMENTS` as the next-session purpose.
4. Stop if `$ARGUMENTS` is empty.
5. Confirm the exact objective and next action from current repository state.

## The close and the packet are one action

A **close ritual** writes durable session state and commits it before the packet is produced. One public entrypoint owns the full sequence: write the state file, commit it (moving `HEAD`), then produce the packet that records the post-commit `HEAD`. Callers cannot reorder those stages.

```json
"close_commit": { "contains": "RITUAL:" },
"state_file": ".claude/session-state.json"
```

**Stable contract:** the `close_commit.contains` key, the `state_file` key, and that produce mode refuses a packet whose `HEAD` commit message does not contain the close marker. **Illustrative:** `RITUAL:` itself — that is one project's marker, and yours is whatever string the close writes into its commit message.

`contains` is a literal substring test, not a regex. `"^RITUAL:"` matches nothing and would refuse every packet.

A project that declares no `close_commit` is unaffected by the marker check; the merged close still requires `state_file`.

## Procedure

1. Run `close_session.py` with the objective, next action, and `$ARGUMENTS` purpose. This is the only close command: it writes durable state, commits with the `close_commit` marker, runs the receiver checks, and writes the packet scaffold at the post-commit `HEAD`.
1a. A red receiver check refuses the packet; the state commit stands. Fix the cause now, while this session holds the context, and close again.
2. Open the generated packet path from the script's JSON output.
3. Replace every `__REQUIRED__` marker.
4. Record failed approaches and null results in time order.
5. Record decisions with their reasons.
6. Add each load-bearing claim with `verified` or `unverified` status.
7. Use typed `path`, `commit`, or `command` probes for verified claims.
7a. Use a `command` probe only when the config authorises that exact command. An unlisted command probe rejects the packet.
8. Label `skills_dispatched` as `telemetry` only when an event source exists.
9. Otherwise use `model-reported` and preserve that evidence limit.
10. Reference source artifacts. Do not copy their contents.
11. Run `validate_packet.py` in produce mode.
12. Claim handoff readiness only after an `ACCEPTED` receipt.
13. Return the packet path, packet ID, HEAD, and exact receiver command.

Example close (one command):

```bash
python <skill-dir>/close_session.py \
  --config .claude/session-boundary.json \
  --objective "<bounded outcome>" \
  --next-action "<exact action>" \
  --purpose "$ARGUMENTS" \
  --repo-root .
```

Example validation after the packet body is filled:

```bash
python <skill-dir>/validate_packet.py <packet.md> \
  --mode produce \
  --repo-root . \
  --config .claude/session-boundary.json
```

## When the project owns its own close sequence

`close_session.py` writes its own state file and generates its own commit message. A project whose close commits a caller-authored message, or decides by judgement what belongs in the commit, drives the packet stage directly with `snapshot_state.py`:

```bash
python <skill-dir>/snapshot_state.py \
  --config .claude/session-boundary.json \
  --objective "<bounded outcome>" \
  --next-action "<exact action>" \
  --purpose "$ARGUMENTS" \
  --repo-root .
```

`snapshot_state.py` runs the receiver checks, refuses when one is red, and otherwise writes the packet scaffold and prints its path. It does nothing else.

That caller now owns the ordering guarantee `close_session.py` holds inside one process: commit first, snapshot second, then assert that the packet's recorded head equals `HEAD` measured after the commit. A caller that skips the assertion ships packets the receiver rejects as stale.

Use `close_session.py` unless the project's close needs that control.

## Boundary limits

The operator runs `/clear`. The producer owes them a **safe-to-clear** verdict, computed from five checks and never asserted. `/clear` is the one action at a session boundary whose cost is one-way, so an `ACCEPTED` receipt is not the verdict; it is the first check.

1. The packet re-validates `ACCEPTED` at the current `HEAD`, not the `HEAD` it was minted against.
2. `HEAD` equals the packet's recorded head and the remote ref.
3. The working tree is clean apart from the exclusions the boundary config declares.
4. Every long-running job the session launched is finished, judged on two signals: process state, and output or CPU. A flat log alone is not a verdict; a job can sit silent for an hour while its worker burns a core.
5. Everything the next session needs is in committed state. A scratchpad path and the conversation are not committed state.

Report residual risk beside the verdict even when it is yes: an unpushed branch, an untracked file, a job whose output lands where the durable state does not name it.

Produce the packet after the session's final commit. A later commit moves HEAD and the receiver rejects the packet as stale. Keep the packet directory out of version control.

`close_commit` checks that the close happened, not that nothing follows it. A commit made after an accepted packet still invalidates it, and the stale-HEAD check is what catches that.

Do not install a Stop hook in this version. A Stop hook fires after ordinary responses and misses interrupts.

Native Claude Code transcripts remain the abnormal-exit recovery path. This packet is an audited execution bootstrap.

Band rotation (removing stale session-band index stubs from the state file) is out of scope. The convention is carried as prose in the project's state file, not enforced by this skill. No enforcing surface exists; the operator manages it manually.
