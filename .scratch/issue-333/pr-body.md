# Issue #333 — publish an install form that works without SSH

## What this change does

The published install path named the GitHub shorthand `MrBinnacle/skills`. On a cold install of v3.0.1 that form failed for a stranger with no SSH key: `git@github.com: Permission denied (publickey)`. The CLI resolved the shorthand toward SSH. The HTTPS clone URL is a first-class `git` source in the Claude Code plugin CLI docs and installed the collection without a key.

This PR:

1. Changes `README.md` §Install and the site install block (`site/index.html`) to publish `https://github.com/MrBinnacle/skills.git`.
2. Adds the shell form beside the interactive form in the README.
3. States in the README which forms were verified, on which CLI version, on which date.
4. Adds `scripts/test_install_form.py`, which pins those published bytes and runs the cold install when `claude` is present.
5. Adds a changeset (`.changeset/install-form-https-333.md`).

## CLI docs consulted

The ticket asked for the current CLI docs through Context7. Context7 is not a tool in this container. The official Claude Code plugin docs were fetched instead:

- https://code.claude.com/docs/en/plugins/install — "Add a marketplace" source table; GitHub shorthand, full clone URL, and `https://` forms; private-marketplace credentials section.
- https://code.claude.com/docs/en/plugins/cli-reference — `claude plugin marketplace add <source>` source-type table.

Documented forms that apply here:

| Source you type | Type | Fetch |
|---|---|---|
| `owner/repo` | `github` | clones GitHub; shorthand resolution can use SSH |
| `https://github.com/owner/repo` or `...repo.git` | `git` | clones the HTTPS URL |

For the shorthand the docs say Claude Code checks whether an SSH key authenticates to github.com, then clones over SSH if it does and over HTTPS if it does not, and that `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` skips the check. That fallback is not a guarantee a stranger's machine will take it. The HTTPS URL does not depend on it.

**Chosen published form:** `/plugin marketplace add https://github.com/MrBinnacle/skills.git` and `claude plugin marketplace add https://github.com/MrBinnacle/skills.git`.

## Acceptance criteria

### 1. README and site publish a form that works without SSH

**Built.** Both reader surfaces now carry the HTTPS URL in the marketplace-add command. The site kbd block and the README install fence no longer publish the shorthand as the install command.

**Test.** `scripts/test_install_form.py` asserts, on the live tree:

- README `## Install` and `site/index.html` name `https://github.com/MrBinnacle/skills.git`.
- The interactive slash form and the shell form both carry that URL.
- The README fence a reader copies carries that URL.
- The site does not publish `marketplace add MrBinnacle/skills`.

**Before the change.** Running the new suite against the pre-change tree failed 11 content checks, including:

```
FAIL README install block names the HTTPS marketplace URL: expected 'https://github.com/MrBinnacle/skills.git' in ## Install
FAIL site install block names the HTTPS marketplace URL: expected 'https://github.com/MrBinnacle/skills.git' in site/index.html
FAIL README marketplace fence copies the HTTPS URL: fences=['/plugin marketplace add MrBinnacle/skills\n/plugin install mrbinnacle-engineering']
```

**After the change.** All content checks pass.

### 2. Cold install from a clean CLAUDE_CONFIG_DIR, no SSH key, following README

**Built.** The README shell form is the form the cold install ran.

**Test.** The same suite runs, when `claude` is on PATH:

```
CLAUDE_CONFIG_DIR=<empty temp dir>
HOME=<empty temp dir, no .ssh>
GIT_SSH_COMMAND='ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes'
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
claude plugin install mrbinnacle-engineering
claude plugin install mrbinnacle-orchestration
claude plugin install mrbinnacle-meta
claude plugin list --json
```

It asserts marketplace add succeeded, all three installs succeeded, versions are 3.0.1, and the three plugins carry 14 `SKILL.md` files on disk. When `claude` is absent the suite FAILS rather than skips.

**Transcript (Claude Code 2.1.287, 2026-10-02).** Environment: clean `CLAUDE_CONFIG_DIR`, empty `HOME` with no `.ssh` directory, `GIT_SSH_COMMAND` as above.

```
$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
Adding marketplace…Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): https://github.com/MrBinnacle/skills.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
✔ Successfully added marketplace: mrbinnacle-skills (declared in user settings)
exit=0

Configured marketplaces:
  ❯ anthropic-plugin-directory
    Source: Built in (Anthropic Directory)
  ❯ mrbinnacle-skills
    Source: Git (https://github.com/MrBinnacle/skills.git)

$ claude plugin install mrbinnacle-engineering
✔ Successfully installed plugin: mrbinnacle-engineering@mrbinnacle-skills (scope: user)
exit=0
$ claude plugin install mrbinnacle-orchestration
✔ Successfully installed plugin: mrbinnacle-orchestration@mrbinnacle-skills (scope: user)
exit=0
$ claude plugin install mrbinnacle-meta
✔ Successfully installed plugin: mrbinnacle-meta@mrbinnacle-skills (scope: user)
exit=0

plugin list --json:
  mrbinnacle-engineering@mrbinnacle-skills  version 3.0.1
  mrbinnacle-meta@mrbinnacle-skills         version 3.0.1
  mrbinnacle-orchestration@mrbinnacle-skills version 3.0.1

skills on disk under installPath: 14 SKILL.md files (10 engineering + 3 orchestration + 1 meta)
```

**Before the change.** The test's cold-install path already used the HTTPS URL (it reads the published form after the content fix). Against the pre-change tree the suite failed the content checks that decide what a stranger runs; the HTTPS cold path itself was already green when forced. The defect under test is the published bytes, not the CLI's ability to clone HTTPS.

### 3. Interactive `/plugin marketplace add` tested; README says which forms were verified

**Built.** README §Install now lists verified forms with CLI version and date.

**Test.** Content checks require the README to say `verified`, to name the `interactive` form, and to name the `shell` form. The suite's live cold install covers the shell form end to end.

**Interactive form run.** Interactive `/plugin marketplace add` was driven in a PTY against Claude Code 2.1.287 from a clean config with `projects["<cwd>"].hasTrustDialogAccepted` set so the workspace-trust dialog did not block the panel. Session output:

```
❯ /plugin marketplace add https://github.com/MrBinnacle/skills.git
  Add Marketplace
  Enter marketplace source: https://github.com/MrBinnacle/skills.git
  Cloning repository (timeout: 120s): https://github.com/MrBinnacle/skills.git
  Clone complete, validating marketplace…
  Successfully added marketplace: mrbinnacle-skills
  Plugins changed. Run /reload-plugins to activate.
```

Follow-up `claude plugin marketplace list` in that config:

```
  ❯ mrbinnacle-skills
    Source: Git (https://github.com/MrBinnacle/skills.git)
```

**README statement (published).** Verified forms, Claude Code 2.1.287, 2026-10-02, from a clean `CLAUDE_CONFIG_DIR` with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git`
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git`
- shell `claude plugin install` of all three plugins — 3.0.1, 14 cards

**Before the change.** The README named no verified forms and published only the shorthand.

## Companion artifacts

| Artifact | Status |
|---|---|
| Issue #333 (`MrBinnacle/skills`) | Named in the ticket; this PR is the fix. |
| Private research checkout audit `docs/audit/skills-v3.0.1-post-release-S498.md` | Cited by the ticket. That path does not exist in this repository. The private research directory name is omitted here because the de-personalization gate blocks it. |
| Mutation receipt | The ticket names none. `scripts/mutation_receipt.py` was not run. |

## Gate run

Repository tooling, after the change (`PYTHONUTF8=1`):

| Gate | Result |
|---|---|
| `scripts/test_install_form.py` | PASS (17 checks, including live cold install) |
| `scripts/validate_card_files.py` + suite | PASS |
| `scripts/validate_scoreboard.py` + `test_readme_admission_lead.py` | PASS |
| `scripts/validate_eval_corpora.py` + suite | PASS |
| `scripts/validate_skill_formats.py` + suite | PASS |
| `scripts/validate_voice_provenance.py` + suite | PASS |
| `scripts/validate_brand_kit.py` + suite | PASS |
| `scripts/validate_conformance.py --root .` + suite | PASS |
| `scripts/validate_vale_style.py` + suite | PASS |
| `scripts/validate_spec_conformance.py --root .` + suite | PASS (skills-ref@0.1.5) |
| `scripts/validate_site_links.py` + suite | PASS |
| `scripts/test_check_prose_claims.py` | PASS |
| `scripts/test_validate_disposition_counts.py` + checker | PASS |
| `scripts/test_validate_path_residue.py` + checker | PASS |
| `scripts/test_validate_quarantine_landing.py` | PASS |
| `scripts/test_validate_standing_costs.py` + checker | PASS |
| `scripts/test_release_model_disclosure.py` | PASS |
| `scripts/test_captured_exit_handling.py` | PASS |
| `scripts/test_design_enforcement_claim.py` | PASS |
| `scripts/test_vale_scope.py` | PASS (Vale binary absent; suite notes the skip) |
| `scripts/test_release_gate.py` | PASS |
| im-down / im-up parity suites | PASS, each prints `, no-drift` |
| im-down poison control (`fixture-stale.md --mode produce`) | REJECTED, non-zero exit |
| `scripts/test_link_skills_guard.py` | PASS after PowerShell 7.4.6 was installed in this container. First run failed with `no pwsh or powershell on PATH`; the suite refuses to skip. Re-run green once `pwsh` was on PATH. |
| De-personalization residue patterns | Clean on README, site, test, and changeset. Path-residue checker PASS. |

## Mutation campaign

The ticket names no mutation receipt. None was applied.

## Scope notes

Out of scope and left unchanged: `CATALOG.md` install block, `AGENTS.md` maintainer install line, `scripts/link-skills.ps1` refusal message, and the `npx skills add MrBinnacle/skills` alternate installer. Those surfaces still name the shorthand. The ticket named README and the site install block.

## Revisit if

The CLI changes its shorthand resolution to HTTPS by default. The README still documents the shorthand's SSH failure as historical evidence for why the HTTPS URL is published.
