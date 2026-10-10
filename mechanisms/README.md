# Mechanisms

A card tells the model what to do. A mechanism fires on the event itself and does not wait to
be remembered. This directory holds the mechanisms that enforce cards in this collection. Each
one names the card it enforces and the harness event it fires on. Today every mechanism here
is a Pi extension; the shared contract, the layout rule and the Pi 1.1.0 behaviour they rely on
are in [DESIGN.md](DESIGN.md).

Why a second column exists: on 2026-10-10 an agent with four of this collection's cards loaded
edited a file and settled without running a check; the verification gate, not a card, is what
made the next run check. That observation is recorded in the operator's private session
handoff, not in this tree, so it is one session, one agent, unverifiable here, and not a
measured verdict.

| Mechanism | Card it enforces | Fires on |
|---|---|---|
| [`verify-gate/`](verify-gate/) | **No published card.** The rule is "a run that edited must run a check before it settles"; no card in this collection states it. [`vacuous-check`](../skills/engineering/vacuous-check/SKILL.md) and [`mocked-stub`](../skills/engineering/mocked-stub/SKILL.md) are the next question — whether the check that ran could fail — and the gate does not read that. | `tool_result` records each edit and each check; `agent_before_settle` refuses to settle a run that edited and ran no check, once per run. Full event list in [DESIGN.md](DESIGN.md) |
| [`reviewer/`](reviewer/) | `reviewer-horizon` (candidate in `_quarantine/`, not admitted), [`disposition-schema`](../skills/orchestration/disposition-schema/SKILL.md), [`decision-rights`](../skills/orchestration/decision-rights/SKILL.md) | `/review` command and `review_diff` tool; opens a fresh read-only session with a brief that separates the task, the evidence and the decision, and returns typed findings |
| [`session-packet/`](session-packet/) | [`im-down`](../skills/engineering/im-down/SKILL.md), [`im-up`](../skills/engineering/im-up/SKILL.md) | `/packet-close` and `/packet-open` commands; `agent_before_settle` validates a fill; `session_start` checks for a packet to open |

`shared/` holds the project-config reader every mechanism uses. It has no `index.ts`, so Pi
does not load it as an extension.

## Loading and testing

Point Pi's `extensions` setting at this directory. Run `bun test mechanisms` from the
repository root. There is no `package.json`, lockfile or `node_modules` here, and there must
not be: Pi supplies `@earendil-works/pi-coding-agent` and `typebox` at runtime, and a second
physical copy of `typebox` breaks schema handling.

Tests sit beside the code as `*.test.ts` inside each subdirectory, where Pi never loads them.
This directory has no `SKILL.md`, so the card validators do not walk it.
