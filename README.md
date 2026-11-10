<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

Skills that started with problems I encountered.

Skills cost something every turn. How much, and to what degree, have you ever questioned the ROI?

This repository records mistakes that coding agents made in real engineering work. A coding agent is an AI model that edits code and runs commands for you. Each record is a card: a dated log of each time the mistake was seen (`gotchas.md`), a note of where the card came from and what has been measured about it (`EVIDENCE.md`), and a skill (`SKILL.md`), a file of instructions that an agent such as Claude Code can load.

The records are the main offer, and you can read them with no install. No skill here has been shown to make an agent less likely to repeat its mistake. Each card's `EVIDENCE.md` says what has and has not been measured.

Controlled tests, with and without a card, run in a separate repository, [skill-harness](https://github.com/MrBinnacle/skill-harness). Only `pull-rebase` has them. Its verdict is `CANT_TELL_YET`, the test's word for a result too weak to decide on; the latest read is dated 2026-10-02. No skill claims a measured benefit yet.

The site, **https://mrbinnacle.github.io/skills/**, is a one-page summary: the install, the rules for how cards get in and out, and what a version promises. The detail for each card is in [CATALOG.md](CATALOG.md) and in the card's own files.

## What a card costs

Some cards load in every session and some run only when you type `/` and their name. A card that loads in every session costs about 70 to 80 tokens of context, as `/context`, Claude Code's own context counter, counts them (Claude Code 2.1.305, measured 2026-10-20, [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476)). When Claude Code lists a card by name only, which it decides from the space it has for the list, the card costs under 20 tokens. A card that runs by hand costs nothing until you call it.

## Read

- [mechanisms/](mechanisms/README.md) holds Pi extensions: code that runs on a tool result, a command or the end of a run, so it does not wait for the agent to remember a card. Its table says what each one backs, including rules no admitted card states, and [one command](mechanisms/README.md#see-it-fire) runs the verification guard against a scripted agent.
- [CATALOG.md](CATALOG.md) lists every card with its evidence.
- [skills/engineering](skills/engineering/README.md), [skills/orchestration](skills/orchestration/README.md) and [skills/meta](skills/meta/README.md) hold the cards, grouped by subject.
- [ADMISSION.md](ADMISSION.md) is the rule for what gets in. Its default answer is no.
- [RETIRED.md](RETIRED.md) lists every card that left, with its evidence.

## Install

There are two installs: Claude Code here, and [Pi](#pi) below. For Claude Code, run these two commands one at a time, because Claude Code reads a paste of both as one malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

Install `mrbinnacle-orchestration` and `mrbinnacle-meta` the same way if you want them.

The cards appear after `/reload-plugins`. If Claude Code reports the reload as pending, run `/reload-plugins --force`. Confirm what you installed with `claude plugin list`. It reports the installed plugins and their versions.

<details>
<summary>Shell form and install receipts</summary>

```bash
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
claude plugin install mrbinnacle-engineering
```

The plugin docs at https://code.claude.com/docs/en/discover-plugins.md state the reload behaviour above (read 2026-10-06).

On Windows, keep the path of your Claude configuration directory (`CLAUDE_CONFIG_DIR`) at 108 characters or fewer. If it is longer, run `git config --global core.longpaths true` before you add the marketplace; that raises the limit to 157 characters. Above 157, the install fails even with that setting. Measured with Claude Code 2.1.302 on 2026-10-17, with Windows long-path support turned on.

The HTTPS clone URL is the form this README publishes. The GitHub shorthand `MrBinnacle/skills` can fail on a machine with no working SSH key for github.com. Issue #333 recorded that failure.

Verified forms, Claude Code 2.1.287, from a clean `CLAUDE_CONFIG_DIR` with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git` (2026-10-02)
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git` (CI, 2026-10-17)
- shell `claude plugin install` of all three plugins, at 3.1.0 (CI run 39075732554, 2026-10-17)

The 2026-10-02 cold-install transcript is in the pull request that changed this section (#340). The 2026-10-17 shell forms ran in the `Install form` CI job on Ubuntu and Windows.

</details>

### Pi

```bash
pi install git:github.com/MrBinnacle/skills@v4.1.1
```

This installs the same cards and the four Pi extensions in [mechanisms/](mechanisms/README.md): a guard that sends a run which edited files back to run a check before it finishes, a line-ending guard, a reviewer, and a session handoff. Pi reads the `pi` key of `package.json` to find them. Confirm the install with `pi list`.

Checked with Pi 1.5.0 on Windows on 2026-11-08, from an empty Pi configuration directory with skills in `~/.agents/skills` excluded. Pi's own resource loader found every card and all four extensions, with no errors. That shows what Pi loads. It does not show how a model uses them, and it has not been run on Linux or macOS. To install the cards without the extensions, list the package in Pi's `settings.json` as `{"source": "git:github.com/MrBinnacle/skills@v4.1.1", "extensions": []}`.

## License

[LICENSE](LICENSE) is the MIT license that covers the collection.
