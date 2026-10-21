<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

This repository is a set of written records of failures, mistakes that coding agents made in real engineering work. A coding agent is an AI model that edits code and runs commands for you. Each record is a pair of Markdown files that you can read with no install, a dated log of each time the failure was seen and a note of what has been measured about it. What is known is that these failures happened, and each record says when and where. Each record also comes with a skill, a `SKILL.md` file of instructions that a coding agent such as Claude Code can load. No skill here has been shown to make an agent less likely to repeat its failure.

Most records started from one failure in the work of the maintainer, the person who keeps this repository, and many have been seen only once. They cover Git pulls, deploy checks, tests that pass for the wrong reason, scripts that block risky commands, and handoffs between agents. Two skills, `im-down` and `im-up`, were designed on purpose rather than written after a recorded incident. One test found a difference, once. On 2026-09-01, an agent (`claude-sonnet-4.5`) that saw only the name and one-line description of the `pull-rebase` skill avoided a silent rewrite of its Git history in 6 of 8 runs, and the same agent without that line avoided it in 0 of 8. The test used an earlier wording of that line and has not been repeated, and 8 runs are too few to rule out chance, so the skill's own record does not count it as a shown effect. Later, larger tests of the same skill decided nothing. No other skill has been tested with and without it. The collection serves the maintainer's own work first, and other developers who work with a coding agent.

Treat the records as documentation. They are the main thing this repository offers, and reading them costs nothing. The skills are the optional, active part, and their value is not yet shown. A plugin is a package that Claude Code installs, and the skills come as three plugins, one for each subject: engineering, orchestration and meta. A plugin can put a skill in front of the agent in every session. A skill gets that place only if its failure has been seen at least twice or it has been tested with and without the skill, whatever the result, and only if it is not a routine you start yourself, such as a session handoff. For each such skill, the agent sees its name and one-line description, about 70 to 80 tokens per skill as `/context`, Claude Code's own context counter, counts them (Claude Code 2.1.305, measured 2026-10-20, [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476)). When Claude Code lists a skill by name only, which it decides from the space it has for the list, the skill costs under 20 tokens. Every other skill stays out of the session until you type `/` and its name, and costs nothing until then. You may not want to install anything yet. Nothing here shows that the skills help, and every record can be read without them.

## Decide whether to install anything

Below, a card is one skill together with its two records: `gotchas.md`, the failure log, and `EVIDENCE.md`, where the card came from and what has been measured. Each card name in the tables links to its failure log. Pick the answer that fits your work.

- **Read only.** Choose this if you want to know the failures but do not want new instructions in your sessions. Start with [CATALOG.md](CATALOG.md), then open the failure log of any card in the tables below that matches your work. [Three decisions, and what they share](docs/explanations/three-decisions.md) explains what three recorded decisions have in common. There is nothing to install.
- **Install one group.** Choose this if one kind of failure in the tables below matches work your agent does often, and you accept instructions whose benefit is not yet shown. The groups split the skills by subject so that you install only what you want: `mrbinnacle-engineering` for shipping software, `mrbinnacle-orchestration` for work spread across agents, and `mrbinnacle-meta` for the skill system itself. A group costs 70 to 80 tokens per session for each of its cards marked "every session" in the tables below, and nothing for its cards marked "by hand". That cost buys a card the agent can reach for when its failure comes up, without you remembering to call it. It does not buy a shown benefit. The commands are in [Install](#install).
- **Wait.** Choose this if you need a controlled result before you add instructions to your agent. Only `pull-rebase` has controlled tests, and they decided nothing. Each card's `EVIDENCE.md` records any controlled result it has.

The [rule for what gets in](ADMISSION.md) decides which new skills enter the collection. Its default answer is no.

## Which cards load on their own

An occasion is one independent occurrence of a card's failure, counted and dated after the fact. Running a card is not an occasion.

Two rules decide where a card loads. First, a card loads in every session only when its `EVIDENCE.md` counts two or more occasions or records a controlled result, a test run with and without the card ([ADR 0008](docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md)). Below that bar, the card runs by hand. Second, a card that is a routine you start, or that has side effects, runs by hand whatever its record says. The first rule counts any controlled result, including one that decided nothing. That is why `pull-rebase`, seen once, loads every session. By hand means the card puts nothing in the session until you type `/` and its name. CI refuses a card that loads every session below the bar, and it checks the Loads column below against each card's own settings. [CATALOG.md](CATALOG.md#card-evidence) has each card's occasion count, checked by CI against its record.

### A tool, test or agent reports success over wrong work

The output says the work succeeded, and it did not. In `pull-rebase` the pull completes and gives no warning, while it has rewritten local history without asking. The other cards in this group are false success alone.

| Card | Group | What goes wrong | Loads |
|---|---|---|---|
| [`pull-rebase`](skills/engineering/pull-rebase/gotchas.md) | engineering | A pull completes without warning after it silently rewrote local commits. | every session (tested, no verdict) |
| [`stale-deploy`](skills/engineering/stale-deploy/gotchas.md) | engineering | A poll matches content already on the page, so it confirms a deploy that has not landed. | by hand (seen once) |
| [`mocked-stub`](skills/engineering/mocked-stub/gotchas.md) | engineering | A test patches a helper that is a stub in production, so the suite passes over a branch that never ran. | by hand (seen once) |
| [`vacuous-check`](skills/engineering/vacuous-check/gotchas.md) | engineering | A success check accepts an error body because it asks only whether the output is non-empty. | every session (seen at least twice) |
| [`clirunner-env`](skills/engineering/clirunner-env/gotchas.md) | engineering | A test's environment override leaves a key in place, the real call happens, and the assertion still passes. | by hand (seen once) |
| [`subagent-handback`](skills/orchestration/subagent-handback/gotchas.md) | orchestration | A subagent returns claims and citations that nobody checked. | every session (seen at least twice) |

Controlled tests, with and without a card, run in a separate repository, [skill-harness](https://github.com/MrBinnacle/skill-harness). Only `pull-rebase` has them, and its verdict is `CANT_TELL_YET`, the test's word for a result too weak to decide on. Three experiments ran. The first, on 2026-09-01, is the 8-run result at the top of this page. In the second, a full-size run on 2026-09-03, the agent never ran into the trap, with the card or without it. The third, a readout dated 2026-10-02, used a design that forces the trap and compared the card, a placebo card and no card. It stopped at its planned cap of 97 looks, 97 runs for each of the three, with no verdict either way. The card was neither shown to help nor shown not to. All three ran on earlier wordings of the card. The [evidence record](skills/engineering/pull-rebase/EVIDENCE.md) has every run. No skill claims a measured benefit yet.

### A guard or hook misfires

A guard is a script that checks each command before the agent runs it. A hook is a rule that runs a script or shows a reminder when something happens in the session.

| Card | Group | What goes wrong | Loads |
|---|---|---|---|
| [`pretooluse-prose`](skills/engineering/pretooluse-prose/gotchas.md) | engineering | A command guard blocks prose that only mentions the command. | every session (seen at least twice) |
| [`dead-predicate`](skills/meta/dead-predicate/gotchas.md) | meta | A hook that should show a reminder stays silent because its pattern can never match, and the silence reads as "nothing needed it". | every session (seen at least twice) |

### Boundaries and handoffs

These cards do not catch a failure. They give a fixed shape to the end of a piece of work or to a handoff between sessions or agents. Three of them, `im-down`, `im-up` and `closure-mode`, are routines you start. The others are references the agent can use on its own.

| Card | Group | What it does | Loads |
|---|---|---|---|
| [`im-down`](skills/engineering/im-down/gotchas.md) | engineering | Writes the closing state of a session as a packet the next session can check. | by hand (you start it) |
| [`im-up`](skills/engineering/im-up/gotchas.md) | engineering | Checks that packet against the repository when the next session starts. | by hand (you start it) |
| [`closure-mode`](skills/engineering/closure-mode/gotchas.md) | engineering | Runs the verification list at a boundary instead of handing it back as options. | by hand (you start it) |
| [`decision-rights`](skills/orchestration/decision-rights/gotchas.md) | orchestration | Separates what the reader of a handoff may re-examine from what is settled. | by hand (seen once) |
| [`disposition-schema`](skills/orchestration/disposition-schema/gotchas.md) | orchestration | Gives parallel reviews one fixed output shape, so their results can be compared. | every session (seen at least twice) |
| [`halt-as-deliverable`](skills/engineering/halt-as-deliverable/gotchas.md) | engineering | Records the stop as the result when your own check stops the work. | every session (seen at least twice) |

## What the agent receives

In a Claude Code session, each loaded card's description is in context, so the agent knows the card exists. The full `SKILL.md` loads only when the agent or you invoke the card. Every card marked by hand sets `disable-model-invocation: true`, which keeps even the description out of the session. The [Claude Code skills documentation](https://code.claude.com/docs/en/skills.md) states this behaviour (read 2026-10-20). Published cards carry only `name` and `description` in their frontmatter, the header block at the top of `SKILL.md`, plus `disable-model-invocation` on the cards that run by hand.

This is the whole line the agent receives for `vacuous-check`. Claude Code lists a plugin's skill under the plugin's name.

> `mrbinnacle-engineering:vacuous-check`: Fail-open success checks. Use when a script says OK but nothing happened, a probe batch returns a false negative or 0 results, or `String(got) === String(want)` passes on a type mismatch.

A description can carry the rule itself. The line for `pull-rebase` reads "Use before `git pull` where `pull.rebase` may be `true`, or after a pull rebased your commits. `--no-ff` does not stop the rebase; every local SHA changes. Check config first; recover by reflog." The 2026-09-01 run measured an earlier wording of this line, which the card has since replaced. In 6 of its 8 runs the agent changed its Git command with only the description in view, and it never opened the full file. Each card's `EVIDENCE.md` gives a smaller per-card cost from a different counter, `skill-harness skill audit`. The 70 to 80 figure above is what Claude Code itself reports.

## How cards get in and out

The [rule for what gets in](ADMISSION.md) asks four questions. Does the model make the failure without the card? Does the failure recur independently? Is a skill the right fix, rather than a project rule or a check? Is the evidence written down, so that the card can leave later? Candidates wait in the open in [`_quarantine/`](_quarantine/README.md).

Not every published card meets the rule. It came after many current cards were published. [The 2026-08-15 triage](dispositions/2026-08-15-S295-admission-triage.md) re-tested the cards published then. Most did not pass all four questions on recorded evidence, and the common gap was recurrence. The triage retired nothing, because removal goes through the routes below. `mocked-stub` and `clirunner-env` were admitted after the rule, on 2026-08-24, with one occasion each, and each still has one. Cards are not graded by when they arrived. Each card's `EVIDENCE.md` states where it stands, and the loading rules above keep a card seen once out of every session. The route that withdraws a card when its own record fails the rule has been used once, on a record of zero. No written rule says whether a record of one should trigger it, or when a card seen only once leaves. [#551](https://github.com/MrBinnacle/skills/issues/551) tracks that gap.

A card leaves on a measured result, on the platform change its record named in advance, or when its own record fails the admission rule outright. The rule has removed a card. `skill-necessity-gate` was removed in August 2026 because its own record counted zero occasions. [RETIRED.md](RETIRED.md) lists every departure with its evidence.

A removal is final at once when a test finds that the card did not improve the result, or made it worse. A removal is staged when a test finds that the model now handles the failure without the card, when the named platform change ships, or when the record fails the rule. One exception applies. When a separate guard already blocks a card's failure, as one does for `pull-rebase` in the maintainer's setup, a watch could not see the failure return, so the platform and rule removals are final at once. On a staged removal, the card leaves the plugins at once, and a copy you already installed stays until you update. A row in the [On watch table](RETIRED.md#on-watch) then records, for at least 90 days and 180 sessions, whether the failure comes back in the maintainer's own sessions. Two new independent occasions restore the card. One occasion extends the watch once by 90 days, up to 180 days in all. The maintainer's periodic review searches those session records. Each occasion it finds becomes a dated entry in the card's `gotchas.md` and a count in its `EVIDENCE.md`, and CI refuses a count that has no dated entry ([Recording a new occurrence](AGENTS.md#recording-a-new-occurrence)). A weekly scheduled check fails when a watch is past its close date. That schedule is a trial, and it retires on 2026-11-07 if it has caught nothing the pull-request checks missed ([SECURITY.md](SECURITY.md)). The session records are private, so a watch that finds nothing cannot be checked from outside. The [Report a gotcha](https://github.com/MrBinnacle/skills/issues/new/choose) issue form is the only outside channel. An outside report about a published card already counts as an occasion once a reproduction confirms it, and it is recorded and counted like any other ([An issue you did not create](AGENTS.md#an-issue-you-did-not-create)). No written rule says whether such a report also counts as a watch event. [#552](https://github.com/MrBinnacle/skills/issues/552) tracks that gap. [ADR 0007](docs/adr/0007-retirement-is-staged-for-three-exits.md) has the retirement rules.

## Install

The install below is for Claude Code. An install for Pi, another coding agent, is planned and untested.

Run these two commands one at a time. Claude Code reads a paste of both in one block as a single malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

Install `mrbinnacle-orchestration` and `mrbinnacle-meta` the same way if you want them.

The cards appear after `/reload-plugins`. If Claude Code reports the reload as pending, run `/reload-plugins --force`. A new `claude` session in the same profile also loads them. Confirm what you installed with `claude plugin list`. It reports the installed plugins and their versions.

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

## Security and license

[SECURITY.md](SECURITY.md) states the security commitments. [LICENSE](LICENSE) is the MIT license that covers the collection.
