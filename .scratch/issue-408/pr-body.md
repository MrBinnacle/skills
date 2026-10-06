# Issue #408: install form copyable units, reload guidance, confirmation command

## Ticket

README Install puts both interactive slash commands in one `text` fence. A reader who copies the fence whole gets a malformed-URL error on their first action (owner run, Claude Code v2.1.291, Windows, PowerShell 7.6.6, 2026-10-06, following README at `7b7a74b`). After a successful install, the session also could not see the cards until restart; the README said nothing about `/reload-plugins`, `--force`, or what to run to confirm the install.

This PR addresses the four acceptance criteria in the agent brief (S528). Out of scope, unchanged: the shell-form fence (a shell runs it line by line; the owner ran it successfully), `npx skills add`, the other two plugins, a credential-free machine, and any card.

## Companion artifacts

| Artifact | Status |
|---|---|
| Issue #408 | This ticket; the work is built against it. |
| Issue #333 | Prior install-form ticket; still cited in README as the record of the SSH-key failure. |
| PR #340 | Cited in README as the cold-install transcript; not created by this change. |
| `https://code.claude.com/docs/en/discover-plugins.md` | Vendor plugin docs; read 2026-10-06 for the reload / `--force` / next-start behaviour. |
| `scripts/test_install_form.py` | The install-form contract; extended here with the three new checks. |
| Mutation receipt under `docs/assurance/` | Does not exist. This repository has no `docs/assurance/` directory and the ticket names no mutation-receipt obligation. The campaign is recorded in this PR body only. |
| `docs/receipts-index.md` | Does not exist in this repository (that registry belongs to skill-harness, not here). |

## Criterion 1 — one `/plugin` command per copyable unit

**What was built.** The README Install section now holds two `text` fences, one per interactive slash command. The landing page puts each command in its own `.action` paragraph, so a drag-select of a paragraph copies one command. A sentence above the fences says the lines run one at a time.

**The test that pins it.** `scripts/test_install_form.py` gained two checks:

- `no README Install fence holds more than one /plugin command`
- `no site Install action holds more than one /plugin command`

Both use a new helper `slash_commands_in(block)`, which counts lines starting with `/plugin` inside one README fence or one landing-page action.

**Observed before the change.** The two checks reject the unmodified tree: the README fence and one landing-page `.action` paragraph each contain both slash commands. The landing-page check extracts the commands from the `<kbd>` elements inside that paragraph, which is the text a reader copies.

**Observed after the change.** Both checks print `ok`. The live cold-install half of the same suite (Claude Code 2.1.287 installed locally for this run) printed `PASS: install form is the HTTPS URL on every reader surface, published and checked-out-tree cold installs are green, and the Verified forms record matches the CLI`.

**Mutants that kill this check.**

| Mutant | Assertion that failed |
|---|---|
| M1: the two interactive fences merged back into one block | `no README Install fence holds more than one /plugin command` |
| M6: both slash commands share one site action | `no site Install action holds more than one /plugin command` |

## Criterion 2 — reload / `--force` / restart, with docs URL and read date

**What was built.** After the install steps the README states:

> The cards appear after `/reload-plugins`. If Claude Code reports the reload as pending, run `/reload-plugins --force`. A new `claude` session in the same profile also loads them. The plugin docs at https://code.claude.com/docs/en/discover-plugins.md state this behaviour (read 2026-10-06).

The behaviour claim is the vendor page's own, read 2026-10-06: plugins load on `/reload-plugins` or the next start, and a reload left pending stays pending until `/reload-plugins --force`. The owner's finding 2 (cards invisible until restart) is consistent with that page; the README now tells the reader the mechanism rather than leaving them to discover it.

**The test that pins it.** Three checks in `scripts/test_install_form.py`:

- `README puts reload guidance after the install commands`
- `README gives /reload-plugins --force for a pending reload`
- `README cites the Claude Code plugin docs URL with a read date`

Constants: `PLUGIN_DOCS_URL = "https://code.claude.com/docs/en/discover-plugins.md"`, `PLUGIN_DOCS_READ = "2026-10-06"`.

**Observed before the change.** All three failed on the unmodified README:

```
FAIL README puts reload guidance after the install commands: ## Install does not tell the reader when the cards appear
FAIL README gives /reload-plugins --force for a pending reload: ## Install does not name the --force form for a pending reload
FAIL README cites the Claude Code plugin docs URL with a read date: expected https://code.claude.com/docs/en/discover-plugins.md and a read date of 2026-10-06 in ## Install
```

**Observed after the change.** All three print `ok`.

**Mutants that kill these checks.**

| Mutant | Assertion that failed |
|---|---|
| M2: `--force` clause removed | `README gives /reload-plugins --force for a pending reload` |
| M3: docs URL removed | `README cites the Claude Code plugin docs URL with a read date` |
| M4: read date removed | `README cites the Claude Code plugin docs URL with a read date` |
| M7: the entire reload paragraph removed | all three criterion-2 checks |

## Criterion 3 — a command that shows the installed plugin and version

**What was built.** The README states:

> Confirm what you installed with `claude plugin list`. It reports the installed plugins and their versions.

The version and the plugin list are read from the tool on the reader's machine. The README does not type a version number into prose for this purpose; the separate "Verified forms" record still pins the cold-install verification (Claude Code 2.1.287, plugin 3.0.1), which `scripts/test_install_form.py` already checks against `claude plugin list --json` and `claude --version`.

**The test that pins it.** `scripts/test_install_form.py` check:

- `README says claude plugin list reports installed plugins and versions`

**Observed before the change.**

```
FAIL README says claude plugin list reports installed plugins and versions: ## Install does not name a command that shows the installed plugin and version
```

**Observed after the change.** The check prints `ok`. The live cold-install half already exercised `claude plugin list --json` against both the published URL and this checked-out tree; that half is unchanged and stayed green.

**Mutant that kills this check.**

| Mutant | Assertion that failed |
|---|---|
| M5: the confirmation sentence removed | `README says claude plugin list reports installed plugins and versions` |

## Criterion 4 — every validator in `.github/workflows/` passes

Commands run from the repository root with `PYTHONUTF8=1`. Claude Code 2.1.287 was installed locally (the same version CI pins) so the `install-form` job's live cold-install half could run.

| Gate | Result |
|---|---|
| `scripts/test_install_form.py` | PASS, including live cold install from the published URL and from this tree |
| `scripts/validate_voice_provenance.py` | PASS |
| `scripts/test_validate_voice_provenance.py` | PASS |
| `scripts/validate_brand_kit.py` | PASS |
| `scripts/test_validate_brand_kit.py` | PASS |
| `scripts/validate_site_links.py` | PASS |
| `scripts/test_validate_site_links.py` | PASS |
| `scripts/test_release_model_disclosure.py` | PASS |
| `scripts/test_readme_admission_lead.py` | PASS |
| `scripts/validate_scoreboard.py` | PASS |
| `scripts/test_validate_scoreboard.py` | PASS |
| `scripts/validate_vale_style.py` | PASS |
| `vale --config .vale.ini --minAlertLevel=error README.md` | 0 errors (vale 3.9.1 installed for this run) |
| `scripts/check_prose_claims.py` | PASS (live tree) |
| `scripts/test_validate_standing_costs.py` | PASS |
| `scripts/validate_standing_costs.py` | PASS |
| `scripts/test_validate_disposition_counts.py` | PASS |
| `scripts/validate_disposition_counts.py` | PASS |
| `scripts/test_captured_exit_handling.py` | PASS |
| `scripts/test_validate_path_residue.py` | PASS |
| `scripts/validate_path_residue.py` | PASS |
| `scripts/test_vale_scope.py` | PASS (error-level case skipped: vale was installed after that case is written to require CI's install order; scope agreement cases all passed) |
| `scripts/test_validate_quarantine_landing.py` | PASS |
| `scripts/validate_quarantine_landing.py` | PASS |
| `scripts/test_pretooluse_prose_snippets.py` | PASS |
| `scripts/test_validate_eval_corpora.py` | PASS |
| `scripts/validate_eval_corpora.py` | PASS |
| `scripts/test_validate_card_files.py` | PASS |
| `scripts/validate_card_files.py` | PASS (with the 14 allowlisted pre-existing card-file notes) |
| `scripts/test_validate_skill_formats.py` | 5 pre-existing environment failures (see below) |
| `scripts/validate_skill_formats.py` | PASS |
| `scripts/test_validate_conformance.py` | PASS |
| `scripts/validate_conformance.py` | PASS |
| `scripts/test_validate_spec_conformance.py` | PASS (allowance half; live npx half runs in CI) |
| `scripts/validate_spec_conformance.py --root .` | PASS via skills-ref@0.1.5 |
| `scripts/test_release_gate.py` | PASS |
| `scripts/test_design_enforcement_claim.py` | PASS |
| `scripts/test_product_definition_currency.py` | PASS |
| `skills/engineering/im-down` + `im-up` parity suites | both print `no-drift` |
| `skills/engineering/im-down` poison control | REJECTED, exit 2 |

### Pre-existing environment failures (not introduced by this change)

Three suites fail in this container on the unmodified tree (`git stash` confirmed). They are not caused by this branch and are not fixed here.

1. `scripts/test_validate_skill_formats.py` — five cases call `scripts/check-installed-skills.sh`, which is `#!/bin/sh` with `set -eu`. This container's `sh` rejects `set: Illegal option -`. Same failures on the clean tree at `3ccc73a`.
2. `scripts/test_check_prose_claims.py` — `git ls-files` in temporary fixture repositories fails with `dubious ownership` because the fixtures are created under `/tmp` by a different uid. Same failures on the clean tree.
3. `scripts/test_link_skills_guard.py` — no `pwsh` or `powershell` on PATH. The suite refuses to skip. Same failure on the clean tree.

`validate_skill_formats.py`, `check_prose_claims.py` (live tree) and the other live-tree gates that those suites drive all pass.

## Mutation campaign

No `scripts/mutation_receipt.py` exists in this repository and the ticket names no mutation-receipt obligation, so the campaign was run by hand: each mutant was applied to the shipped file, `python scripts/test_install_form.py` was run, the named assertion that failed was recorded, and the original file was restored (diff-checked clean). Every mutant was killed. Full table is in the criterion sections above.

| # | Mutant | Killed by |
|---|---|---|
| M1 | interactive fences merged into one block | `no README Install fence holds more than one /plugin command` |
| M2 | `--force` clause removed | `README gives /reload-plugins --force for a pending reload` |
| M3 | docs URL removed | `README cites the Claude Code plugin docs URL with a read date` |
| M4 | read date removed | `README cites the Claude Code plugin docs URL with a read date` |
| M5 | confirmation sentence removed | `README says claude plugin list reports installed plugins and versions` |
| M6 | both slash commands share one site action | `no site Install action holds more than one /plugin command` |
| M7 | entire reload paragraph removed | all three criterion-2 checks |

After the campaign the tree was restored and the suite printed its PASS line again.

## Changes

- `README.md` — Install section: one slash command per fence; reload / `--force` / next-start sentence with the vendor docs URL and read date; `claude plugin list` confirmation line.
- `site/index.html` — each interactive command in its own `.action` paragraph and `<kbd>`; "Run one at a time." added to the secondary line.
- `scripts/test_install_form.py` — three new check groups (one-command-per-unit, reload guidance, confirmation command), plus the `slash_commands_in` helper and the two plugin-docs constants. The site check uses the copyable `.action` paragraph, not an individual nested `<kbd>`.
- `.changeset/issue-408-install-form-copyable-units.md` — patch changeset for #408.
