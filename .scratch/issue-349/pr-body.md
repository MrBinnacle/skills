# PR body — issue #349: rename CONTEXT.md to GLOSSARY.md (Pocock v1.3.1)

Parent: maintainer research ticket #403 (v1.3 migration; facts at comment 5983509597).

The skills repository's domain glossary now carries the name Pocock v1.3.1 reads. The public release gate stays green with the renamed file. Do not merge before the upgrade window ticket.

Head: `d9915da`. Branch holds three commits: `e9ead23` (rename + live surfaces + validator list + changeset), `3bd05ef` (removed a release-brittle changeset assertion and the prior scratch body), `d9915da` (rework F1/F2: `docs/agents/domain.md` made byte-identical to the v1.3.1 template, test repaired to pin exact equality).

Eight files differ from `origin/main`, as reported by `git diff --name-only origin/main...HEAD` at this head:

- `.changeset/glossary-rename-v131.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GLOSSARY.md`
- `PRODUCT.md`
- `docs/agents/domain.md`
- `scripts/test_validate_voice_provenance.py`
- `scripts/validate_voice_provenance.py`

## Acceptance criteria

### 1. `CONTEXT.md` renamed to `GLOSSARY.md` with `git mv`; title line updated; content otherwise unchanged.

**Built.** `git mv CONTEXT.md GLOSSARY.md` recorded a rename, not a delete-and-add (`git diff --stat origin/main...HEAD` shows `CONTEXT.md => GLOSSARY.md`, 99% similarity). Title line changed from `# MrBinnacle / skills` to `# GLOSSARY.md — vocabulary of record`. Every other byte of the glossary body is untouched.

**Test that pins it.** `case_glossary_renamed_from_context` in `scripts/test_validate_voice_provenance.py` asserts three things against the live tree: `GLOSSARY.md` exists at the repo root, `CONTEXT.md` is gone from the repo root, and the title line starts with `# ` and names the glossary.

**Before / after.** Before the rename (on `origin/main`) the suite printed `FAIL GLOSSARY.md exists at the repo root` and `FAIL CONTEXT.md is gone from the repo root` — the live file was `CONTEXT.md`. After `git mv` and the title edit, observed at this head: `ok GLOSSARY.md exists at the repo root`, `ok CONTEXT.md is gone from the repo root`, `ok GLOSSARY.md title line names the glossary`.

### 2. `docs/agents/domain.md` replaced with the v1.3.1 setup template; nothing kept.

**Built.** `docs/agents/domain.md` is byte-identical to the v1.3.1 template inlined in the ticket (`github.com/mattpocock/skills` at tag `v1.3.1`, `skills/engineering/setup-matt-pocock-skills/domain.md`). This repository's base file was the v1.2.3 template with no local additions, so nothing is kept. `GLOSSARY-MAP.md` replaces `CONTEXT-MAP.md`, and the v1.3.1 punctuation (colons after `exists` and after `` `docs/adr/` ``, comma after `(event-sourced orders)`, colon after `signal`) replaces the v1.2.3 em-dashes. Measured at this head: `docs/agents/domain.md` is 2042 bytes, 51 lines, equal to the inlined fixture.

**Test that pins it.** `case_domain_md_is_v131_template` in `scripts/test_validate_voice_provenance.py` stores the v1.3.1 template as the `V131_DOMAIN_TEMPLATE` fixture and asserts exact byte equality. A substring check would pass on a v1.2.3-shaped file that merely renamed `CONTEXT.md` to `GLOSSARY.md`; exact equality reds on both the stale map-file name and the stale punctuation. The test's docstring does not call upstream text "local additions".

**Before / after.** Watched fail at `3bd05ef` (the prior build): `FAIL domain.md is byte-identical to the v1.3.1 template: content differs from the inlined v1.3.1 fixture`, with the first difference named at line 8 — file had `` - **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `GLOSSARY.md` per context…`` where the template has `` - **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one `GLOSSARY.md` per context…``. After the rewrite, observed at this head: `ok domain.md is byte-identical to the v1.3.1 template`.

### 3. Live instruction surfaces name `GLOSSARY.md`; dated records and quarantined example text stay as written.

**Built.** The three surfaces the ticket named, at the measured lines:

| Surface | Line | Change |
|---|---|---|
| `CLAUDE.md` | 45 | `CONTEXT.md` → `GLOSSARY.md` |
| `AGENTS.md` | 245 | `CONTEXT.md` → `GLOSSARY.md` |
| `PRODUCT.md` | 187 | `CONTEXT.md` → `GLOSSARY.md` |

A sweep of tracked `*.md` files outside `CHANGELOG.md`, `docs/adr/`, `_quarantine/`, `.changeset/` and `RETIRED.md` found no other live instruction surface naming `CONTEXT.md`. `docs/agents/domain.md` is covered by criterion 2.

**Left as written (dated records and quarantined example text):**

- `CHANGELOG.md` — release notes describing what `CONTEXT.md` did on those dates.
- `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` lines 64, 68 — the ADR's own historical account.
- `_quarantine/cwd-drift/SKILL.md` — quarantined card example text, part of the recorded incident.

**Test that pins it.** `case_live_instruction_surfaces_name_glossary` asserts each of `CLAUDE.md`, `AGENTS.md` and `PRODUCT.md` names `GLOSSARY.md` and no longer names `CONTEXT.md`. The test deliberately does not scan CHANGELOG, ADR 0003 or the quarantine tree — those are out of scope by the ticket.

**Before / after.** Before the rename, on `origin/main`: six FAIL lines (names `GLOSSARY.md` ×3, no longer names `CONTEXT.md` ×3). After: all six pass, observed at this head.

### 4. `scripts/validate_voice_provenance.py` lists `GLOSSARY.md`; its tests pass; a test fails if the list names a file absent from the tree.

**Built.** `SHIPPED_SURFACES` in `scripts/validate_voice_provenance.py` line 105: `"CONTEXT.md"` → `"GLOSSARY.md"`. `EVIDENCE.md` stays on the list — it is a per-card filename that ships under `skills/`, not at the root, so the existence check resolves it by glob.

**Tests that pin it.** Two cases in `scripts/test_validate_voice_provenance.py`:

- `case_shipped_surfaces_list_names_existing_files` — iterates `SHIPPED_SURFACES` (imported from the gate module, not a copy) and fails if any listed name resolves to no file in the tree. Also asserts the list contains `GLOSSARY.md` and does not contain `CONTEXT.md`.
- `case_absent_listed_surface_is_caught` — poison control. Builds a set containing `NO-SUCH-SURFACE-349.md` and asserts the same existence check reports exactly that name. Proves the check is not vacuous.

**Before / after.** Before the rename, on `origin/main`: `FAIL SHIPPED_SURFACES lists GLOSSARY.md` and `FAIL SHIPPED_SURFACES no longer lists CONTEXT.md`. The existence check itself passed before the change — `CONTEXT.md` still existed then. After the rename the list was updated in the same working unit, so it still passes: observed at this head, `ok every name in SHIPPED_SURFACES exists in the tree`, `ok SHIPPED_SURFACES lists GLOSSARY.md`, `ok SHIPPED_SURFACES no longer lists CONTEXT.md`, `ok an absent listed surface is reported as missing`. The poison control passed before and after — it pins the check, not the rename.

### 5. A changeset announces the rename; `release_gate.py` passes; CI is green.

**Built.** `.changeset/glossary-rename-v131.md` — minor bump on `mrbinnacle-skills`, body naming the rename, the v1.3.1 reason, the surfaces updated, and the dated-record carve-out.

**Tests and gate.** `python scripts/release_gate.py` at this head → `RELEASE GATE: PASS - surfaces healthy at version 3.0.1: plugin versions in lockstep with package.json, release plan assembles, changelog section dated.` The release plan assembles the new changeset alongside the pre-existing ones. `python scripts/test_release_gate.py` → `PASS: release gate verified across 69 contract case(s)`.

The full voice-provenance suite at this head: `python scripts/test_validate_voice_provenance.py` → `PASS: voice-provenance suite, all cases correct` (60 cases, 0 failures). A changeset-assertion case was removed in `3bd05ef` because scanning pending changesets is release-brittle; the changeset file itself remains and `release_gate.py` assembles it.

**CI is green on the repository's own tooling.** This repo's GitHub workflows name no lint or type tool. The gate set run at this head, all PASS: `validate_card_files.py` + suite, `validate_scoreboard.py` + `test_readme_admission_lead.py`, `validate_eval_corpora.py` + suite, `validate_skill_formats.py` + suite, `validate_voice_provenance.py` + suite, `validate_brand_kit.py` + suite, `validate_conformance.py --root .` + suite, `validate_spec_conformance.py` + suite, `release_gate.py` + suite, `validate_path_residue.py` + suite, `validate_disposition_counts.py` + suite, `validate_standing_costs.py` + suite, `validate_site_links.py` + suite, `check_prose_claims.py` + suite, `test_captured_exit_handling.py`, `test_vale_scope.py`, `test_validate_vale_style.py`, `test_release_model_disclosure.py`. The harness compound gate runs after this branch.

### 6. Do not merge before the upgrade window ticket.

Constraint, not a build item. The PR stays open; merge is gated on the upgrade window ticket.

## Which test covers which criterion

| Criterion | Test in `scripts/test_validate_voice_provenance.py` | Other pin |
|---|---|---|
| 1 rename | `case_glossary_renamed_from_context` | — |
| 2 domain.md = v1.3.1 template | `case_domain_md_is_v131_template` | fixture `V131_DOMAIN_TEMPLATE` |
| 3 live surfaces | `case_live_instruction_surfaces_name_glossary` | — |
| 4 validator list + existence | `case_shipped_surfaces_list_names_existing_files`, `case_absent_listed_surface_is_caught` | — |
| 5 changeset + gate + CI | — (changeset file is the artifact) | `release_gate.py`, full gate set |
| 6 merge constraint | — | — |
