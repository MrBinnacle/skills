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
6. Run the project's durable close now and commit it, when the config declares `close_commit`. Before the snapshot, not after.

## The close and the packet are one action

Their order is fixed by a constraint, not a preference. The close commits, which moves `HEAD`. The packet then records `HEAD`. Reversed, the close moves `HEAD` out from under a packet that already recorded it, and the receiver rejects that packet as stale in the next session.

Documenting the order does not hold it. The person typing the second command cannot see the effect of the first. So declare the requirement and let the tool enforce it:

```json
"close_commit": { "pattern": "RITUAL:" }
```

Produce mode then refuses a packet whose `HEAD` commit message lacks that pattern, and names the repair. A project that declares no `close_commit` is unaffected.

## Procedure

1. Run `snapshot_state.py` with the objective, next action, and `$ARGUMENTS` purpose.
2. Open the generated packet.
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

Example scaffold:

```bash
python <skill-dir>/snapshot_state.py \
  --config .claude/session-boundary.json \
  --objective "<bounded outcome>" \
  --next-action "<exact action>" \
  --purpose "$ARGUMENTS" \
  --repo-root .
```

Example validation:

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
