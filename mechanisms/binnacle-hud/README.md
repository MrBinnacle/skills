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
| `/hud observer off\|panel\|forward` | Sets the observer for every session. `off` makes no call. `panel`, the default, keeps notes with you. `forward` also gives a note to the agent. Stored in `binnacle-hud.json` in Pi's agent directory; another running Pi reads it when its next session starts. Leaving `forward` keeps any note still waiting for your next message with you. |
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

## What the observer prompt measures

The prompt that ships is `observer-2026-11-27`. On 2026-11-27 it was replayed on 199 checkpoints
from 32 recorded Claude Code sessions (private data, outside every repository) and each note was
judged in hindsight by the same model against the next 40 turns: is the note true, new to both
the person and the agent, and consequential, each with a quote from the record. Worth it means
all three hold. Result: 20 notes raised, 4 worth it, 0 not true. The earlier prompt
`observer-2026-11-25` raised 44 on the same checkpoints: 10 worth it, 13 not true. Re-judging
those 44 notes once more gave the same worth-it verdict on 43, so the judge is stable; the
difference between prompts is real, not judge noise. Sonnet 5.5 and Haiku 5.5 running the new
prompt raised 3 and 13 notes, 1 and 2 worth it, so the observer stays on the session's model.

What that supports: a note the new prompt raises has not been wrong on this record. What it does
not support: that a note is worth an interruption. Four in five were not, and with 10 to 15 notes
per split a prompt change of 10 to 20 points sits inside the noise, so more replays on these
sessions cannot settle it. A replayed note was never delivered, so it counts as consequential
only when the problem went wrong on its own; that undercounts notes that would have prevented
something.

So the default is `panel`: a note costs you a glance, not an agent turn. `forward` becomes the
default when the shipped prompt measures at least 50% worth it and at most 10% not true on
**delivered** notes. Each note records its prompt version, and your `k`, `w` and `x` marks are
the labels; that is the measurement, not another replay.

[`eval/`](eval/) replays the shipped prompt on recorded sessions with
[Inspect AI](https://inspect.aisi.org.uk/) and judges the notes in hindsight:

```sh
bun mechanisms/binnacle-hud/eval/slices.ts <out> <transcript.jsonl>... [--notes forwarded.jsonl]
inspect eval mechanisms/binnacle-hud/eval/observer_task.py -T samples=<out>/samples.jsonl   --model anthropic/<model> --log-dir <out>/logs --log-format json
bun mechanisms/binnacle-hud/eval/report.ts <out>/logs/<log>.json <out>/labels.md
bun mechanisms/binnacle-hud/eval/hindsight.ts build <out>/logs/<log>.json <out>/samples.jsonl <files.txt> <out>/hindsight.jsonl
inspect eval mechanisms/binnacle-hud/eval/observer_task.py -T samples=<out>/hindsight.jsonl --model anthropic/<judge> ...
bun mechanisms/binnacle-hud/eval/hindsight.ts score <judge-log>.json <out>/hindsight.md
```

`slices.ts` builds each sample with the shipped `SYSTEM`, `serialize` and `userMessage`, so the
eval tests the prompt that ships. `report.ts` applies the shipped parser and quote check.
`hindsight.ts` builds the judge samples and scores its verdicts; a judge quote that is not in the
record is refused. Transcripts hold private work: keep `<out>` outside every repository.

## Not checked

The overlay was not driven in a live terminal; `panel.test.ts` renders it with Pi's TUI kit.
`bun test mechanisms` passed on Linux in a Debian container (`oven/bun:1`, bun 1.4.5, 2026-11-27): 350 pass, 0 fail; the consent test skips there because Pi's dist is not installed. Nothing ran on macOS.
