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

[Inspect the Memory and heads-up transitions](transitions/README.md).

## Use

| You do | What happens |
| --- | --- |
| `alt+h` or `/hud` | Shows the panel and opens one menu: each open heads-up, then keep a thought, add, send or remove a Memory line, forget a thought, hide the panel. |
| `/log <text>`, `/log` | Keeps a thought in the Log; with no text, asks for it. |
| `/hud add <line>`, `/hud send` | Adds a Memory line; sends Memory after you confirm the lines. Sending an empty Memory withdraws it. |
| **Review Log and draft Memory** in the menu | Select any retained thought and edit a copy. Saving adds it to the draft. The original stays in the Log. |
| **Withdraw approved Memory** or `/hud withdraw` | Review the currently approved lines and confirm removal from future instructions. The working draft stays available. |
| `/hud observer off\|panel\|forward` | Sets the observer for every session. `off` makes no call. `panel`, the default, keeps notes with you. `forward` also gives a note to the agent. Stored in `binnacle-hud.json` in Pi's agent directory; another running Pi reads it when its next session starts. Leaving `forward` keeps any note still waiting for your next message with you. |
| `/hud close` | Closes the panel. |

The panel only displays. It never takes the keyboard, so the prompt is the one place you type,
and every line wraps inside the panel. Pick a heads-up in the menu to read it: the line, why it
matters, the call it needs from you, the details and the quoted evidence. Then:

- **Send to the agent now.** Steers a running agent before its next model call, or starts a turn
  on an idle one. Sending marks the note `u`, worth receiving. A sent note offers no second send.
- **Copy to the clipboard.** The note's text alone; a terminal's mouse selection copies whole
  screen rows, the session behind the panel included.
- **Useful, I knew this, Wrong, Dismiss.** The marks `u`, `k`, `w`, `x` below; each closes the
  note.

The line above the editor shows the newest open note until you have sent two more prompts.

## When a note reaches the agent

The observer runs on the session's model, after every 6 agent turns, or when the agent hands back
with at least 3 turns unread. It runs one look at a time, and never starts an agent turn on its
own; only your Send does. In
`forward` mode a note goes to the agent unless the observer judged the agent already knows it:

- **Agent busy:** the note is steered into the run before its next model call.
- **Agent idle:** the note goes out with your next message.

Two dismissals in a row double the wait between looks; reading a note resets it. A note whose
quote is not in what the observer was shown is dropped. Each note records the prompt version that
produced it, so your `u`, `k`, `w` and `x` marks are labels for that version. A look whose reply
the HUD could not read moves no cursor, so the next look reads those turns again; a reply of
`{"note": null}` is a review that found nothing and does move it.

### A note's life, checked

The agent keeps working while the observer answers. On 2026-11-27 a note that a test file still
named a county arrived two seconds after the agent's own edit had removed the name. So before a
note is shown, the HUD sends the turns that came after the observer's read, with the note, in
one more call: does it still hold? A note those turns settled is recorded as `stale` and never
shown; an unreadable answer keeps the note, which already passed the quote check. If more turns
arrive during that call it reads again, up to 3 times, then shows the note as last read.

[`model/HudNote.tla`](model/HudNote.tla) is the lifecycle as a TLA+ model, checked with TLC and
drawn by pstack's `statechart` skill (0.9.147, 2026-11-27). Three rules: a note is never shown
after the agent already fixed it; a note reaches the agent at most once; a dropped note was
really settled. With the recheck off (`off.cfg`) TLC breaks the first rule in 3 steps (the
observer looks, the agent fixes it, the reply arrives), which is the county note. With it on
(`on.cfg`) all three hold over 20 states. The model leaves out `forward` mode, the 3-read cap
and more than one problem at a time. `index.test.ts` replays each path on the real code.

```mermaid
stateDiagram-v2
  direction LR
  state "Problem" as r0 {
    s0: Problem open
    s1: Agent fixed it
    [*] --> s0
    s0 --> s1: the agent fixes it
  }
  --
  state "Note" as r1 {
    s2: Watching
    s3: Observer reading
    s4: Note on the panel
    s5: Marked and closed
    s6: Note opened
    s7: Sent to the agent
    s8: Rereading later turns
    s9: Dropped, already fixed
    [*] --> s2
    s2 --> s3: the observer looks [when Problem open]
    s3 --> s4: the reply arrives [when Problem open]
    s3 --> s8: the agent moved on [read the new turns]
    s8 --> s4: it still holds [when Problem open]
    s8 --> s9: the new turns fixed it [when Agent fixed it]
    s4 --> s6: you open it
    s4 --> s7: you send it
    s4 --> s5: you mark it
    s6 --> s7: you send it
    s6 --> s5: you mark it
  }
```

To draw it again: `node <statechart skill>/scripts/statechart.ts model/HudNote.tla --config
model/on.cfg --view model/view.mjs --out <new dir>`, and `off.cfg` for the broken path.

## What the observer prompt measures

The prompt that ships is `observer-2026-11-28`. It is `observer-2026-11-27` with two more
fields in each note, `stakes` (who it reaches or what it costs, with the facts that bound it)
and `decision` (the call only you can make, or none). Both came from marks on two live notes on
2026-11-27, not from a replay; the numbers below are for `observer-2026-11-27`, and live marks
restart at the new version. On 2026-11-27 `observer-2026-11-27` was replayed on 199 checkpoints
from 32 recorded Claude Code sessions (private data, outside every repository) and each note was
judged in hindsight by the same model against the next 40 turns: is the note true, new to both
the person and the agent, and consequential, each with a quote from the record. Worth it means
all three hold. Result: 20 notes raised, 4 worth it, 0 not true. The earlier prompt
`observer-2026-11-25` raised 44 on the same checkpoints: 10 worth it, 13 not true. Fourteen of
the checkpoints are moments where Claude Code's own side agent had raised a note; the new prompt
raised one at 1 of the 14, the old at 2. That is detection coverage against another observer's
notes, not recall: the incumbent is a comparator, not ground truth, and no one has counted the
consequential errors in sessions where both stayed silent. Re-judging
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
**delivered** notes. Each note records its prompt version, and your marks are the labels: `u`
is "worth receiving", not merely correct; `w` is not true; `k` and `x` are not worth it. The
rates are computed over notes marked `u`, `k`, `w` or `x`; a note only opened (`read`) or never
touched is unclassified. Report the delivered, classified and unclassified counts beside the
rates, because the notes you bother to mark are not a random sample of the notes you receive.
That is the measurement, not another replay.

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

The overlay and the menu were not driven in a live terminal; `panel.test.ts` renders the panel
with a stand-in kit and `index.test.ts` answers the menu with scripted picks. The recheck prompt
was not measured on recorded sessions; one county note is its only evidence.
`bun test mechanisms` passed on Linux in a Debian container (`oven/bun:1`, bun 1.4.5, 2026-11-27): 350 pass, 0 fail; the consent test skips there because Pi's dist is not installed. Nothing ran on macOS.
