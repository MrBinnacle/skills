# binnacle-hud

Keep a private Log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. Nothing in the Log is sent to Claude.

The mod draws a side panel, the Binnacle HUD, next to the chat. The panel has three sections:

- **Log** works. Type a thought in its field and press Enter, or send `/log` from the phone. The mod keeps the thought with the time and where it came from.
- **Memory** and **Watch** are a design preview. They show fixed sample data, and their buttons save or send nothing.

## Install the mod

The collection's current release, v4.0.0, does not contain this mod, so `/plugin install binnacle-hud` finds no mod yet. Until the next release, load it from a clone of the repository:

```text
git clone https://github.com/MrBinnacle/skills.git
claude --plugin-dir skills/mods/binnacle-hud
```

`--plugin-dir` loads the mod for that session only. Pass it each time you start Claude Code.

After the next release, install it from the marketplace. Run each command on its own at the prompt of a Claude Code terminal session. If you paste both at once, Claude Code reads them as one malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install binnacle-hud
```

To load the mod, run `/reload-plugins` or start a new session.

## Commands

| Command | What it does |
| --- | --- |
| `/hud` | Opens the HUD and puts the cursor in the Log's field. Esc returns to the prompt. |
| `/hud narrow hide` | When the window has no room for the side panel, shows one line that says how to get it. This is the default. |
| `/hud narrow strip` | When the window has no room for the side panel, shows the full HUD above the prompt. |
| `/log` | Asks for a thought in Claude Code's question dialog. |

The side panel needs fullscreen (`/tui fullscreen`) and a window at least 110 columns wide. A click on the panel also puts the cursor in the field.

## Log a thought from the phone

The Claude app does not draw the panel, but it does draw the question dialog. To keep a thought from the phone:

1. Open the session in the Claude app over Remote Control.
2. Send `/log` with nothing after it.
3. Type the thought under **Other** in the dialog, and send it.

The reply is "Kept in the Log." The reply never repeats the thought. In the HUD, the thought shows the word `phone`.

If you type text after `/log`, the mod keeps nothing and asks you to use the dialog. Text after a command is part of the conversation.

## How the mod keeps the Log private

- A kept thought starts no model turn, and the mod adds nothing to Claude's context.
- The command line and the mod's reply are part of the conversation, so neither one carries the thought.
- The Log lasts as long as the session. A new session starts with an empty Log.

### Where a kept thought goes

- Claude Code holds the Log in the mod's session state. The mod writes no file and keeps no store between sessions.
- The mod's code makes no network call.
- Other plugins in the same session can read the Log. Claude Code lets any plugin read another plugin's session state, though only the owner can change it. Install only plugins you trust.
- A thought sent from the phone travels over Remote Control, Anthropic's connection between the Claude app and your terminal session, before the mod keeps it. A thought typed in the terminal never leaves your machine through the mod.

## What was tested

On Claude Code 2.1.319, on 2026-11-08 and 2026-11-09, in a terminal session and in the iPhone app over Remote Control:

- In the terminal, a click put the typing in the field. Enter kept the thought and cleared the field.
- From the phone, `/log` kept a thought and replied "Kept in the Log." The session stayed at 0 turns.
- A conversation export taken afterwards held `/log` and the reply, but not the thought.

The mod's tests cover the field, `/log`, the refusal of text after `/log`, and the panel's key row. Run them with `claude plugin test mods/binnacle-hud`.

These are not verified:

- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation, and long text in the phone's dialog.
- What the dialog's **Chat about this** option does. Use **Other** instead.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
