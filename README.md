<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

This repository records mistakes that coding agents made in real engineering work. A coding agent is an AI model that edits code and runs commands for you. Each record is a card: a dated log of each time the mistake was seen (`gotchas.md`), a note of where the card came from and what has been measured about it (`EVIDENCE.md`), and a skill (`SKILL.md`), a file of instructions that an agent such as Claude Code can load.

The records are the main offer, and you can read them with no install. No skill here has been shown to make an agent less likely to repeat its mistake. Each card's `EVIDENCE.md` says what has and has not been measured.

The full guide is the site: **https://mrbinnacle.github.io/skills/**. It explains each card, how cards get in and out, and what installing costs you.

## Read

- [CATALOG.md](CATALOG.md) lists every card with its evidence.
- [skills/engineering](skills/engineering/README.md), [skills/orchestration](skills/orchestration/README.md) and [skills/meta](skills/meta/README.md) hold the cards, grouped by subject.
- [ADMISSION.md](ADMISSION.md) is the rule for what gets in. Its default answer is no.
- [RETIRED.md](RETIRED.md) lists every card that left, with its evidence.

## Install

The install is for Claude Code. Run these two commands one at a time, because Claude Code reads a paste of both as one malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

Install `mrbinnacle-orchestration` and `mrbinnacle-meta` the same way if you want them. Then run `/reload-plugins`. `claude plugin list` shows what you installed.

Some cards load in every session and some run only when you type `/` and their name. A card that loads in every session costs about 70 to 80 tokens of context, as `/context` counts them (Claude Code 2.1.305, measured 2026-10-20, [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476)). A card that runs by hand costs nothing until you call it.

<details>
<summary>Shell form and install receipts</summary>

```bash
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
claude plugin install mrbinnacle-engineering
```

Verified forms, from a clean Claude configuration directory with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git` (2026-10-02)
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git` (CI, 2026-10-17)
- shell `claude plugin install` of all three plugins, at 3.1.0 (CI run 39075732554, 2026-10-17)

The 2026-10-17 shell forms ran in the `Install form` CI job on Ubuntu and Windows.

</details>

## License

[LICENSE](LICENSE) is the MIT license that covers the collection.
