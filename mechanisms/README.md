# Mechanisms

A card tells the model what to do. A mechanism fires on the event itself and does not wait to
be remembered. This directory holds the mechanisms that back rules in this collection: published
cards, candidates not yet admitted, and one rule no card states. Each one names what it backs
and the harness event it fires on. Today every mechanism here
is a Pi extension; the shared contract, the layout rule and the Pi 1.1.0 behaviour they rely on
are in [DESIGN.md](DESIGN.md).

Why a second column exists: on 2026-10-10 an agent with four of this collection's cards loaded
edited a file and settled without running a check; the verification gate, not a card, is what
made the next run check. That observation is recorded in the operator's private session
handoff, not in this tree, so it is one session, one agent, unverifiable here, and not a
measured verdict.

| Mechanism | What it backs | Fires on |
|---|---|---|
| [`verify-gate/`](verify-gate/) | **No published card.** The rule is "a run that edited must run a check before it settles"; no card in this collection states it. [`vacuous-check`](../skills/engineering/vacuous-check/SKILL.md) and [`mocked-stub`](../skills/engineering/mocked-stub/SKILL.md) are the next question — whether the check that ran could fail — and the gate does not read that. | `tool_result` records each edit and each check (through `bash` or `powershell`); `agent_before_settle` refuses to settle a run that edited and ran no check, once per run. Files outside the session's project root are not tracked: measured 2026-10-10 over the first day, 7 of 8 nudges named handoff files outside every repository, where no check applies. Full event list in [DESIGN.md](DESIGN.md) |
| [`eol-guard/`](eol-guard/) | `uniform-eol` (candidate in `_quarantine/`, not admitted). The card's `guard-design.md` names the two blind spots of a typical guard - a mixed-endings predicate and a project-rooted scope - and this guard closes the first: it compares each tracked file's endings against HEAD and reports a uniform LF-to-CRLF or CRLF-to-LF conversion. The second is a limit by design: the guard reads one repository, the one the session runs in. | `tool_result` after `write`, `edit`, `bash` or `powershell`; a converted file gets a note appended to the tool result the model reads, once per run per file. Live proof 2026-10-10: a Python `read_text`/`write_text` round trip on a 5-line LF file produced the note and the model quoted it back |
| [`reviewer/`](reviewer/) | `reviewer-horizon` (candidate in `_quarantine/`, not admitted), [`disposition-schema`](../skills/orchestration/disposition-schema/SKILL.md), [`decision-rights`](../skills/orchestration/decision-rights/SKILL.md) | `/review` command and `review_diff` tool; opens a fresh read-only session with a brief that separates the task, the evidence and the decision, and returns typed findings |
| [`session-packet/`](session-packet/) | [`im-down`](../skills/engineering/im-down/SKILL.md), [`im-up`](../skills/engineering/im-up/SKILL.md) | `/packet-close` and `/packet-open` commands; `agent_before_settle` validates a fill |

## See it fire

From the repository root, with Pi installed:

```sh
node mechanisms/verify-gate/demo.mjs
```

It needs no API key and takes a few seconds. It runs Pi's own agent loop twice on a
throwaway project, with Pi's real `edit` and `bash` tools. The agent is asked to give every
order a 10% discount and writes `subtotal * 0.1`, a bug the project's test catches.

- **Run 1, gate not loaded.** The agent edits, says "Done.", and the run ends. The demo then
  runs the project's tests itself, and they fail: the bug would have shipped.
- **Run 2, `verify-gate/` loaded as shipped.** After "Done." the gate's message appears, the
  agent runs `npm test`, the test fails, and the agent's last reply quotes the failure.

The model's replies are scripted, so this shows what the gate does, not how a real model
responds to it. The last reply is built from the real test output in the transcript. The demo
checks its own result and exits non-zero when the gate does not fire. It finds Pi through the
managed install under `~/.pi/agent/install/`, then `npm root -g`; set `PI_CODING_AGENT_PACKAGE`
to the `@earendil-works/pi-coding-agent` directory to point it elsewhere. Checked with Pi 1.5.0
on Windows on 2026-11-08; not run on Linux or macOS.

`shared/` holds the project-config reader every mechanism uses. It has no `index.ts`, so Pi
does not load it as an extension.

## Loading and testing

Point Pi's `extensions` setting at this directory. Run `bun test mechanisms` from the
repository root. There is no `package.json`, lockfile or `node_modules` here, and there must
not be: Pi supplies `@earendil-works/pi-coding-agent` and `typebox` at runtime, and a second
physical copy of `typebox` breaks schema handling.

Tests sit beside the code as `*.test.ts` inside each subdirectory, where Pi never loads them.
This directory has no `SKILL.md`, so the card validators do not walk it.
