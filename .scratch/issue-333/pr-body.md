# Publish the HTTPS marketplace install form (#333)

Cold install of v3.0.1 failed for a stranger with no SSH key: the README's then-published marketplace-add line used the GitHub shorthand `MrBinnacle/skills`, the CLI resolved that shorthand to SSH, and the install died with `git@github.com: Permission denied (publickey)`. This branch publishes the HTTPS clone URL `https://github.com/MrBinnacle/skills.git` on every reader-facing install surface, pins the suite to the bytes a reader actually copies, and proves both the published URL and the checked-out tree install clean from an empty config directory.

Branch: `agent/issue-333`. Code head at the time of this body: `7c5963ae71d2f6b98389070df885013d3a0de5d9`.

## Files on this branch (`git diff --name-only origin/main...HEAD`)

- `.changeset/install-form-https-333.md`
- `.github/workflows/tests.yml`
- `AGENTS.md`
- `CATALOG.md`
- `README.md`
- `scripts/link-skills.ps1`
- `scripts/test_install_form.py`
- `site/index.html`

Versions at this head: `package.json` `3.0.1`; each of `mrbinnacle-engineering`, `mrbinnacle-orchestration`, `mrbinnacle-meta` declares `3.0.1` in its `plugin.json`. Published cards: 14 (engineering 10, orchestration 3, meta 1). Claude Code used for the cold installs: `2.1.287`.

CI: the **Install form** job in `.github/workflows/tests.yml` (`install-form`) installs `@anthropic-ai/claude-code@2.1.287` and runs `python scripts/test_install_form.py`. That job was already on this branch from the previous build and is unchanged here.

`.changeset/install-form-https-333.md` is left exactly as it stands. Its level (`major` against `patch`) is an open decision the coordinator holds; this rework does not touch it.

## Acceptance criteria

### Original ticket

**1. README and the site install block give a form that works without SSH.**
Satisfied by the HTTPS URL `https://github.com/MrBinnacle/skills.git` in the README install fences and in `site/index.html`'s `/plugin marketplace add` kbd. The CLI docs' documented `git` source is that full URL; the operator ruled on 2026-10-05 that it is the form to publish.
Test: `scripts/test_install_form.py` checks `README install block names the HTTPS marketplace URL`, `site install block names the HTTPS marketplace URL`, `README shows the interactive form with the HTTPS URL`, `README shows the shell form with the HTTPS URL`, `site interactive form uses the HTTPS URL`, `README marketplace fence copies the HTTPS URL`, and `no README install fence publishes only the shorthand`.
Observed: before this branch the site and CATALOG/AGENTS/link-skills surfaces published the shorthand marketplace-add form (`MrBinnacle/skills` after `marketplace add`); after the change those checks are green. The shorthand form was also observed failing a cold install on a machine with no SSH key — that is the incident this branch exists to close.

**2. A cold install from a clean `CLAUDE_CONFIG_DIR` with no SSH key, following the README exactly, succeeds.**
Satisfied by the live half of `scripts/test_install_form.py`, which executes the README's own `claude plugin marketplace add` and `claude plugin install` lines exactly as written (argv[0] only is replaced with the CLI path). Transcript below.
Test: `cold marketplace add (HTTPS form) succeeds without SSH`, `cold install of all three plugins succeeds`, `installed plugins report one nonempty version from the cold install`, `cold install carries cards in every requested plugin`, plus the version cross-checks under criterion 3.
Observed: the previous suite replaced the README install command's last word with its own plugin list, so a README naming a plugin the marketplace does not declare stayed green. The repair runs the README lines as written and checks every published plugin name against `.claude-plugin/marketplace.json` first.

**3. The interactive `/plugin marketplace add` form is tested too, and the README says which forms were verified.**
Satisfied by the `Verified forms` block in `README.md` (interactive form, shell form, shell install of all three plugins at 3.0.1, Claude Code 2.1.287) and by the suite checks that name those surfaces and then compare the stated versions to the cold install's own `claude plugin list --json` and to `claude --version`.
Test: `README states which install forms were verified`, `README names the interactive form among the verified surfaces`, `README names the shell form among the verified surfaces`, `README Verified forms record states a Claude Code version`, `README Verified forms record states a plugin version`, `README Verified forms Claude Code version matches the installed CLI`, `README Verified forms plugin version matches the cold install`.
Observed: a README that stated `Claude Code 0.0.1` and `at 9.9.9` stayed green at the previous head; both now fail by their own named check (mutant receipts below).

### Rework round 1 (S516)

**1. README cites the wrong number.**
`README.md` now says the cold-install transcript is in "the pull request that changed this section (#340)". #333 is the issue; #340 is the pull request.
Test: `README cold-install transcript cites pull request #340`.
Observed before: the sentence cited (#333). After: the check is green.

**2. The suite must run the README's plugin install lines as written.**
`scripts/test_install_form.py` takes every `claude plugin install <name>` line from the README shell fence and every `/plugin install <name>` line from the README and site text blocks. Each `<name>` is checked against the `plugins[].name` values in `.claude-plugin/marketplace.json`. The live cold install then runs the README's install line exactly as written.
Test: `README shell install names are declared in marketplace.json`, `README and site slash install names are declared in marketplace.json`, and the live `cold install of all three plugins succeeds`.
Mutant receipt (requirement 2): changing README line 25 from `claude plugin install mrbinnacle-engineering` to `claude plugin install mrbinnacle-bogus` makes the suite print
`FAIL README shell install names are declared in marketplace.json: names=['mrbinnacle-bogus'], declared=['mrbinnacle-engineering', 'mrbinnacle-meta', 'mrbinnacle-orchestration']`
and also fails the live install of that line (`mrbinnacle-bogus: rc=1`). Restored to green afterwards.

**3. The suite must check the "Verified forms" record against the cold install.**
The version the README's Verified forms list states for the plugins is compared to the version `claude plugin list --json` reports after the cold install. The Claude Code version the list states is compared to the CLI version the suite runs (`claude --version`).
Test: `README Verified forms Claude Code version matches the installed CLI`, `README Verified forms plugin version matches the cold install`.
Mutant receipt (requirement 3): changing README `at 3.0.1` to `at 9.9.9` makes the suite print
`FAIL README Verified forms plugin version matches the cold install: README says '9.9.9', cold install reports {'3.0.1'}`.
A second mutant, `Claude Code 2.1.287` → `Claude Code 0.0.1`, prints
`FAIL README Verified forms Claude Code version matches the installed CLI: README says '0.0.1', CLI reports '2.1.287'`.
Both restored to green afterwards.

**4. Every reader-facing install site gives the same form.**
`CATALOG.md`, `AGENTS.md` and `scripts/link-skills.ps1` now publish `https://github.com/MrBinnacle/skills.git`. `npx skills add MrBinnacle/skills` lines are a different installer and are unchanged.
Test: `CATALOG install block names the HTTPS marketplace URL`, `AGENTS.md install line names the HTTPS marketplace URL`, `link-skills.ps1 refusal message names the HTTPS marketplace URL`, and `no tracked install surface publishes the SSH-prone marketplace shorthand` — a scan over `git ls-files` that fails if any tracked file other than `docs/design/variants/**` and `.changeset/**` still contains the contiguous shorthand form (`marketplace add` immediately followed by `MrBinnacle/skills`).
Mutant receipt: putting the shorthand back into `CATALOG.md` prints both `FAIL CATALOG install block names the HTTPS marketplace URL` and `FAIL no tracked install surface publishes the SSH-prone marketplace shorthand: files still carrying the shorthand form: ['CATALOG.md']`. Restored to green afterwards.

**5. Remove the private-path sentence.**
The sentence "The private research checkout's post-release audit path named in the ticket does not exist in this repository." is deleted. "Issue #333 tracks that failure." is now "Issue #333 recorded that failure." because #333 closes when this merges.
Test: `README omits the private-path disclaimer`, `README records issue #333 in the past tense`.
Observed before: both checks failed on the old README text. After: green.

**6. Test the tree under test, not only the default branch.**
The published-URL case stays. A second cold install runs `claude plugin marketplace add <path of the checked-out tree>` in a separate clean `CLAUDE_CONFIG_DIR` and installs all three plugins from that tree, then compares the reported versions to each plugin's own `plugin.json` on the branch.
Test: `cold install from the checked-out tree succeeds`, `checked-out tree cold install carries every declared plugin`, `checked-out tree cold install reports the branch plugin versions`, `checked-out tree cold install carries cards in every plugin`.
Observed: before this repair the live half installed only from `https://github.com/MrBinnacle/skills.git`, so a break this branch made in `.claude-plugin/marketplace.json` was invisible. The new case installs from `/home/agent/workspace` and is green.

**7. Windows home.**
`cold_env()` sets both `HOME` and `USERPROFILE` to the empty scratch home. Windows OpenSSH and git read `USERPROFILE`, not `HOME`; setting only `HOME` left a Windows runner able to see the real user profile.
Test: covered by the live cold-install path that uses `cold_env()` for both cases. There is no separate named check; the setting is in the install environment both cases share.

**8. PR body true at head.**
This body lists every file in `git diff --name-only origin/main...HEAD` at code head `7c5963ae71d2f6b98389070df885013d3a0de5d9`, the versions that head declares (`3.0.1` everywhere, Claude Code `2.1.287`), the card count (14), and the **Install form** job in `.github/workflows/tests.yml`.

**9. Do not change `.changeset/install-form-https-333.md`.**
Untouched. Still `major`. The level decision stays with the coordinator.

## Cold-install transcript

Environment for both cases: clean `CLAUDE_CONFIG_DIR`, empty scratch `HOME` and `USERPROFILE`, `GIT_SSH_COMMAND="ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes"`. No SSH key exists under the scratch home.

### Case 1 — published URL, commands exactly as the README publishes them

```
$ claude --version
2.1.287 (Claude Code)

$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
Adding marketplace…Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): https://github.com/MrBinnacle/skills.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
✔ Successfully added marketplace: mrbinnacle-skills (declared in user settings)

$ claude plugin install mrbinnacle-engineering
Installing plugin "mrbinnacle-engineering"...✔ Successfully installed plugin: mrbinnacle-engineering@mrbinnacle-skills (scope: user)

$ claude plugin install mrbinnacle-orchestration
Installing plugin "mrbinnacle-orchestration"...✔ Successfully installed plugin: mrbinnacle-orchestration@mrbinnacle-skills (scope: user)

$ claude plugin install mrbinnacle-meta
Installing plugin "mrbinnacle-meta"...✔ Successfully installed plugin: mrbinnacle-meta@mrbinnacle-skills (scope: user)
```

`claude plugin list --json` after that install reported all three plugins at `version: 3.0.1`, `scope: user`, with `installPath` under the scratch `CLAUDE_CONFIG_DIR/plugins/cache/mrbinnacle-skills/<plugin>/3.0.1`. Card count from those install paths: 14 `SKILL.md` files (10 + 3 + 1).

### Case 2 — checked-out tree, the branch under test

```
$ claude plugin marketplace add /home/agent/workspace
Adding marketplace…✔ Successfully added marketplace: mrbinnacle-skills (declared in user settings)

$ claude plugin install mrbinnacle-engineering
Installing plugin "mrbinnacle-engineering"...✔ Successfully installed plugin: mrbinnacle-engineering@mrbinnacle-skills (scope: user)

$ claude plugin install mrbinnacle-orchestration
Installing plugin "mrbinnacle-orchestration"...✔ Successfully installed plugin: mrbinnacle-orchestration@mrbinnacle-skills (scope: user)

$ claude plugin install mrbinnacle-meta
Installing plugin "mrbinnacle-meta"...✔ Successfully installed plugin: mrbinnacle-meta@mrbinnacle-skills (scope: user)
```

`claude plugin list --json` after that install reported all three plugins at `3.0.1`, matching each `skills/<bucket>/.claude-plugin/plugin.json` on this branch. Card count: 14.

## Suite result at head

`python scripts/test_install_form.py` prints every check above as `ok`, then:

```
PASS: install form is the HTTPS URL on every reader surface, published and checked-out-tree cold installs are green, and the Verified forms record matches the CLI
```

## Which test covers which criterion

| Criterion | Test |
|---|---|
| T1 / R1 — SSH-free form on README + site | `README install block names the HTTPS marketplace URL`, `site install block names the HTTPS marketplace URL`, interactive/shell/fence HTTPS checks |
| T2 / R2 — cold install follows README exactly | live `cold marketplace add (HTTPS form)`, `cold install of all three plugins succeeds`; static `README shell install names are declared in marketplace.json` |
| T3 / R3 — verified forms + version cross-check | `README Verified forms *` checks, including `…matches the cold install` and `…matches the installed CLI` |
| R4 — same form on every surface + scan | `CATALOG`/`AGENTS.md`/`link-skills.ps1` HTTPS checks, `no tracked install surface publishes the SSH-prone marketplace shorthand` |
| R5 — README prose about the incident | `README cold-install transcript cites pull request #340`, `README omits the private-path disclaimer`, `README records issue #333 in the past tense` |
| R6 — tree under test | `cold install from the checked-out tree succeeds`, `checked-out tree cold install carries every declared plugin`, `checked-out tree cold install reports the branch plugin versions`, `checked-out tree cold install carries cards in every plugin` |
| R7 — Windows home | `cold_env()` sets `HOME` and `USERPROFILE`; exercised by both live cases |
| R8 — body true at head | this document |
| R9 — changeset untouched | `.changeset/install-form-https-333.md` still carries `major`, unmodified |
