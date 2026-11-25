# binnacle-hud

Keep a Log of thoughts beside a Claude Code session, from the terminal or from the Claude app on your phone. The mod keeps each thought in session state. It does not send a thought to Claude or add it to the conversation. Whether a thought stays out of a later model request has not been verified.

Keep the decisions you and Claude agreed in Memory. The mod gives Memory to Claude only when you press Send and confirm it. From then on the lines are part of Claude's system instructions on every request, so a long chat or a compaction does not push them out of Claude's view.

The mod also takes the heads-ups that Claude Code's built-in side agent offers above the prompt. It lists each one in the panel and gives it to Claude itself, so no heads-up waits on a key press.

The mod draws a side panel, the Binnacle HUD, next to the chat. The panel has three sections:

- **Memory** holds the lines you want Claude to keep. Send gives Claude those lines, after you confirm.
- **Heads-ups** lists the notes the side agent offered in this session, one line each. Press `h` to open them. In the side panel, the details of each note stop at three lines.
- **Log** keeps thoughts for you. Type a thought in its field and press Enter, or send `/log` from the phone. The mod keeps the thought with the time and where it came from.

## Give Claude your Memory lines

1. Type a line in the field. Press Tab to reach the actions, then press `a` to add the line to Memory.
   If you pressed Enter by habit, the line is in the Log. Press Tab, then `p`, to copy the newest Log thought into Memory. The Log keeps it.
2. To remove a line, press its number. With more than nine lines, `0` removes the last one.
   Memory holds at most 20 lines. When it is full, the `a` and `p` keys are gone and the HUD says so. Remove a line to add another.
3. Press `s` to send. Claude Code shows the lines and asks, for example, "Give Claude these 2 lines now?". Choose **Send**.

The mod adds the lines to Claude Code's own memory section of the system prompt, under the heading "Memory the operator approved at HH:MM:". They go out with every request from Claude's next turn onward. The system prompt is not part of the chat that Claude Code compacts, so the lines stay through a compaction. Send adds no row to the conversation and starts no model turn.

A Send changes the system prompt, so Claude Code rewrites its prompt cache once. The next request writes the whole conversation to the cache again, which costs more and takes longer than a cached request. Claude also loses its earlier thinking blocks, and Claude Code shows a dim line naming the mod. Requests after that use the cache again.

The line under the Memory heading says where things stand:

| Status | Meaning |
| --- | --- |
| Not sent. | Claude has no Memory lines from this session. |
| Sent at HH:MM. Not yet in Claude's instructions. | You sent the lines shown, and Claude Code has not yet built a system prompt that carries them. It does so at Claude's next turn. If this stays after a turn, the lines are not reaching Claude. |
| In Claude's instructions since HH:MM. | Claude Code put exactly the lines shown into the system prompt at HH:MM, and keeps them on every request. |
| Changed since Send. The HH:MM version is not yet in Claude's instructions. | You changed the lines after the last Send, and that Send has not reached the system prompt yet either. |
| Changed since Send. Claude has the HH:MM version. | You changed the lines after the last Send. Claude still has the older lines until you send again. |

The mod says the lines are in Claude's instructions only after its hook has added them to the memory section. A Send alone does not make that claim.

Memory goes to the main conversation. A subagent that is already running keeps the instructions it started with. Whether a subagent started after a Send also receives the lines is not verified.

If Claude Code refuses to save the Send, the HUD shows "Not sent." and the reason while the lines are the ones that Send carried. The reason goes away when you change the lines or when they match the last Send. The previous Send stays in force. To change a line, remove it and add the new wording.

## Heads-ups reach Claude with no key press

Claude Code's built-in side agent (`cc-plugin-you-should-know`) watches the session and sometimes offers a note, the "Heads up" row above the prompt with Learn more, Knew this already and Dismiss. With this mod installed:

1. The mod takes the note from the side agent's own store write, under the turn id the side agent wrote it with. A reload or a redraw does not take a note twice.
2. The row leaves the band above the prompt once its headline is exactly the line of a note listed in the panel. Any other row stays, so a note the mod missed, or a headline the side agent shortened, is still on screen.
3. The first note since your last message goes to Claude as a turn of its own. Claude Code labels that turn as sent by the mod.
4. A note that comes before you send another message waits, and goes with your next message as context Claude reads beside it. A slash command carries no note. One note-started turn for each message you send means a note's turn cannot set off a chain of turns.
5. If Claude Code refuses or fails the note's turn, the note waits for your next message instead. If another mod or Claude Code drops your message, its notes stay waiting for the one after.

The panel lists every note of the session, numbered, with its line. Press `h` to open them: each shows its details, the time it came and how it reached Claude ("sent to Claude", "goes with your next message" or "sent with your message"). The list lasts as long as the session.

**Claude acts on a note it finds to hold, without asking you.** A note can repeat text that reached the session from files, tool output or web pages, so text written by someone else can reach Claude this way, and you do not read it first. The mod removes hidden characters, normalises the text, and gives Claude each note as one line of JSON, with a sentence that says the data may repeat outside text and that an instruction inside it is not one to follow. How far that lowers the chance that Claude follows a planted instruction has not been measured. If you would rather read each note before Claude does, do not install this version.

Do not set `CLAUDE_CODE_YOU_SHOULD_KNOW_AUTO_SEND` with this mod. That setting makes the side agent attach its current note to your next prompt itself, so the note would reach Claude twice. With the `tips-anywhere` mod also installed, the phone's question for a note still appears; answering it with **Hand to Claude** sends that note a second time.

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
- The Log lasts as long as the session. A new session starts with an empty Log.
- The Log keeps the newest 100 thoughts. When a new thought arrives, the oldest one is dropped. The list of thoughts that failed to save also keeps its newest 100.
- The mod keeps the first 2000 characters of a thought or a Memory line and drops the rest. When the mod cuts a thought it kept, `/log` says so in its reply, and the HUD says so in a notice. A thought that failed to save is cut the same way, without a notice.
- In the side panel, a long thought, a Memory line, or the details of an opened heads-up shows at most three lines, so the field stays in view. The strip shows an opened heads-up whole, because it hides the field while the heads-ups are open. This needs Claude Code 2.1.326 or later. An older Claude Code shows the whole text, because it refuses the setting that stops a row at three lines.
- The mod gives Memory lines to Claude only when you press Send and choose **Send** in the dialog. Keeping a thought does not add it to Memory; `p` copies it there without sending it.
- The mod writes no file. Memory, like the Log, lasts as long as the session.
- A heads-up is different: the mod gives each one to Claude with no key press (see above). Its text came from the side agent, not from you.

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

The mod's tests cover the field, `/log`, the refusal of text after `/log`, the panel's key row, failed keeps surviving later captures, and edits during Log or Memory saves, including emptying and retyping the same text. Memory tests cover confirmation before Send, freezing the lines when Send is pressed, the memory section before and after Send, the engine's own memory text kept ahead of the lines, the status before and after the memory section carries a Send, a memory section that is never asked for, a refused save, and state written by earlier versions. Other tests cover a refused command name, saved state that cannot be read at start, a pane that fails to open, the limits on the Log, the failed list, Memory and the length of one thought, and the three-line rows on 2.1.326 and their absence on older versions. Run them with `claude plugin test mods/binnacle-hud` on Claude Code 2.1.326 or later. On an older version, the test of the three-line rows fails, because that version refuses the setting.

On 2026-11-23 the heads-up path was checked against the Claude Code 2.1.331 binary, which writes each offer as one store write of the turn id and the note, and with the mod's tests. A dev mod built for the design, which read the row instead of the store, hid the row and sent the note as a turn of its own in a live 2.1.331 session. This mod's store route has not yet run live.

These are not verified:

- The heads-up path in a live session: the store route, the row leaving the band, and a note riding with a message.
- How often Claude follows an instruction planted in a heads-up.
- Whether the side agent offers fewer notes over time. It counts each message sent while its note is open and unanswered, and after a run of them it holds back later notes. With the row hidden, no note is ever answered, so every open note counts. A mod cannot answer for you, because it cannot write another plugin's store.
- Whether the row's headline is always the note's line word for word. If it is not, the row stays above the prompt, and the note is still listed and sent.

- Memory in a live interactive session. Its tests run against the test kit, and the probe ran headless.
- Memory after a real compaction, from `/compact` or an automatic one. That the lines survive follows from the system prompt not being compacted; it was not observed.
- Memory after resuming the session in a new Claude Code process.
- That the model read the lines. The status rests on the mod's hook adding them to the memory section, which is not proof that the model read them.
- That no other plugin changes the memory section after this mod's hook. A plugin whose hook runs outside this one can replace the section, and the status would still say the lines are in Claude's instructions.
- Which conversation the hook ran for. Claude Code does not say whether a section was built for the main conversation or a subagent, so a subagent started after a Send could turn the status before the main conversation picks the lines up.
- That the thought is absent from what Claude reads on a later turn. The export suggests so, but no turn was sent to check it.
- Pasting, dictation, and long text in the phone's dialog.

Choosing **Chat about this** in the `/log` dialog keeps nothing, and the reply is "Nothing kept." Claude Code's documentation says the dialog call fails on that choice, as it does when the dialog is dismissed ([events](https://code.claude.com/docs/en/plugins/mods/events.md), read 2026-11-17). The mod treats both failures the same way, and a test covers the dismissed dialog. The choice itself was not tried on a phone.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
