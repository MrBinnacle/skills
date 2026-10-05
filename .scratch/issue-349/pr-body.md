# PR body — issue #349: rename CONTEXT.md to GLOSSARY.md (Pocock v1.3.1)

Parent: maintainer research ticket #403 (v1.3 migration; facts at comment 5983509597).

The skills repository's domain glossary now carries the name Pocock v1.3.1 reads. The public release gate stays green with the renamed file. Do not merge before the upgrade window ticket.

Head: `8bde70c`. Branch commits since `origin/main`: `e9ead23` (rename + live surfaces + validator list + changeset), `3bd05ef` (removed a release-brittle changeset assertion), `d9915da` (rework F1/F2: `docs/agents/domain.md` made byte-identical to the v1.3.1 template), `2d683b5` (prior scratch body, replaced by this one), `615951b` (byte-identical template check pinned in the suite), `0d760b5` (merge of `origin/main`), `8bde70c` (S513: pin `docs/agents/domain.md` to LF in `.gitattributes`).

Nine files differ from `origin/main`, as reported by `git diff --name-only origin/main...HEAD` at this head. Every path below exists in that list. Counts from `git diff --stat origin/main...HEAD` at this head: 9 files changed, 224 insertions(+), 16 deletions(-). `docs/agents/domain.md` is 2042 bytes.

- `.changeset/glossary-rename-v131.md`
- `.gitattributes`
- `AGENTS.md`
- `CLAUDE.md`
- `GLOSSARY.md`
- `PRODUCT.md`
- `docs/agents/domain.md`
- `scripts/test_validate_voice_provenance.py`
- `scripts/validate_voice_provenance.py`

## Acceptance criteria

### 1. `CONTEXT.md` renamed to `GLOSSARY.md` with `git mv`; title line updated; content otherwise unchanged.

**Built.** `git diff --stat origin/main...HEAD` records `CONTEXT.md => GLOSSARY.md` at 99% similarity — a rename, not a delete-and-add. Title line changed from `# MrBinnacle / skills` to `# GLOSSARY.md — vocabulary of record`. Every other byte of the glossary body is untouched.

**Test that pins it.** `case_glossary_renamed_from_context` in `scripts/test_validate_voice_provenance.py` asserts three things against the live tree: `GLOSSARY.md` exists at the repo root, `CONTEXT.md` is gone from the repo root, and the title line starts with `# ` and names the glossary.

**Before / after.** On `origin/main` the live file is `CONTEXT.md` and the title is `# MrBinnacle / skills`; the three checks would fail there. At this head, observed: `ok GLOSSARY.md exists at the repo root`, `ok CONTEXT.md is gone from the repo root`, `ok GLOSSARY.md title line names the glossary`.

### 2. `docs/agents/domain.md` replaced with the v1.3.1 setup template; nothing kept.

**Built.** `docs/agents/domain.md` is byte-identical to the v1.3.1 template inlined in the ticket (`github.com/mattpocock/skills` at tag `v1.3.1`, `skills/engineering/setup-matt-pocock-skills/domain.md`). This repository's base file was the v1.2.3 template with no local additions, so nothing is kept. `GLOSSARY-MAP.md` replaces `CONTEXT-MAP.md`, and the v1.3.1 punctuation replaces the v1.2.3 em-dashes. Measured at this head: 2042 bytes, equal to the inlined fixture.

**Test that pins it.** `case_domain_md_is_v131_template` stores the v1.3.1 template as the `V131_DOMAIN_TEMPLATE` fixture and asserts exact byte equality. The test's docstring does not call upstream text "local additions".

**Before / after.** Watched fail at `3bd05ef` (prior build): `FAIL domain.md is byte-identical to the v1.3.1 template: content differs from the inlined v1.3.1 fixture`, first difference at line 8 — the file still carried `` - **`CONTEXT-MAP.md`** … it points at one `GLOSSARY.md` per context…`` where the template has `` - **`GLOSSARY-MAP.md`** …: it points at one `GLOSSARY.md` per context…``. After the rewrite at `d9915da` and re-verified at this head: `ok domain.md is byte-identical to the v1.3.1 template`.

### 3. Live instruction surfaces name `GLOSSARY.md`; dated records and quarantined example text stay as written.

**Built.** The three surfaces the ticket named, at the measured lines:

| Surface | Line | Change |
|---|---|---|
| `CLAUDE.md` | 45 | `CONTEXT.md` → `GLOSSARY.md` |
| `AGENTS.md` | 245 | `CONTEXT.md` → `GLOSSARY.md` |
| `PRODUCT.md` | 187 | `CONTEXT.md` → `GLOSSARY.md` |

A sweep of tracked `*.md` files outside `CHANGELOG.md`, `docs/adr/`, `_quarantine/`, `.changeset/` and `RETIRED.md` found no other live instruction surface naming `CONTEXT.md`.

**Left as written (dated records and quarantined example text):**

- `CHANGELOG.md` — release notes describing what `CONTEXT.md` did on those dates.
- `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` lines 64, 68 — the ADR's own historical account.
- `_quarantine/cwd-drift/SKILL.md` — quarantined card example text, part of the recorded incident.

**Test that pins it.** `case_live_instruction_surfaces_name_glossary` asserts each of `CLAUDE.md`, `AGENTS.md` and `PRODUCT.md` names `GLOSSARY.md` and no longer names `CONTEXT.md`. It deliberately does not scan CHANGELOG, ADR 0003 or the quarantine tree.

**Before / after.** On `origin/main` those three files name `CONTEXT.md`; six checks would fail there. At this head, all six pass.

### 4. `scripts/validate_voice_provenance.py` lists `GLOSSARY.md`; its tests pass; a test fails if the list names a file absent from the tree.

**Built.** `SHIPPED_SURFACES` in `scripts/validate_voice_provenance.py` line 105: `"CONTEXT.md"` → `"GLOSSARY.md"`. `EVIDENCE.md` stays on the list — a per-card filename that ships under `skills/`, resolved by glob.

**Tests that pin it.**

- `case_shipped_surfaces_list_names_existing_files` — imports `SHIPPED_SURFACES` from the gate module and fails if any listed name resolves to no file. Also asserts the list contains `GLOSSARY.md` and does not contain `CONTEXT.md`.
- `case_absent_listed_surface_is_caught` — poison control. Builds a set containing `NO-SUCH-SURFACE-349.md` and asserts the same existence check reports exactly that name.

**Before / after.** On `origin/main` the list still says `CONTEXT.md`; at this head: `ok every name in SHIPPED_SURFACES exists in the tree`, `ok SHIPPED_SURFACES lists GLOSSARY.md`, `ok SHIPPED_SURFACES no longer lists CONTEXT.md`, `ok an absent listed surface is reported as missing`. The poison control passed before and after — it pins the check, not the rename.

### 5. A changeset announces the rename; `release_gate.py` passes; CI is green.

**Built.** `.changeset/glossary-rename-v131.md` — minor bump on `mrbinnacle-skills`, body naming the rename, the v1.3.1 reason, the surfaces updated, and the dated-record carve-out.

**Gate.** `python scripts/release_gate.py` at this head → `RELEASE GATE: PASS - surfaces healthy at version 3.0.1: plugin versions in lockstep with package.json, release plan assembles, changelog section dated.`

**Local gate set at this head** (the validator and suite commands `.github/workflows/tests.yml` runs, all PASS unless noted):

| Command | Result |
|---|---|
| `python scripts/validate_voice_provenance.py` | PASS |
| `python scripts/test_validate_voice_provenance.py` | PASS (60 cases) |
| `python scripts/release_gate.py` | PASS |
| `python scripts/validate_card_files.py` | PASS |
| `python scripts/validate_scoreboard.py` | PASS |
| `python scripts/test_readme_admission_lead.py` | PASS |
| `python scripts/validate_eval_corpora.py` | PASS |
| `python scripts/test_validate_eval_corpora.py` | PASS |
| `python scripts/validate_skill_formats.py` | PASS |
| `python scripts/validate_vale_style.py` | PASS |
| `python scripts/test_validate_vale_style.py` | PASS |
| `python scripts/validate_brand_kit.py` | PASS |
| `python scripts/validate_path_residue.py` | PASS |
| `python scripts/test_validate_path_residue.py` | PASS |
| `python scripts/validate_disposition_counts.py` | PASS |
| `python scripts/test_validate_disposition_counts.py` | PASS |
| `python scripts/validate_standing_costs.py` | PASS |
| `python scripts/test_validate_standing_costs.py` | PASS |
| `python scripts/check_prose_claims.py` | PASS |
| `python scripts/validate_site_links.py` | PASS |
| `python scripts/test_validate_site_links.py` | PASS |
| `python scripts/test_validate_spec_conformance.py` | PASS (live npx run deferred to CI) |
| `python scripts/test_release_model_disclosure.py` | PASS |
| `python scripts/test_captured_exit_handling.py` | PASS |
| `python scripts/test_vale_scope.py` | PASS |
| `python scripts/test_design_enforcement_claim.py` | PASS |
| `python scripts/test_validate_vale_style.py` | PASS (also pins that `.gitattributes` still carries `styles/** text eol=lf`) |

This repository's GitHub workflows name no lint or type tool. Several long-running suite cells (`test_release_gate.py`, `test_validate_conformance.py`, `test_check_prose_claims.py`, `test_validate_skill_formats.py`, `test_validate_brand_kit.py`) intermittently exceed a local subprocess timeout in this container; the same suites are unchanged from `origin/main` and the standalone validators they wrap all PASS here.

**CI run URL.** This container has no GitHub token and no network, so the Actions run URL for `validator (windows-latest)` cannot be fetched or recorded here. The code change that made that cell red is fixed (see criterion 7); the local Windows-equivalent check is recorded below. The runner/harness attaches the CI result after push.

### 6. Do not merge before the upgrade window ticket.

Constraint, not a build item. The PR stays open; merge is gated on the upgrade window ticket.

### 7. S513 rework: `validator (windows-latest)` was red on the byte-identical template check; pin the file's line endings.

**Built.** `.gitattributes` now carries, with a one-line comment naming the exact-bytes test:

```
docs/agents/domain.md text eol=lf
```

The comment sits beside the existing `styles/**` and `scripts/vendor/**` eol pins, which solve the same class of problem for hash-pinned files. The byte comparison in `case_domain_md_is_v131_template` is unchanged.

**Test that pins it.** `case_domain_md_is_v131_template` still compares `docs/agents/domain.md` byte-for-byte to `V131_DOMAIN_TEMPLATE`. With a CRLF worktree copy that check reds. `test_validate_vale_style.py` separately asserts the `styles/** text eol=lf` pin is still present, so this change cannot silently drop the older rule.

**Before / after — Windows simulation.**

Before the pin, a CRLF copy of `docs/agents/domain.md` was written into the worktree (what a Windows checkout with `core.autocrlf=true` produces when no eol rule is set). Observed:

```
FAIL domain.md is byte-identical to the v1.3.1 template: content differs from the inlined v1.3.1 fixture
FAIL domain.md first difference is named: line 1: file='# Domain Docs\r\n' template='# Domain Docs\n'
```

`python scripts/test_validate_voice_provenance.py` exited 1.

After the pin, the ticket's exact sequence was run at this head:

```
git -c core.autocrlf=true checkout -- docs/agents/domain.md
python scripts/test_validate_voice_provenance.py
```

Result: the checkout kept the file at 2042 bytes with zero CRLF (`git check-attr -a docs/agents/domain.md` reports `text: set`, `eol: lf`). The suite printed `ok domain.md is byte-identical to the v1.3.1 template` and exited 0 with `PASS: voice-provenance suite, all cases correct`. A stronger local simulation, `git -c core.autocrlf=true -c core.eol=crlf checkout -- docs/agents/domain.md`, also kept the file pure LF and the suite green — the attributes rule overrides both `core.autocrlf` and `core.eol`.

**Before / after — this run's only tree edit.** Before `8bde70c`, `.gitattributes` had no rule for `docs/agents/domain.md` and a CRLF worktree copy failed the suite (exit 1, two FAIL lines above). After `8bde70c`, the pin is in place, the Windows-equivalent checkout keeps LF, and the suite passes.

## Which test covers which criterion

| Criterion | Test / gate | Other pin |
|---|---|---|
| 1 rename | `case_glossary_renamed_from_context` | `git diff --stat` rename record |
| 2 domain.md = v1.3.1 template | `case_domain_md_is_v131_template` | fixture `V131_DOMAIN_TEMPLATE` |
| 3 live surfaces | `case_live_instruction_surfaces_name_glossary` | — |
| 4 validator list + existence | `case_shipped_surfaces_list_names_existing_files`, `case_absent_listed_surface_is_caught` | — |
| 5 changeset + gate + CI | — (changeset file is the artifact) | `release_gate.py`; local gate set above |
| 6 merge constraint | — | — |
| 7 LF pin for the byte check | `case_domain_md_is_v131_template` under a CRLF worktree | `.gitattributes`; `test_validate_vale_style.py` styles-pin case |
