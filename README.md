<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills" src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

Skills that started with problems I encountered.

The agent says "Done." It never ran the tests.<br>
The check passed. It could not have failed.<br>
The deploy went out. The page still serves the old build.

Each of these happened in real work with a coding agent. This repository is what got built in response.

- **Guards** are code that runs on the agent's action, so nothing depends on the agent remembering an instruction.
- **Cards** are instructions an agent loads for one specific mistake.
- **Mods** add to Claude Code's own interface.

## See a guard fire

With Pi installed, run this from the repository root. It needs no API key and takes a few seconds.

```sh
node mechanisms/verify-gate/demo.mjs
```

An agent is asked for a 10% discount and writes a bug. In the first run it says "Done." and the bug ships. In the second run the guard sends it back to run the tests, and it reports the failure. The agent's replies are scripted, so you see what the guard does and not what a model makes of it.

## Install

### Claude Code

Run these one at a time. Claude Code reads a paste of both as one malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

Install `mrbinnacle-orchestration`, `mrbinnacle-meta`, `binnacle-hud` and `tips-anywhere` the same way if you want them. They appear after `/reload-plugins`.

`claude plugin details mrbinnacle-engineering` shows what a plugin adds to each session. `claude plugin uninstall mrbinnacle-engineering` removes it.

### Pi

```bash
pi install git:github.com/MrBinnacle/skills@v4.1.1
```

This installs the cards and the four guards. `pi list` confirms the install, and `pi remove` with the same source undoes it.

## What is here

| | What it does | Runs in |
|---|---|---|
| [`verify-gate`](mechanisms/verify-gate/) | Sends a run that edited files back to run a check before it finishes. | Pi |
| [`eol-guard`](mechanisms/eol-guard/) | Tells the agent when it has converted a file's line endings. | Pi |
| [`reviewer`](mechanisms/reviewer/) | Reviews a diff in a fresh read-only session. | Pi |
| [`session-packet`](mechanisms/session-packet/) | Hands a session's state to the next one. | Pi |
| [`binnacle-hud`](mods/binnacle-hud/README.md) | A side panel for your own notes, and for the lines you want Claude to keep. | Claude Code |
| [`tips-anywhere`](mods/tips-anywhere/README.md) | Brings Claude Code's "You should know" notes to the phone app. | Claude Code |
| [Cards](CATALOG.md) | A card for each mistake, grouped by subject. | Claude Code, Pi |

[mechanisms/](mechanisms/README.md) says what each guard fires on. Each mod's README says what it keeps and what it sends.

## Contribute

If your agent keeps making a mistake that nothing here covers, [open an issue](https://github.com/MrBinnacle/skills/issues/new) and say what happened. Fixes and new guards are welcome as pull requests. Report a security problem through [the private form](https://github.com/MrBinnacle/skills/security/advisories/new), not a public issue.

## How it is kept

[ADMISSION.md](ADMISSION.md) is the rule for which cards get in, and [RETIRED.md](RETIRED.md) lists the ones that left. The [runtime delivery matrix](docs/product/runtime-delivery-matrix.md) records which installs were checked, on what, and when. The [changelog](CHANGELOG.md) says what each version changed.

## License

[MIT](LICENSE).
