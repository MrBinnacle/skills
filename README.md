<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

Skills that started with problems I encountered.

Skills is a knowledge base and a set of skill cards for engineering work with frontier models. A card is one skill: a `SKILL.md` file that a coding agent loads as instructions, kept with its evidence record and its record of observed failures. Most of the cards here are for mistakes that report success. The collection is built for the owner's own work first, and for other developers who work with a coding agent.

Here is the mistake behind `pull-rebase`. An agent ran `git pull origin main --no-commit --no-ff` on a machine with `pull.rebase=true` set. Git ignored `--no-ff` and rebased with no warning. It rewrote 22 local commits, and 111 references to the old commit IDs had to be corrected across 5 state files. The card tells the agent to check `git config --get pull.rebase` before it pulls, to fetch and merge instead when the setting is on, and to recover through the reflog when a pull has already rebased.

Most cards started from a failure like that one. Two, `im-down` and `im-up`, were designed on purpose. No skill claims a measured benefit yet. Most published cards do not yet meet all four questions of the [admission policy](ADMISSION.md) on recorded evidence ([the 2026-08-15 triage](dispositions/2026-08-15-S295-admission-triage.md) checked the cards published then). Each card's `EVIDENCE.md` says where it stands.

## Find the card for your situation

The cards install as three Claude Code plugins, one per group. A card marked "by hand" runs only when you call it by name.

**mrbinnacle-engineering**

| Card | Use it when |
|---|---|
| `pull-rebase` | You pull with `pull.rebase` on, and something else records your commit IDs. |
| `stale-deploy` | You confirm a deploy by polling a page that may already show the new text. |
| `mocked-stub` | A test mocks a helper that is only a stub in production. |
| `vacuous-check` | A success check only asks whether the output is non-empty. |
| `clirunner-env` | A test overrides environment variables to stop a real call. |
| `pretooluse-prose` | A command guard might block prose that mentions the command. |
| `halt-as-deliverable` | Your own gate stops the work, and the stop is the result. |
| `closure-mode` (by hand) | You reach a boundary with a checklist to run. |
| `im-down`, `im-up` (by hand) | You end a session and start the next one from written state. |

**mrbinnacle-orchestration**

| Card | Use it when |
|---|---|
| `subagent-handback` | You send work to a subagent and need to check what comes back. |
| `decision-rights` | You write a handoff, plan or prompt that someone else will act on. |
| `disposition-schema` | You run parallel reviews that must be compared. |

**mrbinnacle-meta**

| Card | Use it when |
|---|---|
| `dead-predicate` | A hook or router stays silent and you need to know why. |

## Install

[Pi](https://pi.dev), a coding agent, is the runtime this work targets first. There is no tested Pi install yet. The install below is for Claude Code, the install route that has a receipt today.

Run these two commands one at a time. Claude Code reads a paste of both in one block as a single malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

Install `mrbinnacle-orchestration` and `mrbinnacle-meta` the same way if you want them.

The cards appear after `/reload-plugins`. If Claude Code reports the reload as pending, run `/reload-plugins --force`. A new `claude` session in the same profile also loads them. Confirm what you installed with `claude plugin list`. It reports the installed plugins and their versions.

Each card not marked "by hand" adds one line to every session: about 70 to 80 tokens, as `/context` counts it (Claude Code 2.1.305, measured 2026-10-20, [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476)). That holds when the host lists the card with its description. A host that lists it by name only charges under 20. The rest loads only when it is used. The cards marked "by hand" cost nothing until you run them.

On Windows, a long path for your Claude configuration directory can make the install fail. The limits are in the block below.

<details>
<summary>Shell commands, Windows path limits, and the install receipts</summary>

Shell form, same source:

```bash
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
claude plugin install mrbinnacle-engineering
```

The plugin docs at https://code.claude.com/docs/en/discover-plugins.md state the reload behaviour above (read 2026-10-06).

On Windows, keep the path of your Claude configuration directory (`CLAUDE_CONFIG_DIR`) at 108 characters or fewer. If it is longer, run `git config --global core.longpaths true` before you add the marketplace; that raises the limit to 157 characters. Above 157, the install fails even with that setting. Measured for this release with Claude Code 2.1.302 on 2026-10-17, with Windows long-path support turned on. Not tested with that support off. Windows long-path support is an opt-in setting.

The HTTPS clone URL is what this README publishes. The GitHub shorthand `MrBinnacle/skills` is also a documented CLI source; on a machine with no working SSH key for github.com it can fail with `git@github.com: Permission denied (publickey)`, which is what a cold install of v3.0.1 recorded. Issue #333 recorded that failure.

Verified forms, Claude Code 2.1.287, from a clean `CLAUDE_CONFIG_DIR` with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git` (2026-10-02)
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git` (CI, 2026-10-17)
- shell `claude plugin install` of all three plugins, at 3.1.0 (CI run 39075732554, 2026-10-17)

The 2026-10-02 cold-install transcript is in the pull request that changed this section (#340). The 2026-10-17 shell forms ran in the `Install form` CI job on Ubuntu and Windows.

</details>

## What comes with each card

Most cards add a line to every session whether or not they fire, and whether they help is still open. So each one comes with:

- **Test cases** (`evals/evals.json`) you can run on your own model. A pass with the card attached does not show that the card caused it.
- **An evidence record** (`EVIDENCE.md`): where the card came from, and what has and has not been measured.
- **A retirement condition**: the change that would send it back to a screen or retire it, named in advance.

Controlled tests, with and without a card, run in a separate repository, [skill-harness](https://github.com/MrBinnacle/skill-harness). So far only `pull-rebase` has them, and its verdict is `CANT_TELL_YET`. In the first full-size run, on 2026-09-03, the agent never ran into the trap, with the card or without it, so the run could not tell whether the card helps. The latest read, a readout dated 2026-10-02, compared the card, a placebo card and no card, and stopped at its cap of 97 looks, one per paired run, with neither a pass nor a cut. The [evidence record](skills/engineering/pull-rebase/EVIDENCE.md) has every run. No skill claims a measured benefit yet.

## How cards get in and out

A new card is admitted only if it passes all four questions of the [admission policy](ADMISSION.md). The default answer is no. The policy came after many of the current cards were published. Candidates wait in the open in [`_quarantine/`](_quarantine/README.md).

A card leaves on recorded evidence: a screen result, the platform change its retirement condition names, or its own record failing an admission question outright, such as zero observed occurrences over its whole life. [RETIRED.md](RETIRED.md) lists every card that has left, with its evidence.

Two screen verdicts make a removal final at once: `CUT(no_lift)`, where the card did not improve the result, and `CUT(harmful)`, where it made the result worse. The other exits are staged. The card leaves the published plugins at once, and a copy you already installed stays until you update. A row in RETIRED.md then records whether the failure comes back in the owner's own sessions over at least 90 days. Two events during that watch restore the card. An event is a new, independent occurrence of the failure. After `CUT(subsumed)`, the verdict that the model now handles the failure without the card, an entry into the failure that a guard blocks also counts. One exception applies. When an independent guard already blocks a card's failure, a watch could not see the failure return, so a removal for a platform change or under the admission policy is final at once. [ADR 0007](docs/adr/0007-retirement-is-staged-for-three-exits.md) has the rules.

## Read the record behind the cards

The repository is also a knowledge base: evidence, explanations and failure records you can use without installing a card.

- [CATALOG.md](CATALOG.md) has the evidence posture of every card, the card forms and the admission detail. CI checks its tables against the cards.
- [Three decisions, and what they share](docs/explanations/three-decisions.md) looks at what three recorded decisions here have in common underneath the individual traps.
- [SECURITY.md](SECURITY.md) states the security commitments.
- [LICENSE](LICENSE) is the MIT license that covers the collection.
