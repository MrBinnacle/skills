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

1. Run `close_session.py` with the objective, next action, and `$ARGUMENTS` purpose. This is the only close command: it writes durable state, commits with the `close_commit` marker, and writes the packet scaffold at the post-commit `HEAD`.
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

## Boundary limits

Do not run `/clear`. The operator controls session creation.

Produce the packet after the session's final commit. A later commit moves HEAD and the receiver rejects the packet as stale. Keep the packet directory out of version control.

`close_commit` checks that the close happened, not that nothing follows it. A commit made after an accepted packet still invalidates it, and the stale-HEAD check is what catches that.

Do not install a Stop hook in this version. A Stop hook fires after ordinary responses and misses interrupts.

Native Claude Code transcripts remain the abnormal-exit recovery path. This packet is an audited execution bootstrap.

Band rotation (removing stale session-band index stubs from the state file) is out of scope. The convention is carried as prose in the project's state file, not enforced by this skill. No enforcing surface exists; the operator manages it manually.
