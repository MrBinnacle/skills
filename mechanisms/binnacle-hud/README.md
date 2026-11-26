# binnacle-hud (Pi)

The Binnacle HUD for Pi. It is a rewrite for Pi of the Claude Code mod in
[`mods/binnacle-hud/`](../../mods/binnacle-hud/README.md), not a port, and it has three parts:

- **Log.** Thoughts you keep beside the session. They never reach a model request.
- **Memory.** Lines you choose to give the agent. They go into its system prompt only after you
  send them, and they stay there through `/compact`.
- **Observer.** A second model call that reads the new turns at natural pauses. It raises at most
  one note, and only when it can quote the line in the record that supports it.

The consent rules are tested end to end. `consent.test.ts` runs Pi's real agent loop, session
store and extension loader, with only the model's replies scripted. It captures every request the
model receives. It checks that the Log and an unsent Memory draft never reach any request; that sent
Memory reaches the agent, also after `/compact`, and never the observer; and that a note reaches
the agent only under the rule below, and not after you leave `forward`. With the unit tests beside
it, it goes red on each of eleven faults planted in `index.ts` and `observer.ts` (checked
2026-11-26, Pi 1.6.1). One of them found that a text search for the Memory line would pass
after `/compact` even with Memory removed. Pi keeps the old system message and adds a patch that
sets the section to null, so the test folds those patches the way a provider reads them.

## Use

| You do | What happens |
| --- | --- |
| `alt+h` | Opens the panel as an overlay that does not take the keyboard. Press again to move the keys between the panel and the prompt. |
| `/log <text>` | Keeps a thought in the Log. |
| `/hud add <line>`, `/hud send` | Adds a Memory line; sends Memory after you confirm the lines. Sending an empty Memory withdraws it. |
| `/hud observer off\|panel\|forward` | Sets the observer for every session. `off` makes no call. `panel` keeps notes with you. `forward`, the default, also gives a note to the agent. Stored in `binnacle-hud.json` in Pi's agent directory; another running Pi reads it when its next session starts. Leaving `forward` keeps any note still waiting for your next message with you. |
| `/hud close` | Closes the panel. |

In the panel: Enter keeps a thought, Tab switches between Log and Memory, ↑ reaches the items,
`x` removes or dismisses, `k` marks a note known, `w` marks it wrong, Enter on a note opens its
details and the quoted evidence, `ctrl+s` sends Memory, and Esc returns to the prompt. The line
above the editor shows the newest open note until you have sent two more prompts.

## When a note reaches the agent

The observer runs on the session's model, after every 6 agent turns, or when the agent hands back
with at least 3 turns unread. It runs one look at a time, and never starts an agent turn. In
`forward` mode a note goes to the agent unless the observer judged the agent already knows it:

- **Agent busy:** the note is steered into the run before its next model call.
- **Agent idle:** the note goes out with your next message.

Two dismissals in a row double the wait between looks; reading a note resets it. A note whose
quote is not in what the observer was shown is dropped. Each note records the prompt version that
produced it, so your `k`, `w` and `x` marks are labels for that version.

## The observer prompt is unmeasured

Whether this prompt raises notes worth an interruption is unmeasured.
[`eval/`](eval/) replays it on recorded sessions with [Inspect AI](https://inspect.aisi.org.uk/):

```sh
bun mechanisms/binnacle-hud/eval/slices.ts <out> <transcript.jsonl>... [--notes forwarded.jsonl]
inspect eval mechanisms/binnacle-hud/eval/observer_task.py -T samples=<out>/samples.jsonl \
  --model anthropic/<model> --log-dir <out>/logs --log-format json
bun mechanisms/binnacle-hud/eval/report.ts <out>/logs/<log>.json <out>/labels.md
```

`slices.ts` builds each sample with the shipped `SYSTEM`, `serialize` and `userMessage`, so the
eval tests the prompt that ships. `report.ts` applies the shipped parser and quote check, then
writes a sheet for a person to label. Transcripts hold private work: keep `<out>` outside every
repository. A first run on 2026-11-26 covered 73 of 199 samples before the account ran out of
credit. Its notes are not yet labelled, so it supports no verdict.

## Not checked

The overlay was not driven in a live terminal; `panel.test.ts` renders it with Pi's TUI kit.
The observer was not run on Linux or macOS.
