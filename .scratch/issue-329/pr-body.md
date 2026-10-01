#329: Dependabot for pinned GitHub Actions

## What this is

This repository pins every GitHub Action by full commit SHA. Those pins never received update PRs, because the tree carried no `.github/dependabot.yml`. Issue #329 asks for that file, covering the github-actions ecosystem, weekly, with updates grouped. The source named on the ticket is `docs/research/stakeholder-coverage-S498.md` (S498 stakeholder sweep). That path does not exist in this container. The ticket text is the tracker of record here.

The ticket also names `skill-harness/.github/dependabot.yml` as the pattern to copy. That repository is not checked out in this container. Checked 2026-10-01, its GitHub Actions entry uses the required github-actions ecosystem, weekly schedule, and grouped updates. This focused config keeps those ticketed properties without importing that repository's labels, pull-request limit, or commit-message convention.

## Criterion 1: config covers github-actions, weekly, with updates grouped

**Built.** `.github/dependabot.yml`, Dependabot v2, one update entry:

- `package-ecosystem: "github-actions"`
- `directory: "/"`
- `schedule.interval: "weekly"`
- `groups.github-actions.patterns: ["*"]`

A trailing comment in the file records the revisit condition from the ticket: if this repository gains a package manifest beyond the changesets tooling already in `package.json`, add that ecosystem then. `package.json` today carries release tooling only; `.github/workflows/dependency-audit.yml` already audits it.

**Test that pins it.** `scripts/test_dependabot_config.py`. The live-tree cases read the shipped file and assert the three properties as external state: `live .github/dependabot.yml exists`, `live config covers the github-actions ecosystem`, `live github-actions schedule is weekly`, `live github-actions updates are grouped`, `live group carries a non-empty patterns list`.

**Observed before and after.** First run of the suite, before any implementation existed: every live case failed, starting with `FAIL live .github/dependabot.yml exists: expected /home/agent/workspace/.github/dependabot.yml to exist`. Every subprocess case also failed, because `scripts/validate_dependabot_config.py` was absent and python reported `can't open file`. After the config and validator landed, the same suite printed `PASS: dependabot config suite - live file covers github-actions weekly and grouped, the validator accepts it, and every breach shape is refused` and exited 0.

## Criterion 2: the config validates; the first run is noted as pending

**Built.** `scripts/validate_dependabot_config.py`, a stdlib-only checker. It parses the shipped file with a Dependabot-v2 subset reader (mappings, nested mappings, lists of mappings; not a general YAML engine) and refuses any config that fails one of these:

- `version` is not 2
- `updates` is missing or empty
- any update entry states no `directory`
- no update entry covers the `github-actions` ecosystem
- a github-actions entry's `schedule.interval` is not `weekly`
- a github-actions entry's `groups` is missing, empty, or carries a group whose `patterns` list is empty

Every github-actions entry is checked, not only the first. A second ungrouped entry would otherwise slip past a first-entry-only check.

**Test that pins it.** The same suite, through the validator as a subprocess on live and poison trees. Each poison tree lives in a temp directory and each case asserts the refusal *names the property*, not merely a non-zero exit:

| Poison fixture | Refusal the suite requires |
|---|---|
| no `.github/dependabot.yml` | names the missing file |
| `package-ecosystem: "npm"` only | names `github-actions` |
| `interval: "monthly"` | names `weekly` |
| no `groups` key | names groups |
| `patterns: []` | names patterns |
| `version: 1` | names version |
| the clean body | passes with a `PASS:` line |

**Observed before and after.** With the validator written and the live file still absent: all six poison message assertions reported `ok`, the clean-fixture case reported `ok`, and the three live cases still failed on the missing file. After `.github/dependabot.yml` landed, the validator printed `PASS: dependabot config - github-actions ecosystem, weekly schedule, updates grouped under ['github-actions']` and the full suite exited 0.

**First Dependabot run: pending.** This container holds no GitHub token and no outbound path to the Dependabot service. GitHub reads `.github/dependabot.yml` when the file reaches `main`, validates it server-side, and schedules the first weekly run from there. The first run is therefore noted as pending, not shown. Structural validation is the local half. The service-side half arrives after merge.

## Mutation campaign

The ticket names no mutation receipt. `scripts/mutation_receipt.py` does not exist in this repository; that instrument is skill-harness tooling. No mutation receipt was run. The poison controls above are the local mutation evidence: each plants one breach in a temp tree and requires the shipped validator to refuse it for the named reason. Each control also asserts the message that separates that breach from any other, so a green poison run cannot be a validator that exits non-zero for an unrelated reason.

## Companion artifacts

| Artifact | State |
|---|---|
| Ticket #329 | This branch. Tracker of record is the ticket text. |
| `docs/research/stakeholder-coverage-S498.md` | Does not exist in this container. Named on the ticket as the S498 stakeholder sweep source. |
| `skill-harness/.github/dependabot.yml` | Does not exist in this container. Named on the ticket as the pattern to copy. |
| `scripts/validate_dependabot_config.py` | Shipped on this branch. |
| `scripts/test_dependabot_config.py` | Shipped on this branch. |

## Gate run on this branch

Repository tooling, run after the implementation commit `bc50dec`. No lint or type tool is named in this repository's workflows, so none was invented.

| Check | Result |
|---|---|
| `scripts/test_dependabot_config.py` | PASS |
| `scripts/validate_dependabot_config.py` | PASS |
| captured-exit suite | PASS |
| path-residue suite + sweep | PASS |
| vale-scope suite | PASS |
| quarantine-landing suite | PASS |
| vale-style suite + check | PASS |
| im-down parity (`no-drift`) + im-up parity (`no-drift`) | PASS |
| stale-packet poison control | PASS |
| scoreboard suite + check | PASS |
| disposition-counts suite + check | PASS |
| prose-claims suite + check | PASS |
| README admission-lead suite | PASS |
| standing-cost suite + check | PASS |
| site-link suite + check | PASS |
| release-model disclosure suite | PASS |
| skill-format suite + check | PASS |
| voice-provenance suite + check | PASS |
| conformance suite + sweep | PASS |
| eval-corpus suite + check | PASS |
| brand-kit suite + check | PASS |
| DESIGN.md enforcement-claim suite | PASS |
| card-files suite | PASS |
| release-gate suite + `release_gate.py` | PASS |
| spec-conformance allowance suite + live run | PASS |
| link-guard suite | Not run in this container. The suite requires `pwsh` or `powershell` on PATH and refuses to report a pass when it cannot execute. CI's Windows cell runs it. |

Two environment notes, neither a code defect. First, prose-claims and several poison controls copy the tree into `/tmp` and run `git` there; this container's git refused those paths as dubious ownership until `safe.directory` was set for the run. CI clones as one user and does not hit that. Second, `skill-harness/.github/dependabot.yml` is absent here, so criterion 1's config was built from the ticket text rather than copied.

## Next action

Merge this branch. After merge, GitHub reads `.github/dependabot.yml`, validates it server-side, and opens the first weekly grouped update PR for the pinned actions. If that first run surfaces a schema complaint the local subset reader did not, treat the service as the authority and correct the config against it.
