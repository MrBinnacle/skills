# binnacle-hud

Keep a private Log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. Nothing in the Log is sent to Claude.

Keep the decisions you and Claude agreed in Memory. Memory reaches Claude only when you press Send and confirm it.

The mod draws a side panel, the Binnacle HUD, next to the chat. The panel has three sections:

- **Log** works. Type a thought in its field and press Enter, or send `/log` from the phone. The mod keeps the thought with the time and where it came from.
- **Memory** holds the lines you want Claude to keep. Send gives Claude those lines at once, after you confirm.
- **Watch** is a preview. It shows one sample finding and is not connected to an observer yet.

## Give Claude your Memory lines

1. Type a line in the field. Press Tab to reach the actions, then press `a` to add the line to Memory.
   If you pressed Enter by habit, the line is in the Log. Press Tab, then `p`, to copy the newest Log thought into Memory. The Log keeps it.
2. To remove a line, press its number. With more than nine lines, `0` removes the last one.
3. Press `s` to send. Claude Code shows the lines and asks, for example, "Give Claude these 2 lines now?". Choose **Send**.

The mod adds one row to the conversation that reads "Memory the operator approved at HH:MM:", followed by the lines. The row starts no model turn. Claude reads it on its next turn.

The line under the Memory heading says where things stand:

| Status | Meaning |
| --- | --- |
| Not sent. | Claude has no Memory lines from this session. |
| In Claude's context since HH:MM. | Claude has exactly the lines shown. |
| Changed since Send. Claude has the HH:MM version. | You changed the lines after the last Send. Claude still has the older lines. |

If Claude Code refuses the row, the HUD shows "Not sent." and the reason, and the previous Send stays in force. To change a line, remove it and add the new wording.

## Install the mod

Run each command on its own at the prompt of a Claude Code terminal session. If you paste both at once, Claude Code reads them as one malformed URL.

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
- Memory is the one section that reaches Claude. Its lines reach Claude only when you press Send and choose **Send** in the dialog. A kept thought never goes into Memory.
- The mod writes no file. Memory, like the Log, lasts as long as the session.

## What was tested

On Claude Code 2.1.319, on 2026-11-08 and 2026-11-09, in a terminal session and in the iPhone app over Remote Control:

- In the terminal, a click put the typing in the field. Enter kept the thought and cleared the field.
- From the phone, `/log` kept a thought and replied "Kept in the Log." The session stayed at 0 turns.
- A conversation export taken afterwards held `/log` and the reply, but not the thought.

The mod's tests cover the field, `/log`, the refusal of text after `/log`, the panel's key row, and Memory: Send only after a confirmation, the lines sent exactly as shown when Send was pressed, an edit after Send that leaves the sent lines unchanged, a refused row, and a kept thought that never reaches Memory. Run them with `claude plugin test mods/binnacle-hud`.

These are not verified:

- Memory in a live session. Its tests run against the test kit, not a terminal or the phone.

- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation, and long text in the phone's dialog.
- What the dialog's **Chat about this** option does. Use **Other** instead.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
