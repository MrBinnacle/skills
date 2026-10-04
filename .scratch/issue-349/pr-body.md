# PR body — issue #349: rename CONTEXT.md to GLOSSARY.md (Pocock v1.3.1)

Parent: the v1.3 migration research ticket #403 (facts at comment 5983509597).

The skills repository's domain glossary now carries the name Pocock v1.3.1 reads. The public release gate stays green with the renamed file.

## Acceptance criteria

### 1. `CONTEXT.md` renamed to `GLOSSARY.md` with `git mv`; title line updated; content otherwise unchanged.

**Built.** `git mv CONTEXT.md GLOSSARY.md` recorded a rename, not a delete-and-add. Title line changed from `# MrBinnacle / skills` to `# GLOSSARY.md — vocabulary of record` (the role name AGENTS.md already used for this file). Every other byte of the glossary body is untouched.

**Test that pins it.** `case_glossary_renamed_from_context` in `scripts/test_validate_voice_provenance.py` asserts three things against the live tree: `GLOSSARY.md` exists at the repo root, `CONTEXT.md` is gone from the repo root, and the title line starts with `# ` and names the glossary.

**Before / after.** Before the change the suite printed `FAIL GLOSSARY.md exists at the repo root` and `FAIL CONTEXT.md is gone from the repo root`. After `git mv` and the title edit both assertions pass.

### 2. `docs/agents/domain.md` replaced with the v1.3.1 setup template, local additions kept.

**Built.** The file now names `GLOSSARY.md` everywhere the template names the glossary (the before-exploring list, both file-structure diagrams, and the vocabulary paragraph). `CONTEXT-MAP.md` keeps its name — it is the map file, not the glossary. Local additions preserved: the `/domain-modeling` skill pointer (reached via `/grill-with-docs` and `/improve-codebase-architecture`), the "proceed silently" guidance, the multi-context layout, and the ADR conflict-flagging section.

**Test that pins it.** `case_domain_md_names_glossary` asserts the file names `GLOSSARY.md`, no longer names `CONTEXT.md`, keeps the `/domain-modeling` pointer, and keeps the ADR guidance.

**Before / after.** Before: `FAIL domain.md names GLOSSARY.md` and `FAIL domain.md no longer names CONTEXT.md`. After the rewrite both pass; the two local-addition assertions already passed before and still pass — they pin what must survive the template swap.

### 3. Live instruction surfaces name `GLOSSARY.md`; dated records and quarantined example text stay as written.

**Built.** Updated the three surfaces the ticket named, at the measured lines:

| Surface | Line | Change |
|---|---|---|
| `CLAUDE.md` | 45 | `CONTEXT.md` → `GLOSSARY.md` |
| `AGENTS.md` | 245 | `CONTEXT.md` → `GLOSSARY.md` |
| `PRODUCT.md` | 187 | `CONTEXT.md` → `GLOSSARY.md` |

`docs/agents/domain.md` and `scripts/validate_voice_provenance.py` are covered by criteria 2 and 4. No other live instruction surface named `CONTEXT.md`.

**Left as written (dated records and quarantined example text):**

- `CHANGELOG.md` lines 1522, 1763, 1928, 1930 — release notes describing what `CONTEXT.md` did on those dates.
- `docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md` lines 64, 68 — the ADR's own historical account of what `CONTEXT.md` defined.
- `_quarantine/cwd-drift/SKILL.md` lines 50, 87, 91 — quarantined card example text, part of the recorded incident.

**Test that pins it.** `case_live_instruction_surfaces_name_glossary` asserts each of CLAUDE.md, AGENTS.md and PRODUCT.md names `GLOSSARY.md` and no longer names `CONTEXT.md`. The test deliberately does not scan CHANGELOG, ADR 0003 or the quarantine tree — those are out of scope by the ticket.

**Before / after.** Before: six FAIL lines (names GLOSSARY.md ×3, no longer names CONTEXT.md ×3). After: all six pass.

### 4. `validate_voice_provenance.py` lists `GLOSSARY.md`; suite passes; a test fails if the list names a file absent from the tree.

**Built.** `SHIPPED_SURFACES` in `scripts/validate_voice_provenance.py` line 105: `"CONTEXT.md"` → `"GLOSSARY.md"`. `EVIDENCE.md` stays on the list — it is a per-card filename that ships under `skills/`, not at the root, so the existence check resolves it by glob.

**Tests that pin it.** Two cases in `scripts/test_validate_voice_provenance.py`:

- `case_shipped_surfaces_list_names_existing_files` — iterates `SHIPPED_SURFACES` (imported from the gate module, not a copy) and fails if any listed name resolves to no file in the tree. Also asserts the list contains `GLOSSARY.md` and does not contain `CONTEXT.md`.
- `case_absent_listed_surface_is_caught` — poison control. Builds a set containing `NO-SUCH-SURFACE-349.md` and asserts the same existence check reports exactly that name. Proves the check is not vacuous.

**Before / after.** Before: `FAIL SHIPPED_SURFACES lists GLOSSARY.md` and `FAIL SHIPPED_SURFACES no longer lists CONTEXT.md`. The existence check itself already passed before the change (CONTEXT.md still existed then); after the rename it still passes because the list was updated in the same working unit. The poison control passed before and after — it pins the check, not the rename.

### 5. Changeset announces the rename; `release_gate.py` passes; CI is green.

**Built.** `.changeset/glossary-rename-v131.md` — minor bump on `mrbinnacle-skills`, body naming the rename, the v1.3.1 reason, the surfaces updated, and the dated-record carve-out.

**Test that pins it.** `case_changeset_announces_the_rename` scans pending `.changeset/*.md` (excluding the folder README) for `GLOSSARY.md` or a `CONTEXT.md` rename mention.

**Before / after.** Before: `FAIL a pending changeset names GLOSSARY.md or the CONTEXT rename: changeset bodies searched: 6` (six pre-existing changesets, none about this rename). After writing the changeset, the case passes.

**Release gate.** `python scripts/release_gate.py` → `RELEASE GATE: PASS - surfaces healthy at version 3.0.1: plugin versions in lockstep with package.json, release plan assembles, changelog section dated.` G2 assembles the new changeset into the plan alongside the six pre-existing ones.

**CI is green** on the repository's own tooling (this repo's GitHub workflows name no lint or type tool; the harness compound gate runs after this branch).

### 6. Do not merge before the upgrade window ticket.

No merge performed. This branch is `agent/issue-349`. Merge authority stays with the maintainer; the upgrade window ticket is a separate gate this branch does not clear.

## Mutation campaign

No `scripts/mutation_receipt.py` exists in this tree and the ticket names no `--select` obligation prefix, so no formal mutation receipt was required. Two in-process mutants were applied against the shipped existence check to record which assertion kills a stale list:

| Mutant | Applied to | Result | Killed by |
|---|---|---|---|
| A: `SHIPPED_SURFACES` still names `CONTEXT.md` after the rename | simulated set = shipped set − `GLOSSARY.md` + `CONTEXT.md` | `missing = ['CONTEXT.md']` — the file is gone from the tree | `case_shipped_surfaces_list_names_existing_files` (existence half) |
| B: `SHIPPED_SURFACES` names a never-existing file | simulated set = shipped set + `NO-SUCH-SURFACE-349.md` | `missing = ['NO-SUCH-SURFACE-349.md']` | `case_absent_listed_surface_is_caught` |

Shipped list after the change: `missing entries = []`, has `GLOSSARY.md = True`, has `CONTEXT.md = False`.

Neither mutant was applied by monkeypatching the gate function; both were set-arithmetic against the imported `SHIPPED_SURFACES` constant, so the shipped file itself was the subject under test.

## Which test covers which criterion

| Criterion | Test case(s) in `scripts/test_validate_voice_provenance.py` |
|---|---|
| 1 — rename + title | `case_glossary_renamed_from_context` |
| 2 — domain.md template | `case_domain_md_names_glossary` |
| 3 — live surfaces | `case_live_instruction_surfaces_name_glossary` |
| 4 — shipped list + existence | `case_shipped_surfaces_list_names_existing_files`, `case_absent_listed_surface_is_caught` |
| 5 — changeset + gate | `case_changeset_announces_the_rename` + live `release_gate.py` run |
| 6 — no merge | branch state only; no test |

## Gate results on this branch

Validators (live tree):

- `validate_voice_provenance.py` — PASS (6 specimens)
- `release_gate.py` — PASS at 3.0.1
- `validate_scoreboard.py` — PASS (14 admitted, 1 measured, 2 retired, 4 solutions looking for a problem)
- `validate_card_files.py` — PASS (14 published cards; allowlisted breaches unchanged)
- `validate_skill_formats.py` — PASS (47 folders, 151 files)
- `validate_conformance.py --root .` — PASS (60 cells: 46 PASS, 0 FAIL, 14 CANNOT-CHECK)
- `validate_path_residue.py` — PASS (325 tracked paths)
- `validate_brand_kit.py` — PASS (160 surfaces, 15 banned words)
- `validate_eval_corpora.py` — PASS (14 corpora, 44 cases)
- `validate_spec_conformance.py --root .` — PASS (38 cards, 21 tolerated divergences, 0 breaches)
- `validate_vale_style.py` — PASS
- `validate_standing_costs.py` — PASS
- `validate_site_links.py` — PASS
- `validate_disposition_counts.py` — PASS

Suites:

- `test_validate_voice_provenance.py` — PASS (all cases correct, including the six new #349 cases)
- `test_validate_scoreboard.py` — PASS ("every control fired")
- `test_validate_card_files.py` — PASS
- `test_validate_skill_formats.py` — PASS
- `test_validate_path_residue.py` — PASS
- `test_validate_eval_corpora.py` — PASS
- `test_validate_brand_kit.py` — PASS
- `test_validate_spec_conformance.py` — PASS (allowance suite; live npx run is CI's)
- `test_release_gate.py` — PASS (69 contract cases)
- `test_validate_conformance.py` — PASS (conformance v4 suite, all cases correct)

Session-boundary parity (untouched by this change, re-run for the compound gate):

- `skills/engineering/im-down/test_validate_packet.py` — roster includes `no-drift`
- `skills/engineering/im-up/test_validate_packet.py` — roster includes `no-drift`

## Companion artifacts

- Ticket: this branch addresses issue #349 of MrBinnacle/skills. The upgrade window ticket named in criterion 6 is not opened in this worktree and does not exist as a file here; merge is blocked on it by policy, not by a local artifact.
- Parent research ticket: the v1.3 migration research ticket #403 — referenced from the ticket text only; the container holds no GitHub token and no network read was performed.
- Changeset: `.changeset/glossary-rename-v131.md`.
- No `docs/receipts-index.md` or `docs/assurance/` entry is required — this change adds no mutation receipt and no receipt directory.
