# Evidence body — issue #327

**Branch:** `agent/issue-327`
**Ticket:** MrBinnacle/skills #327 — gotchas convention after the S496 Fable adjudication
**Scope:** first tranche only — strike the always-load reading, require a when-to-open pointer on every published `SKILL.md`, allow dated status lines under entries, gate the pointer in `validate_card_files.py`.

Companion artifacts named in this body:

| Artifact | Where it lives |
|---|---|
| This ticket | `MrBinnacle/skills#327` |
| Rule screen for "gotchas.md is read during use" | `docs/rule-screens.md`, section `2026-10-01` (this repository) |
| S496 read classification (1,141 transcripts) | the maintainer's research repository at `docs/audit/gotchas-readrate-S495/read-classification-S496.md` |
| S496 cross-family adjudication | the maintainer's research repository at `docs/research/gotchas-convention-adjudication-S496.md` |
| S496 cross-family receipt | the maintainer's research repository at `docs/audit/t1-gotchas-S496/` |
| Pointer-check gate | `scripts/validate_card_files.py`, rule kind `gotchas_pointer` |
| Pointer-check suite | `scripts/test_validate_card_files.py` |
| Guard-carried status lines | `skills/engineering/pull-rebase/gotchas.md`, `skills/orchestration/decision-rights/gotchas.md` |

The research-repository paths above are cited without the repository's local name because the de-personalization gate refuses that term in `*.md` files; the paths are the checkable part. The `~/.claude` global rule text is out of scope (claude-config ticket) and was not touched.

---

## Criterion 1 — `AGENTS.md` convention text updated

**What was built.** Two surfaces in `AGENTS.md`:

1. **Per-skill layout line.** Appended: the `gotchas.md` sibling is the append-only ledger reached on a context pointer from `SKILL.md`; it is not part of the card's always-loaded surface, and nothing that must fire rests on it being read.
2. **`gotchas.md is required` rule.** Rewritten in three movements: what the file is (append-only ledger and promotion history, OBSERVED + ANTICIPATED entries plus dated status lines); how it is reached (opened on a pointer, every published `SKILL.md` carries one when-to-open pointer; measured 4 of 14 named it at all on 2026-09-30; S496 zero in-use opens across 1,141 transcripts, screen in `docs/rule-screens.md`); what does not rest on it (no discipline that must fire — hook backing lives in the adopter's environment). The status-line vocabulary is documented under the same append-only rule: `promoted: description` / `promoted: body` / `promoted: hook` (naming the guard) / `retired`. The gate sentence names `scripts/validate_card_files.py` as the check.

**Test that pins it.** No automated test grades convention prose — that is a judgement row in `docs/rule-screens.md`'s own gated/judgement table. The pin is the companion gate on criterion 4: `validate_card_files.py` now refuses a card without the pointer the convention requires, so the convention's operative clause cannot rot silently. Residue gate ran on every commit and passed; the research repository's local name is blocked in `*.md` files, so citations use the research-repository path form.

**Observed before/after.** Before: the rule said "append-only log of OBSERVED + ANTICIPATED failure modes" with no statement of how the file is reached, and the layout line listed it among sibling files with no reach qualifier. After: both surfaces state the pointer contract, the measured zero, and the no-must-fire-rests-on-it clause.

---

## Criterion 2 — `docs/rule-screens.md` carries the dated screen

**What was built.** A new dated section, `2026-10-01 — gotchas.md is read during use: REVISE, on a measured zero`, appended after the 2026-09-06 section (screens are never rewritten; a correction is a new entry). It records:

- the rule under screen (the prior always-load reading);
- the measurement: S496 read classification over **1,141 transcripts, 2026-08-30 to 2026-09-30**, **zero** model-emitted reads of any published card's `gotchas.md` followed a Skill invocation of that card in the same transcript — **measured, not `UNMEASURED`**;
- the same-date pointer-surface count: 4 of 14 published `SKILL.md` files named their `gotchas.md` at all;
- the disposition: `REVISE`, class `model-execution` + `repository-integrity`;
- the cross-family adjudication paths (above);
- what the zero does **not** establish (no lift claim; paired with-vs-without is out of scope and pre-registered separately);
- the revisit condition: rerun `classify_reads.py` on the next hundred transcripts; if it still shows zero in-use opens on invoked cards, the pointer requirement is falsified and the convention narrows to the label fix alone.

The "Which rules are gated" table gained a row: every published `SKILL.md` carries a when-to-open pointer to its `gotchas.md` — **Gated** by `scripts/validate_card_files.py` (skills#327).

**Test that pins it.** Same judgement surface as criterion 1; the gate is the validator row. The screen's count and paths are checkable against the named research-repository artifacts.

**Observed before/after.** Before: the only `gotchas.md` screen was the 2026-09-06 `REVISE` on the replace-versus-supplement contradiction; nothing screened whether the file is read during use. After: a measured zero is on the record with its instrument, corpus size, date window, and path.

---

## Criterion 3 — every published `SKILL.md` names its `gotchas.md` with a when-to-open pointer

**What was built.** Thirteen cards gained one context pointer. `closure-mode` already carried a qualifying pointer on its ship-criteria line ("recognize the failure modes in [gotchas.md](gotchas.md) **before** they happen") and was left unchanged. Pointers added:

| Card | Pointer (abridged) |
|---|---|
| `clirunner-env` | Open gotchas.md when a CLI test silently passed on a branch that never ran the absent-env path. |
| `halt-as-deliverable` | Open gotchas.md when a pre-flight gate refuses to produce your deliverable and you are about to treat the HALT as a setback. |
| `im-down` | Open gotchas.md when a close was skipped, a packet went missing, or the receiver rejects a packet this producer just wrote. |
| `im-up` | Open gotchas.md when a packet arrives and you are about to trust its claims without re-deriving them. |
| `mocked-stub` | Open gotchas.md when a returned implementation reports all gates green and the branch's safety helper looks patched in the test. |
| `pretooluse-prose` | Open gotchas.md when a Bash guard blocks its own install, a commit message, or a heredoc body. |
| `pull-rebase` | Open gotchas.md when `git config pull.rebase` may be `true`, or when a guard you installed blocks a command that merely names this skill. |
| `stale-deploy` | Open gotchas.md when a deploy poll exits instantly on content that pre-dated the deploy, or a `sleep && curl` chain is blocked. |
| `vacuous-check` | Replaced the bare `see \`gotchas.md\`` mention with a when-to-open pointer on the same Notes bullet. |
| `dead-predicate` | Open gotchas.md when a router rule matches nothing you type, or when a per-rule suite is green and you suspect a dead pattern. |
| `decision-rights` | Open gotchas.md when a handoff carries blanket "do not re-litigate" framing, or when a hook catch needs classifying as a known negative. |
| `disposition-schema` | Open gotchas.md when consolidator renumbering drops a seat-local finding ID, or before choosing a namespace strategy. |
| `subagent-handback` | Open gotchas.md when a research handback arrives empty, or when a claim survives citation-check but fails a re-run. |

**Test that pins it.** `case_live_cards_carry_gotchas_pointers` in `scripts/test_validate_card_files.py`. It runs the real checker entrypoint against the live tree (external behaviour) **and** independently asserts, against each published card's own `SKILL.md` text, that some line carries a markdown link to `gotchas.md` plus a when-to-open cue — written as a separate regex from the checker's, so a checker that goes soft cannot pass alone. The count is derived from `find_cards`, never pinned as a literal.

**Observed before/after.**

- **Before the change, watching the test fail for the right reason:** the independent live assertion listed 13 cards missing a when-to-open pointer (`closure-mode` was the only card that already qualified). The checker entrypoint was still green at that moment for the pointer predicate, because the check did not exist yet — which is exactly the gap the independent assertion closes.
- **After pointers landed and the check was wired:** the live tree passes; the suite prints `PASS: card-file conformance suite, all cases correct`.

---

## Criterion 4 — `validate_card_files.py` gains the pointer check

**What was built.** Rule kind `gotchas_pointer`. `gotchas_pointer_breaches()` requires, in the `SKILL.md` body (frontmatter stripped — a description is a retrieval router, not a when-to-open pointer):

1. a markdown link whose target is `gotchas.md` (angle brackets, `#fragment`, and optional title tolerated);
2. a when-to-open cue on the same line as that link (`when` / `before` / `whenever` / `prior to` / `if`, case-insensitive).

Every link line is scanned: a card may carry several mentions and one proper pointer; returning on the first bare link would red-flag a card whose later line says when to open the file (that bug was caught live against `closure-mode` and fixed before commit). A missing `gotchas.md` skips the pointer check — the missing-file breach already reports it, and double-reporting would inflate one defect into two, the same pattern `evidence_breaches` uses. The PASS line now states the pointer claim. No allowlist entry was added: the live tree passes after the card edits.

**Tests that pin it.** Three fixture cases plus the live case:

| Case | Fixture shape | Expected |
|---|---|---|
| `case_gotchas_pointer_missing_is_rejected` | `SKILL.md` links EVIDENCE.md only (same-length filler keeps the file ≥ 400 bytes); EVIDENCE.md links gotchas.md so reachability stays green transitively | rejected; `1 card contract breach(es)`; message names "no context pointer to gotchas.md" |
| `case_gotchas_pointer_without_when_cue_is_rejected` | `SKILL.md` links gotchas.md on a line with no when-cue | rejected; `1 card contract breach(es)`; message names "no link line says a when-to-open" |
| `case_gotchas_pointer_with_when_cue_passes` | conforming fixture via `skill_md()` | returncode 0 |
| `case_live_cards_carry_gotchas_pointers` | live tree, independent regex | checker PASS + every published card's own text carries a qualifying pointer |

Supporting fixture updates, made so existing cases keep pinning their own assertions rather than going red for an unrelated reason:

- `skill_md()` helper: the See-line now carries a when-to-open pointer, so every conforming tempdir fixture models the new contract (same move the description-bar check made when fixtures gained real frontmatter).
- `case_quotes_do_not_count_against_the_budget`: custom quoted `SKILL.md` updated to carry the pointer.
- Committed rowless poison fixture (`scripts/fixtures/card-missing-evidence-row/.../SKILL.md`): pointer added so the case stays red for exactly one reason — the missing `Re-screen trigger` row — which its assertion requires.
- Committed missing-gotchas poison fixture: **not edited**. The validator skips the pointer check when `gotchas.md` is absent, so that fixture stays red for exactly one reason — the missing file — which its assertion requires.

**Mutation / red-then-green observation (the ticket names no mutation receipt, so none was written; this is the test-first record):**

1. Test cases added first, fixtures/helpers updated to model the new contract. Run: the two negative fixture cases failed for the **right predicate reasons** once the size-floor filler was corrected — earlier drafts dropped below 400 bytes and failed on `size` instead, which is the wrong reason and was fixed before trusting the red. The live independent assertion failed listing 13 cards.
2. Validator implemented. Negative fixture cases passed; live cases stayed red because 13 cards still lacked pointers — the check bites on the live tree, not only on fixtures.
3. Pointers added to 13 cards. Full suite green. A first draft of the checker returned on the **first** link line and red-flagged `closure-mode`, whose later line already said "before"; the every-line scan fix is what let that card pass on its existing pointer.

---

## Criterion 5 — guard-carried entries carry a `promoted: hook` status line naming the guard

**What was built.** Two OBSERVED entries describe traps a named PreToolUse guard now prevents. Each gains one dated status line, appended under the entry, under the existing append-only rule:

| Card | Entry | Status line |
|---|---|---|
| `pull-rebase` | 2026-05-25 origin (bare `git pull` under `pull.rebase=true`) | `` `promoted: hook` — 2026-10-01, `guard-git-pull-rebase.py` (PreToolUse). Prevention fires on the tool call, not on a reader opening this file. `` |
| `decision-rights` | 2026-06-07 origin (blanket "do not re-litigate" framing in a handoff) | `` `promoted: hook` — 2026-10-01, `guard-downstream-framing.py` (PreToolUse on Write/Edit). Prevention fires on the tool call, not on a reader opening this file. `` |

The guards are named from the cards' own records: `guard-git-pull-rebase.py` from `pretooluse-prose/gotchas.md` ("this collection's own preventive half — the hook the `pull-rebase` card prescribes") and `pull-rebase/gotchas.md` 2026-08-23 ("A PreToolUse guard in the maintainer's environment deterministically blocks the bare `git pull`"); `guard-downstream-framing.py` from `decision-rights/EVIDENCE.md` (Enforcement note) and `decision-rights/gotchas.md` 2026-08-29 ("each a draft carrying this card's forbidden framing that `guard-downstream-framing.py` refused to persist").

Entries **not** marked: guard false-positive records (they are *about* a guard, not carried by one); `stale-deploy` (its own 2026-08-23 entry states "no deterministic guard covers it"); `pretooluse-prose` and `dead-predicate` (no named guard carries their discipline); `im-down`/`im-up` (the receiver script is the card's own procedure, not a platform hook).

**Test that pins it.** No validator check was added for status lines — the ticket names only the pointer check for `validate_card_files.py`. The pin is the acceptance inspection plus the append-only diff check below.

**Observed before/after.** Before: zero `promoted:` lines anywhere in the published tree. After: two status lines, each naming its guard and its date.

---

## Criterion 6 — `git diff` shows no existing `gotchas.md` line changed or removed

**What was built.** Nothing — this criterion is a verification of the append-only contract on the two files criterion 5 touched, and of every other `gotchas.md` in the tree (untouched).

**How it was checked.** `git diff --numstat -- 'skills/*/*/gotchas.md'` reports additions only:

```
2  0  skills/engineering/pull-rebase/gotchas.md
3  0  skills/orchestration/decision-rights/gotchas.md
```

A line-by-line comparison of `HEAD`'s version against the working tree confirms every pre-existing line is present byte-identical, in order: pull-rebase 57/57 lines unchanged + 2 appended; decision-rights 107/107 unchanged + 3 appended. All other `gotchas.md` files show no diff at all.

---

## Gate run (compound, after the final commit)

| Gate | Result |
|---|---|
| `scripts/validate_card_files.py` | PASS — 14 cards, pointer claim in the PASS line, 14 allowlisted pre-existing breaches (reachability on EVIDENCE.md / size on two cards), none of them the pointer |
| `scripts/test_validate_card_files.py` | PASS — card-file conformance suite, all cases correct |
| `scripts/validate_scoreboard.py` | PASS — banner line, derived counts, origin tiers |
| `scripts/test_readme_admission_lead.py` | PASS — README admission lead matches the card ledger |
| `scripts/validate_eval_corpora.py` + suite | PASS — 14 corpora, 44 cases |
| `scripts/validate_skill_formats.py` + suite | PASS — 47 folders, 151 files |
| `scripts/validate_voice_provenance.py` + suite | PASS |
| `scripts/validate_brand_kit.py` + suite | PASS |
| `scripts/validate_conformance.py --root .` + suite | PASS — conformance v4, 60 cells, O1/O6/O7/O8 PASS |
| `scripts/validate_spec_conformance.py --root .` + suite | PASS — skills-ref@0.1.5, 38 cards, 21 declared divergences tolerated, 0 breaches |
| `scripts/validate_path_residue.py` + suite | PASS — 317 tracked paths, no residue term |
| `scripts/validate_standing_costs.py` + suite | PASS — 13 freshness hashes re-pinned after the body-only pointer edits; calibrated token figures untouched (descriptions byte-identical since the 2026-09-22 calibration; skill-harness not installed in this container, so the committed snapshot carries the figures and the script's own hash function re-pins the pins) |
| `scripts/validate_disposition_counts.py` + suite | PASS |
| `scripts/validate_site_links.py` + suite | PASS |
| `scripts/test_validate_quarantine_landing.py` | PASS |
| `im-down` parity suite | PASS — roster includes `, no-drift` |
| `im-up` parity suite | PASS — roster includes `, no-drift` |
| Poison control (`validate_packet.py fixture-stale.md --mode produce`) | REJECTED, exit 2 |
| De-personalization residue hooks (pre-commit) | Passed on every commit |

No lint or type tool is named by this repository's workflows; none was invented.

---

## Commit sequence

1. `0ff126c` — `docs(agents): gotchas.md is opened on a pointer, not always-loaded (#327)` — criteria 1 and 2.
2. `3237fcc` — `feat(card-files): gate the gotchas.md when-to-open pointer; every published card carries one (#327)` — criteria 3 and 4 (test-first: fixture red observed, then green after validator + card pointers).
3. `863864a` — `docs(gotchas): append promoted: hook status lines on guard-carried entries (#327)` — criteria 5 and 6.
4. Standing-costs freshness re-pin + this file — `.scratch/issue-327/pr-body.md`.

## Revisit condition (from the ticket, restated so it survives the merge)

Rerun `classify_reads.py` on the next hundred transcripts. If that rerun still shows zero in-use opens on invoked cards, the pointer requirement is falsified and this convention narrows to the label fix alone. That condition is recorded in `docs/rule-screens.md` under the 2026-10-01 screen.
