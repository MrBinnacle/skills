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

A **close ritual** writes durable session state and commits it before the packet is produced. This skill runs the full close: it writes the state file, commits it, then produces the packet that records the post-commit `HEAD`.

The order is fixed by a constraint, not a preference. The close commits, which moves `HEAD`. The packet then records `HEAD`. Reversed, the close moves `HEAD` out from under a packet that already recorded it, and the receiver rejects that packet as stale in the next session.

Documenting the order does not hold it. Whoever types the second command cannot see the effect of the first. So the tool enforces it structurally: `write_state.py` commits first, and only then does `snapshot_state.py` record `HEAD` into the packet.

```json
"close_commit": { "contains": "RITUAL:" }
```

**Stable contract:** the `close_commit.contains` key, and that produce mode refuses a packet whose `HEAD` commit message does not contain that value. **Illustrative:** `RITUAL:` itself — that is one project's marker, and yours is whatever string your close reliably writes into its commit message.

`contains` is a literal substring test, not a regex. `"^RITUAL:"` matches nothing and would refuse every packet.

A project that declares no `close_commit` is unaffected.

This establishes that `HEAD` is *a* close commit, not that it is *this* session's. A session that committed nothing still sits on the previous close and passes.

## Procedure

1. Run `write_state.py` with the objective, next action, and `$ARGUMENTS` purpose. This writes the durable state file and commits it with the `close_commit` marker.
2. Run `snapshot_state.py` with the objective, next action, and `$ARGUMENTS` purpose. This produces the packet scaffold recording the post-commit `HEAD`.
3. Open the generated packet.
4. Replace every `__REQUIRED__` marker.
5. Record failed approaches and null results in time order.
6. Record decisions with their reasons.
7. Add each load-bearing claim with `verified` or `unverified` status.
8. Use typed `path`, `commit`, or `command` probes for verified claims.
8a. Use a `command` probe only when the config authorises that exact command. An unlisted command probe rejects the packet.
9. Label `skills_dispatched` as `telemetry` only when an event source exists.
10. Otherwise use `model-reported` and preserve that evidence limit.
11. Reference source artifacts. Do not copy their contents.
12. Run `validate_packet.py` in produce mode.
13. Claim handoff readiness only after an `ACCEPTED` receipt.
14. Return the packet path, packet ID, HEAD, and exact receiver command.

Example state write:

```bash
python <skill-dir>/write_state.py \
  --config .claude/session-boundary.json \
  --objective "<bounded outcome>" \
  --next-action "<exact action>" \
  --purpose "$ARGUMENTS" \
  --repo-root .
```

Example packet scaffold:

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

Band rotation (removing stale session-band index stubs from the state file) is out of scope. The convention is carried as prose in the project's state file, not enforced by this skill. No enforcing surface exists; the operator manages it manually.
