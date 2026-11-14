# binnacle-hud

Keep a Log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. The mod keeps each thought in session state. It does not send a thought to Claude or add it to the conversation. Whether a thought stays out of a later model request has not been verified.

Keep the decisions you and Claude agreed in Memory. The mod gives Memory to Claude only when you press Send and confirm it. From then on the lines are part of Claude's system instructions on every request, so a long chat or a compaction does not push them out of Claude's view.

The mod draws a side panel, the Binnacle HUD, next to the chat. The panel has two sections:

- **Memory** holds the lines you want Claude to keep. Send gives Claude those lines, after you confirm.
- **Log** keeps thoughts for you. Type a thought in its field and press Enter, or send `/log` from the phone. The mod keeps the thought with the time and where it came from.

## Give Claude your Memory lines

1. Type a line in the field. Press Tab to reach the actions, then press `a` to add the line to Memory.
   If you pressed Enter by habit, the line is in the Log. Press Tab, then `p`, to copy the newest Log thought into Memory. The Log keeps it.
2. To remove a line, press its number. With more than nine lines, `0` removes the last one.
3. Press `s` to send. Claude Code shows the lines and asks, for example, "Give Claude these 2 lines now?". Choose **Send**.

The mod adds the lines to Claude Code's own memory section of the system prompt, under the heading "Memory the operator approved at HH:MM:". Claude reads them from its next turn and on every request after that. The system prompt is not part of the chat that Claude Code compacts, so the lines stay through a compaction. Send adds no row to the conversation and starts no model turn.

A Send changes the system prompt, so Claude Code rewrites its prompt cache once. The next request writes the whole conversation to the cache again, which costs more and takes longer than a cached request. Claude also loses its earlier thinking blocks, and Claude Code shows a dim line naming the mod. Requests after that use the cache again.

The line under the Memory heading says where things stand:

| Status | Meaning |
| --- | --- |
| Not sent. | Claude has no Memory lines from this session. |
| In Claude's instructions since HH:MM. | Claude has exactly the lines shown, on every request. |
| Changed since Send. Claude has the HH:MM version. | You changed the lines after the last Send. Claude still has the older lines until you send again. |

Memory goes to the main conversation. A subagent that is already running keeps the instructions it started with.

If Claude Code refuses to save the Send, the HUD shows "Not sent." and the reason while the lines are the ones that Send carried. The reason goes away when you change the lines or when they match what Claude has. The previous Send stays in force. To change a line, remove it and add the new wording.

## Get back a prompt you wiped by accident

Claude Code brings a cleared draft back itself. After Ctrl+C, press Up on the empty prompt. It keeps the ten most recent cleared drafts of the session, from version 2.1.292. To set a draft aside on purpose, use its Ctrl+S stash. The HUD does not read or keep the prompt box.

## Install the mod

Marketplace installs require a pin to **v4.1.0 or later**; v4.0.0 does not contain this mod. A version bump alone does not make the mod installable: the marketplace must also be pinned to that release.

On Claude Code 2.1.275 or later, one command adds the marketplace and installs the mod. Run it at the prompt of a Claude Code terminal session:

```text
/plugin install binnacle-hud --marketplace MrBinnacle/skills
```

On an older Claude Code, run these two commands, each on its own. If you paste both at once, Claude Code reads them as one malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install binnacle-hud
```

If the marketplace is already added, update it first by running `claude plugin marketplace update mrbinnacle-skills` in a shell. To load the mod, run `/reload-plugins` or start a new session.

For development, load it from a clone instead:

```text
git clone https://github.com/MrBinnacle/skills.git
claude --plugin-dir skills/mods/binnacle-hud
```

`--plugin-dir` loads the mod for that session only. Pass it each time you start Claude Code.

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

If a keep fails, the HUD shows the submitted text beside the capture field, including in the collapsed strip. Failed attempts stay visible in session state even after later keeps, so you can recover them without replacing a newer draft. Once you have them, press Tab, then `d`, to dismiss the ones on screen. A failed `/log` also replies that the save failed, without repeating the thought.

If you type text after `/log`, the mod keeps nothing and asks you to use the dialog. Text after a command is part of the conversation.

## What the mod does with a kept thought

- Keeping a thought starts no model turn, and the mod adds nothing to the conversation or the unfinished Claude prompt.
- The command line and the mod's reply are part of the conversation, so neither one carries the thought.
- The Log lasts as long as the session. A new session starts with an empty Log.
- The mod gives Memory lines to Claude only when you press Send and choose **Send** in the dialog. Keeping a thought does not add it to Memory; `p` copies it there without sending it.
- The mod writes no file. Memory, like the Log, lasts as long as the session.

### Where a kept thought goes

- The mod keeps Log entries in Claude Code's session state. It writes no kept thought to a file or to a store of its own. This describes the mod's code, not Claude Code's own logging, syncing or retention.
- The mod's code makes no network call.
- Other plugins in the same session can read the Log. A plugin cannot write another plugin's state directly, but it can intercept a state write and change it. The Log is not isolated from other plugins. Install only plugins you trust.
- A thought sent from the phone travels over Remote Control, Anthropic's connection between the Claude app and your terminal session, before the mod keeps it. A thought typed in the terminal goes to session state with no network call by the mod. Claude Code and other plugins are outside what the mod can promise.

## What was tested

On Claude Code 2.1.319, on 2026-11-08 and 2026-11-09, in a terminal session and in the iPhone app over Remote Control:

- In the terminal, a click put the typing in the field. Enter kept the thought and cleared the field.
- From the phone, `/log` kept a thought and replied "Kept in the Log." The session stayed at 0 turns.
- A conversation export taken afterwards held `/log` and the reply, but not the thought.

On Claude Code 2.1.325, on 2026-11-13, in headless sessions with a test mod that used the same mechanism:

- A section answer that changed between turns, with the cache-break flag, reached the model on the next turn and stayed on the turn after.
- Without the flag, or without telling Claude Code that the answer changed, the model kept reading the old text.
- A section added through the system-prompt composition hook did not change mid-conversation, which is why the mod uses Claude Code's memory section instead.

The mod's tests cover the field, `/log`, the refusal of text after `/log`, the panel's key row, failed keeps surviving later captures, and edits during Log or Memory saves, including emptying and retyping the same text. Memory tests cover confirmation before Send, freezing the lines when Send is pressed, the memory section before and after Send, the engine's own memory text kept ahead of the lines, a refused save, and state written by earlier versions. Run them with `claude plugin test mods/binnacle-hud`.

These are not verified:

- Memory in a live interactive session. Its tests run against the test kit, and the probe ran headless.
- Memory after a real compaction, from `/compact` or an automatic one. That the lines survive follows from the system prompt not being compacted; it was not observed.
- Memory after resuming the session in a new Claude Code process.
- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation, and long text in the phone's dialog.
- What the dialog's **Chat about this** option does. Use **Other** instead.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
