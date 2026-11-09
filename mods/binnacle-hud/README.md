# binnacle-hud

Keep a private log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. Nothing in the log is sent to Claude.

The mod draws a side panel, the Binnacle HUD, next to the chat. It has three sections:

- **Log** is real. Type a thought in its field and press Enter, or send `/log` from the phone, and the thought is kept with the time and where it came from.
- **Memory** and **Watch** are a design preview. They show fixed sample data, and their buttons save or send nothing.

## Install

Run these two commands one at a time at the prompt of a Claude Code terminal session. Claude Code reads a paste of both in one block as a single malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install binnacle-hud
```

The mod loads after `/reload-plugins`, or in a new session.

## Use

| Command | What it does |
| --- | --- |
| `/hud` | Opens the HUD and puts the cursor in the Log's field. Esc returns to the prompt. |
| `/hud narrow hide` | Without room for the side panel, shows one line that says how to get it. This is the default. |
| `/hud narrow strip` | Without room for the side panel, shows the full HUD above the prompt. |
| `/log` | Asks for a thought in Claude Code's question dialog. Type it under the dialog's free-text option. |

The side panel needs fullscreen (`/tui fullscreen`) and a window at least 110 columns wide. A click on the panel also puts the cursor in the field.

On the phone, the Claude app does not draw the panel, but it does draw the question dialog, so `/log` is the way to log from there. Type `/log` alone. Text typed after `/log` is part of the conversation, so the mod keeps nothing and asks you to use the dialog instead. The reply is "Kept in the Log." and never repeats the thought. A thought sent from the phone shows the word `phone` in the HUD.

## How it keeps the log private

- A kept thought starts no model turn, and the mod adds nothing to Claude's context.
- The command line and the mod's reply are part of the conversation, so neither one carries the thought.
- The log lasts for the session. A restart starts it empty.

## Status

Tested on Claude Code 2.1.319 on 2026-11-08 and 2026-11-09, in a terminal session and with the iPhone app over Remote Control. In the terminal, a click put the typing in the field, and Enter kept the thought and cleared the field. From the phone, `/log` kept a thought, the reply was "Kept in the Log.", and the session stayed at 0 turns. A conversation export afterwards held `/log` and the reply but not the thought. The mod's test suite covers the field, `/log`, the refusal of text after it, and the panel's key row.

Not verified:

- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation and long text in the phone's dialog.
- What the dialog's "Chat about this" option does. Choose the free-text option instead.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
