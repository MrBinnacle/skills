# tips-anywhere

See Claude Code's "You should know" heads-ups on your iPhone or iPad, and act on them with one tap.

Claude Code runs a side agent that sometimes spots something worth knowing and shows it above the prompt on your computer. The Claude app on a phone or tablet does not draw that band, so when you work from the phone you never see the note. This mod asks you about each heads-up in the chat instead, using Claude Code's own question prompt. The phone draws it with buttons:

- **Hand to Claude** sends the note to Claude to check and act on.
- **Show details** shows the side agent's longer explanation first.
- **Dismiss** clears it for the rest of the session.

## Install

Run these two commands one at a time at the prompt of a Claude Code terminal session. Claude Code reads a paste of both in one block as a single malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install tips-anywhere
```

The mod loads after `/reload-plugins`, or in a new session.

## Use

The mod works by itself once installed. To see it before a real heads-up arrives, type `/tips demo` and keep the chat open for about eight seconds. A sample question appears.

| Command | What it does |
| --- | --- |
| `/tips` | Shows the waiting heads-up and asks about it again. |
| `/tips do` | Hands the heads-up to Claude. |
| `/tips why` | Shows the longer explanation. |
| `/tips skip` | Dismisses the heads-up. |
| `/tips via buttons` | Asks in the chat with buttons, on every app. This is the default. |
| `/tips via computer` | Shows a pop-up on the computer only and asks nothing. |
| `/tips demo` | Sends a sample heads-up after eight seconds. |

The same setting is in `/config` as "How heads-ups reach you".

## How it keeps you in control

A heads-up can quote text from files or web pages, so the mod treats it as data, never as your instructions.

- Claude receives the note inside a marked block, with an instruction to check it first and to ask you before anything that deletes, publishes, sends, installs or changes settings. The note cannot close that block early.
- The note goes to Claude only after you tap Hand to Claude or type `/tips do`. Claude receives the longer explanation only if you opened it.
- Only you can act on a heads-up or change the setting. A `/tips` command run by another plugin, another session or a script shows the note and does nothing else.
- The mod strips control characters, terminal escape sequences, and invisible characters that could hide text from you while Claude still reads it.
- The mod accepts a heads-up only from the side agent built into Claude Code, and on disk only from that agent's own store file.

Two limits remain. Another plugin you install could alter the side agent's note before this mod sees it. Any program running under your account could write a fake store file. In both cases the controls above still apply: the note is quoted data, and nothing happens until you choose it.

## Status

Tested on Claude Code 2.1.309 with the iPhone app on 2026-10-23: the sample heads-up appeared on the phone with tappable buttons, and Hand to Claude reached the session. The mod's test suite covers the commands, the hand-over and the controls above. A heads-up from the real side agent has not yet been seen passing through the mod. The side agent is a built-in feature whose internals are not documented, so a later Claude Code release may change how the mod picks it up.

## License

MIT, under the collection's [LICENSE](../../LICENSE).
