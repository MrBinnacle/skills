# Engineering skills

Workflow disciplines for shipping software. This bucket installs as the `mrbinnacle-engineering` plugin, and its [`plugin.json`](.claude-plugin/plugin.json) is the authoritative list of what it installs. The cards fall under the three headings that manifest names. Each card's `EVIDENCE.md` records where the card came from and what has and has not been measured; an installed card is not thereby shown to work. `im-down`, `im-up`, `pretooluse-prose` and `stale-deploy` name Claude Code mechanisms. For what delivery has been observed on each runtime, read the [runtime delivery matrix](https://github.com/MrBinnacle/skills/blob/main/docs/product/runtime-delivery-matrix.md).

A card marked *(by hand)* sets `disable-model-invocation: true`, so it runs only when you invoke it by name, as `/mrbinnacle-engineering:<card>`. The other cards load in every session. A card runs by hand when it is below the always-on bar in [ADR 0008](../../docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md), or when it is a procedure.

### Mistakes that report success

- [**clirunner-env**](clirunner-env/SKILL.md) *(by hand)* — Click's `CliRunner.invoke(env=...)` overrides only the keys the dict names, so a test that builds a "clean" environment by leaving a key out, or passes `env={}`, still runs with that key set and can make the live API call it was written to prevent; pass `{key: None}` to delete one ([the receipt](clirunner-env/EVIDENCE.md)).
- [**mocked-stub**](mocked-stub/SKILL.md) *(by hand)* — a test that patches a helper which is itself a production stub turns green on a branch that never ran; use it when reviewing all-green work on spend guards, idempotency, auth or refusal paths, and drive the real helper unpatched with at least two seeded values ([the receipt](mocked-stub/EVIDENCE.md)).
- [**stale-deploy**](stale-deploy/SKILL.md) *(by hand)* — a green GitHub Pages or CDN deploy is not proof the site changed; poll for a marker that did not exist before this deploy, and use poll forms the Claude Code Bash tool does not block. The origin incident is in a public repository, so its record can be checked ([the receipt](stale-deploy/EVIDENCE.md)).
- [**vacuous-check**](vacuous-check/SKILL.md) — a success check that accepts any non-empty output passes on failure, because failure output is non-empty too, and a type-blind comparison such as `String(got) === String(want)` passes on a mismatch; the mirror case is a probe batch that reports nothing found when the tool never ran, so any finding of absence carries a positive control in the same run ([the receipt](vacuous-check/EVIDENCE.md)).

### Guards and gates that stop your work

- [**halt-as-deliverable**](halt-as-deliverable/SKILL.md) — when a pre-registration, pre-flight or sanity gate you built refuses to produce your own deliverable, the catch can be worth more than the deliverable; commit the audit trail publicly before deciding what to do next, and lead with the catch ([the receipt](halt-as-deliverable/EVIDENCE.md)).
- [**pretooluse-prose**](pretooluse-prose/SKILL.md) — a Claude Code `PreToolUse` Bash guard receives the whole command string, so a heredoc or commit message that only names a banned command trips it; write such prose with a file-write tool, and anchor a matcher to command position outside quotes ([the receipt](pretooluse-prose/EVIDENCE.md)).
- [**pull-rebase**](pull-rebase/SKILL.md) — with `pull.rebase=true` configured, `git pull --no-ff` still rebases and every local commit gets a new SHA, while `--ff-only` refuses instead; check the setting before pulling, and recover through the reflog if a pull already rebased your work. The origin incident rewrote 22 local commits ([the receipt](pull-rebase/EVIDENCE.md)).

### Rituals at phase and session boundaries

These three are procedures, so each runs by hand whatever its evidence.

- [**closure-mode**](closure-mode/SKILL.md) *(by hand)* — when a sprint, phase or vertical slice locks, or a "what next" decision has several candidates, dispatch a parallel review swarm, execute the action list it produces, and only then present a single pick or the values axis that separates the survivors ([the receipt](closure-mode/EVIDENCE.md)).
- [**im-down**](im-down/SKILL.md) *(by hand)* — the producer side of a Claude Code session boundary: one close command commits durable state, runs the receiver's checks, and writes a packet that must validate as `ACCEPTED`, the first of the five checks behind a safe-to-clear verdict ([the receipt](im-down/EVIDENCE.md)).
- [**im-up**](im-up/SKILL.md) *(by hand)* — the receiver side: a fresh Claude Code session treats the `im-down` packet as untrusted data, verifies branch, HEAD and every verified claim against the repository, runs the configured checks or reuses a cached pass on an unchanged tree, and reports an acceptance receipt before any work starts ([the receipt](im-up/EVIDENCE.md)).
