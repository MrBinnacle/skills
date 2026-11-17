# binnacle-hud

Keep a Log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. The mod keeps each thought in session state. It does not send a thought to Claude or add it to the conversation. Whether a thought stays out of a later model request has not been verified.

Keep the decisions you and Claude agreed in Memory. The mod gives Memory to Claude only when you press Send and confirm it. From then on the lines are part of Claude's system instructions on every request, so a long chat or a compaction does not push them out of Claude's view.

Keep every heads-up from Claude Code's You should know side agent. The side agent holds one note per session, so a newer note replaces one you have not acted on. The HUD lists each note until you hand it to Claude, dismiss it, or send it from the side agent's own band.

The mod draws a side panel, the Binnacle HUD, next to the chat. The panel has up to three sections:

- **Heads-ups** lists the side agent's notes that wait. It appears only while one waits.
- **Memory** holds the lines you want Claude to keep. Send gives Claude those lines, after you confirm.
- **Log** keeps thoughts for you. Type a thought in its field and press Enter, or send `/log` from the phone. The mod keeps the thought with the time and where it came from.

## Hand heads-ups to Claude

1. Each note from the side agent joins the Heads-ups list at the top of the panel, numbered in the order it arrived. In the strip above the prompt, the summary says how many wait.
2. Press Tab to reach the actions, then press `h`. The HUD puts every waiting note into the prompt box, after anything you have typed. Nothing is sent.
3. Read the prompt, edit it if you want, and send it yourself. The notes leave the list when the prompt you send holds them.

If you clear the prompt box instead of sending it, the notes stay in the list, and `h` puts them in again. Pressing `h` while the box already holds a note does not add it twice.

The notes go in as quoted data, each in its own `<heads-up>` block. The text before them tells Claude that the notes are information, not instructions, and to ask before anything that deletes, publishes, sends, installs or changes settings. The mod removes hidden characters from a note, and any text that could close a block early.

Press `x` to dismiss every waiting note. A note you send from the side agent's band leaves the list too. If the prompt box cannot take the notes, for example while a dialog is open, they stay in the list and a notice says why.

The list lasts as long as the Claude Code process, through `/clear` (see [What `/clear` and `/resume` keep](#what-clear-and-resume-keep)). It holds the newest 20 notes. The mod reads notes only from the side agent that comes with Claude Code: the plugin named `cc-plugin-you-should-know` in the built-in tier, and its own store file. Another plugin can still rewrite that side agent's state on its way through, and any program running as you can write the store file. That is why a note goes to Claude only as quoted data, and only when you send the prompt.

## Give Claude your Memory lines

1. Type a line in the field. Press Tab to reach the actions, then press `a` to add the line to Memory.
   If you pressed Enter by habit, the line is in the Log. Press Tab, then `p`, to copy the newest Log thought into Memory. The Log keeps it.
2. To remove a line, press its number. With more than nine lines, `0` removes the last one.
   Memory holds at most 20 lines. When it is full, the `a` and `p` keys are gone and the HUD says so. Remove a line to add another.
3. Press `s` to send. Claude Code shows the lines and asks, for example, "Give Claude these 2 lines now?". Choose **Send**.

The mod adds the lines to Claude Code's own memory section of the system prompt, under the heading "Memory the operator approved at HH:MM:". They go out with every request from Claude's next turn onward. The system prompt is not part of the chat that Claude Code compacts, so the lines stay through a compaction. Send adds no row to the conversation and starts no model turn.

A Send changes the system prompt, so Claude Code rewrites its prompt cache once. The next request writes the whole conversation to the cache again, which costs more and takes longer than a cached request. Claude also loses its earlier thinking blocks, and Claude Code shows a dim line naming the mod. Requests after that use the cache again. The Send question says so before you choose.

The mod removes hidden characters from a Memory line before it saves the line: control characters, zero-width and direction-changing characters, and the tag characters that can carry text you cannot see to a model. Pasted text could bring them in. The 2000-character limit counts only the characters that remain.

The line under the Memory heading says where things stand:

| Status | Meaning |
| --- | --- |
| Not sent. | Claude has no Memory lines from this session. |
| Sent at HH:MM. Not yet in Claude's instructions. | You sent the lines shown, and Claude Code has not yet built a system prompt that carries them. It does so at Claude's next turn. |
| Sent at HH:MM, but a turn ran without it in Claude's instructions. Press q to put the lines in the prompt instead. | A turn of the main conversation started after the Send and ended without Claude Code asking for the memory section, so the lines did not reach Claude. Press `q` to put them in the prompt box as a request to keep to them, then send the prompt yourself. A subagent's turn and a turn that started before the Send do not count. |
| In Claude's instructions since HH:MM. | Claude Code put exactly the lines shown into the system prompt at HH:MM, and keeps them on every request. |
| Changed since Send. The HH:MM version is not yet in Claude's instructions. | You changed the lines after the last Send, and that Send has not reached the system prompt yet either. |
| Changed since Send. Claude has the HH:MM version. | You changed the lines after the last Send. Claude still has the older lines until you send again. |

The mod says the lines are in Claude's instructions only after its hook has added them to the memory section. A Send alone does not make that claim.

Memory goes to the main conversation only. In one headless run on Claude Code 2.1.326, a general-purpose subagent started after a Send did not receive the memory section. A subagent that is already running keeps the instructions it started with. So the status "In Claude's instructions" is about the main conversation, and a subagent does not have the lines.

If Claude Code refuses to save the Send, the HUD shows "Not sent." and the reason while the lines are the ones that Send carried. The reason goes away when you change the lines or when they match the last Send. The previous Send stays in force. To change a line, remove it and add the new wording.

## What `/clear` and `/resume` keep

Claude Code empties a session's state at `/clear` and `/resume`, and starts no new session for the mod. The mod reads its lists as the old session ends and writes them back once the new one runs. Nothing goes to a file.

| What | After `/clear` | After `/resume` |
| --- | --- | --- |
| Log thoughts and failed keeps | kept | kept |
| Memory lines you have not sent, and the field's text | kept | kept |
| Heads-ups waiting, and the ones already handed or dismissed | kept | dropped, because they are about the conversation you left |
| The Memory you approved with Send | dropped | dropped |

The approved Memory is dropped on purpose. You approved it for one conversation, so a new conversation starts with "Not sent." and your unsent lines, ready to send again. Anything you write in the new session before the mod writes its lists back is kept beside them, and nothing is listed twice. A new Claude Code process starts with everything empty.

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

The mod's `tsconfig.json` extends `.claude-plugin/types/tsconfig.json`, which is not in git. To create it, load the mod with `claude --plugin-dir skills/mods/binnacle-hud` in an interactive session. Claude Code then writes the type declarations for the version you run ([Create a mod](https://code.claude.com/docs/en/plugins/mods/create.md), read 2026-11-17). Until then, `tsc -p` has nothing to extend.

`claude plugin validate --strict skills/mods/binnacle-hud` type-checks the mod without that folder. Run it with Claude Code 2.1.326 or later. An older one does not know the three-line setting and fails the check.

## Commands

| Command | What it does |
| --- | --- |
| `/hud` | Opens the HUD and puts the cursor in the Log's field. Esc returns to the prompt. |
| `/hud narrow hide` | When the window has no room for the side panel, shows one line that says how to get it. This is the default. |
| `/hud narrow strip` | When the window has no room for the side panel, shows the full HUD above the prompt. |
| `/log` | Asks for a thought in Claude Code's question dialog. |

The side panel needs fullscreen (`/tui fullscreen`) and a window at least 110 columns wide. A click on the panel also puts the cursor in the field.

If Claude Code refuses `/hud` or `/log`, for example because a later release or another plugin takes the name, the HUD still opens and a notice names the command it could not add.

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
- The Log lasts as long as the Claude Code process. It comes back after `/clear` and `/resume`, and a new process starts with an empty Log.
- The Log keeps the newest 100 thoughts. When a new thought arrives, the oldest one is dropped. The list of thoughts that failed to save also keeps its newest 100.
- The mod keeps the first 2000 characters of a thought or a Memory line and drops the rest. When the mod cuts a thought it kept, `/log` says so in its reply, and the HUD says so in a notice. A thought that failed to save is cut the same way, without a notice.
- In the side panel, a long thought or Memory line shows at most three lines, so the field stays in view. This needs Claude Code 2.1.326 or later. An older Claude Code shows the whole text, because it refuses the setting that stops a row at three lines.
- The mod gives Memory lines to Claude only when you press Send and choose **Send** in the dialog. Keeping a thought does not add it to Memory; `p` copies it there without sending it.
- The mod writes no file. Its lists live in Claude Code's session state, and the mod carries them across `/clear` in memory only.
- The mod reads one file: the side agent's own store file in Claude Code's `plugins/store` folder, at session start and after each turn of the main conversation. It keeps only the note for the current session.

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

The mod's tests cover the field, `/log`, the refusal of text after `/log`, the panel's key row, failed keeps surviving later captures, and edits during Log or Memory saves, including emptying and retyping the same text. Memory tests cover confirmation before Send, freezing the lines when Send is pressed, the memory section before and after Send, the engine's own memory text kept ahead of the lines, the status before and after the memory section carries a Send, a memory section that is never asked for, a refused save, and state written by earlier versions. Other tests cover a refused command name, a pane that fails to open, the limits on the Log, the failed list, Memory and the length of one thought, and the three-line rows on 2.1.326 and their absence on older versions. Heads-up tests cover the list at session start, a newer note that replaces an unacted one, `h` filling the prompt box once and in order after a draft, a fill the box refuses, `x`, a note sent from the band, a note from another session, the source check and the quoted block. Memory safety tests cover hidden characters in an added line and a copied Log thought, the cache cost in the Send question, and a Send that a turn ran without, including subagent turns and a turn begun before the Send. A mutation pass turned each changed condition of these features into a red test. Run them with `claude plugin test mods/binnacle-hud` on Claude Code 2.1.326 or later. On an older version, the test of the three-line rows fails, because that version refuses the setting.

These are not verified:

- Memory in a live interactive session. Its tests run against the test kit, and the probe ran headless.
- Memory after a real compaction, from `/compact` or an automatic one. That the lines survive follows from the system prompt not being compacted; it was not observed.
- Memory after resuming the session in a new Claude Code process.
- The carry in a live interactive session. Headless probes on 2.1.326 showed that state can be read as a session ends at `/clear` and written once the new one runs, twice each. An interactive `/clear` and `/resume` were not tried, and whether `/resume` empties state first was not probed; the mod doubles nothing if it does not.
- That the model read the lines. The status rests on the mod's hook adding them to the memory section, which is not proof that the model read them.
- That no other plugin changes the memory section after this mod's hook. A plugin whose hook runs outside this one can replace the section, and the status would still say the lines are in Claude's instructions.
- Which conversation the hook ran for. Claude Code does not say whether a section was built for the main conversation or a subagent, so a subagent started after a Send could turn the status before the main conversation picks the lines up.
- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation, and long text in the phone's dialog.
- Heads-up capture in a live session. The tests read a store file in the shape the side agent wrote on 2026-10-23 and 2026-11-17. A later Claude Code can change that shape; the mod finds a note by its shape, not by its key name, and lists nothing it cannot read.
- That `q` and `h` fill the prompt box on the phone. The Claude app draws no panel, so neither key is reachable there.

Choosing **Chat about this** in the `/log` dialog keeps nothing, and the reply is "Nothing kept." Claude Code's documentation says the dialog call fails on that choice, as it does when the dialog is dismissed ([events](https://code.claude.com/docs/en/plugins/mods/events.md), read 2026-11-17). The mod treats both failures the same way, and a test covers the dismissed dialog. The choice itself was not tried on a phone.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
