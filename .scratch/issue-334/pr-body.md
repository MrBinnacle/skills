# Issue #334 — S498 currency audit: correct STALE facts in PRODUCT.md, BRAND.md, DESIGN.md

Source audit: `docs/audit/product-definitions-currency-S498.md` in the research repo (not present
in this worktree; the STALE rows are copied verbatim in the ticket, standing order 3). Branch:
`agent/issue-334`. Base: `origin/main` at `246ac5c`.

This PR corrects factual drift only. INTENT surfaces — Users, Positioning, Product Purpose
(governance claim), Brand Commitments, Product Principles — keep their product meaning. Where an
INTENT section contained a stale citation, only the citation changed.

---

## Acceptance criterion 1 — every STALE row corrected (or shown wrong)

Each row below is the audit row, the pre-change text at `origin/main`, the post-change text at
PR head, and the evidence. Line numbers in the "PR head" column are the lines in the cited file
**at this PR head**, not at the audit's tree.

### skills/PRODUCT.md (file lives at repo root `PRODUCT.md`)

| Audit row | PR-head correction | Evidence |
|---|---|---|
| 13-16 "This file states NO counts" | Reworded to "does not restate inventory tallies"; remaining counts named as fixed artifact properties (banned-word list size, scoreboard assertion sites, screened-out candidates) | File still carries "Fifteen words" (~PRODUCT.md:222), "five places across three files" (~:178), "four of the author's own" (~:245). Self-contradiction closed by narrowing the claim, not by deleting those artifact facts |
| 15 AGENTS.md:315 tally ruling | Cites `AGENTS.md:434` | `AGENTS.md:434` opens "The page states no tally of cards, of tiers…". Line 315 is "## Recording a new occurrence" |
| 33-34 README honest ceilings | Attribution to README removed; rule stated as this file's own | `git grep -i "adoption metrics"` / `"honest ceiling"` on origin/main: no hit outside PRODUCT/BRAND. README is 67 lines and has no honest-ceilings section. Rule text itself kept |
| 58-60 README.md:226-230 coverage quote | Cites `CATALOG.md:31` with the live wording (includes "The admission policy keeps it small" and the full Pocock link sentence) | `CATALOG.md:31-33` holds the sentence. README has 67 lines; 226-230 does not exist |
| 86 README.md:14 "useful enough to keep…" | Cites `docs/design/variants/front-page/variant-1.md:20`; notes README:10's current line | variant-1.md:20 holds the retired first-person line. README:10: "Any Claude Code user can hit these failures." |
| 87 BRAND.md:72 "not with a market" | Cites `BRAND.md:75-76` (PR head) | The audit said 74-75 against its tree. After this PR's BRAND.md edit in "What the repository claims", the line sits at 75-76. Verified: line 76 is `not with a market.` |
| 89-90 README.md:87-88 "breadth you do not use…" | Cites `docs/design/variants/front-page/variant-5.md:38` (also at PRODUCT.md Operating Context, which repeated the same stale ref) | variant-5.md:38 holds the line. README has 67 lines |
| 95-97 "each carrying a dated origin incident" | Purpose now allows designed cards; cites README:10 | README:10: "`im-down` and `im-up`, were designed on purpose". Governance claim ("admission is governed…") unchanged |
| 109 "Publication is not validation… both BRAND.md and README.md" | Now "Stated in BRAND.md" | `git grep "Publication is not validation"`: BRAND.md:50, PRODUCT.md (this claim), CHANGELOG.md:1411 (historical). README: no hit |
| 118-120 RETIRED.md:1, 18-20 | Cites `RETIRED.md:3, 26` | Line 3: "Most collections only ever grow…". Line 26: "Turning away your own work costs something…". Quote text unchanged |
| 122-124 RETIRED.md:48-78 + old quote wording | Cites `RETIRED.md:93-102`; wording updated to "All four returned three passes out of three with no skill present" | RETIRED.md:93-102 holds the July 2026 screen section; line 102 has the current wording. The row also records the later `CANT_TELL_YET` / `wrong_instrument` reclassification of one candidate — the PRODUCT quote keeps the ellipsis form and does not claim all four remain ceiling |
| 146-147 installer tracks `main` | Distribution bullet now states version-stamped delivery; release bullet cites ADR 0002 and site/index.html:164 | ADR 0002 (accepted 2026-08-24): "Delivery happens when a version bump merges to `main`." site/index.html:164: "The install path, a card's name and the card format are what a version promises." Old bullet contradicted both this PR's next bullet and ADR 0002 |
| 174 README.md:120 OBSERVED/DESIGNED/DISTILLED | Cites `CATALOG.md:158-160` and `AGENTS.md:429-430` | CATALOG.md:158-160 is the origin-category table. AGENTS.md:429-430 defines the closed vocabulary. README has 67 lines and no such vocabulary |
| 185 public project page undecided | Removed from the undecided list; recorded as settled below that list | `site/index.html` exists; `site/index.html:13-14` sets canonical `https://mrbinnacle.github.io/skills/`; `.github/workflows/pages.yml` deploys it and records homepage set 2026-09-06 |
| 220-223 "a live cautionary precedent" | Now "A cautionary precedent, closed on 2026-09-06"; states the SVG/PNG check that now exists | `assets/tokens.json > closed_gaps.social_preview_raster_is_unreadable.closed = "2026-09-06"`; `words_to_avoid_surfaces` includes `assets/*.svg`; `asset_pairs` pins the SVG/PNG hash pair |

### skills/BRAND.md (repo root `BRAND.md`)

| Audit row | PR-head correction | Evidence |
|---|---|---|
| 47-54 "Publication is not validation" is "in the README's own words" | Attribution removed; sentence kept as BRAND.md's own; notes README does not carry it | `git grep "Publication is not validation"` on README.md: no hit |
| 202-203 project page open decision | Removed from Open decisions; recorded as settled | site/index.html live; homepage set (pages.yml, measured 2026-09-06) |

### skills/DESIGN.md (repo root `DESIGN.md`)

| Audit row | PR-head correction | Evidence |
|---|---|---|
| 112-116 scoreboard extraction citation + proposal to point at social-preview.svg | Cites `validate_scoreboard.py:450-452`; states that social-preview.svg is already covered by `validate_brand_kit.py` (`svg_copy` over `assets/*.svg`) and `asset_pairs` | `scripts/validate_scoreboard.py:452` is `texts = re.findall(r"<text\b…`. `validate_brand_kit.py` collects `svg_copy` surfaces from `tokens.json`; `asset_pairs` records social-preview.svg ↔ social-preview.png. The section no longer reads as a future proposal |

### Audit rows shown to be wrong

None. Every STALE row reproduced here checks out against origin/main. One line-number nuance:
the audit's "BRAND.md:74-75" for *not with a market* was correct on its tree; this PR's BRAND.md
edit added one line above that sentence, so the citation at PR head is 75-76. That is the
audit row being corrected, not a counterexample.

Related stale citation fixed even though the audit did not list it as its own row: PRODUCT.md
Operating Context repeated `README.md:87-88` for the breadth-cost quote (same defect as audit row
89-90). Fixed in the same pass.

---

## Acceptance criterion 2 — no INTENT line changed

Built: `scripts/test_product_definition_currency.py`, cases `case_intent_*`. Those cases read the
live files and pin the INTENT sentences:

- Users: hypothesis blockquote ("The operator of an agent rig they built themselves"), status
  line ("derived design hypothesis. Not observed…"), anti-trigger framing
- Positioning: "turns candidates away… including its own author's", credence-good framing
- Product Purpose: "admission is governed and the governance is visible", ADMISSION four-question
  quote ending "Default answer: not admitted."
- Brand Commitments: authorship rule, voice-specimen citation rule, dressing rule
- Product Principles 1–5, each named phrase
- BRAND.md Voice specimens (owner lines + VERBATIM.md citations)
- DESIGN.md dressing doctrine and the still-open card primary-line decision

Test that pins it: those cases in `test_product_definition_currency.py`. Before the doc fixes
they already passed (INTENT text was present and left alone). After the doc fixes they still
pass. Diff against origin/main (`git diff origin/main -- PRODUCT.md BRAND.md DESIGN.md`) shows
every hunk is either an audit STALE row or a re-dereferenced citation inside an INTENT section;
no INTENT sentence was reworded except the Purpose sentence the audit itself marked STALE.

Observed: suite green on INTENT cases both before and after the content edits — the pin is that
the fixes did not delete the product record.

---

## Acceptance criterion 3 — line-number citations point at the cited text at PR head

Built: two suite cases —

- `case_citations_resolve_at_pr_head` — every `FILE:LINE` citation in PRODUCT.md, BRAND.md and
  DESIGN.md must name a file that exists and a line span inside that file. Validator scripts
  resolve under `scripts/`.
- `case_corrected_citations_match_needles` — each corrected citation is re-opened and the claimed
  phrase must appear at the cited lines.

Before the change, `case_citations_resolve_at_pr_head` failed on PRODUCT.md citing
README.md:226-230, README.md:87-88 (twice) and README.md:120 against a 67-line README. After the
change it reports 17 citation spans, all in range, and every needle matches.

Independent re-check (not the suite): a one-off resolver over the PR-head tree confirmed each
cited span contains the claimed text — see the evidence column above for the target lines.

---

## Acceptance criterion 4 — independent verifier can re-read each corrected line

Built into this body: every STALE row above names (a) the PR-head citation, (b) the target file
and the phrase that must sit at that line, (c) the origin/main claim that was false. An
independent verifier can run:

```
python3 scripts/test_product_definition_currency.py
```

and, for any row, open the cited file at the cited line and compare to the "Evidence" column.
The suite is fail-closed: a citation that moves off its phrase reds the needle case; a citation
that points past EOF reds the range case; an INTENT sentence that disappears reds an intent case.

---

## Tests: what pins what

| Acceptance criterion | Test | Fail-before / pass-after |
|---|---|---|
| 1 STALE rows corrected | `test_product_definition_currency.py` cases `case_product_*`, `case_brand_*`, `case_design_*` | 30 FAIL on the uncorrected tree (stale citations, self-contradiction, old quote wording, open project-page decision, proposal-shaped DESIGN text). After the three file edits: all green |
| 2 No INTENT changed | `case_intent_*` + `case_product_brand_commitment_citations_resolve` | Green before and after — pins non-deletion. `case_product_brand_commitment_citations_resolve` was added because re-dereferencing BRAND.md shifted the Brand Commitment citations; it failed until PRODUCT.md cited 21-23 / 35-41 / 47-54 |
| 3 Citations resolve at PR head | `case_citations_resolve_at_pr_head`, `case_corrected_citations_match_needles` | Failed on out-of-range README cites before; green after. Needle case failed on BRAND.md:74-75 (audit number, pre-shift) until PRODUCT.md and the suite were re-dereferenced to 75-76 |
| 4 Verifier can re-read | The suite itself + this body's evidence table | n/a (documentation criterion) |

Mutation campaign: none. The ticket names no mutation receipt obligation, so
`scripts/mutation_receipt.py` was not run. No mutant was applied. The pinning property is
external: the suite reads the shipped markdown and the cited repository files, not an internal
branch of a checker.

---

## Gate runs (this worktree, `PYTHONUTF8=1`)

Ran after the content edits:

| Gate | Result |
|---|---|
| `python3 scripts/test_product_definition_currency.py` | PASS (29 cases) |
| `python3 scripts/test_design_enforcement_claim.py` | PASS (DESIGN.md enforcement claims; suite not edited) |
| `python3 scripts/validate_voice_provenance.py` | PASS (6 specimens) |
| `python3 scripts/validate_brand_kit.py` | PASS (155 surfaces, 15 banned words, asset pair, hexes) |
| `python3 scripts/validate_scoreboard.py` + suite | PASS |
| `python3 scripts/validate_card_files.py` + suite | PASS (14 cards; known allowlisted link/size notes unchanged) |
| `python3 scripts/check_prose_claims.py` + suite | PASS (7/7 controls; suite needs `GIT_CONFIG_KEY_0=safe.directory` in this container because temp copies hit "dubious ownership") |
| `python3 scripts/validate_site_links.py` + suite | PASS |
| `python3 scripts/test_release_model_disclosure.py` | PASS (ADR 0002 surfaces) |
| `python3 scripts/test_readme_admission_lead.py` | PASS |
| `python3 scripts/validate_vale_style.py` + suite | PASS |
| `python3 scripts/validate_standing_costs.py` + suite | PASS |
| `python3 scripts/validate_disposition_counts.py` + suite | PASS |
| `python3 scripts/validate_skill_formats.py` + suite | PASS |
| `python3 scripts/validate_eval_corpora.py` + suite | PASS |
| `python3 scripts/validate_conformance.py --root .` + suite | PASS (O7 manifests agree; 14 CANNOT-CHECK cells unchanged) |
| `python3 scripts/validate_path_residue.py` + suite | PASS |
| `python3 scripts/validate_quarantine_landing.py` + suite | PASS |
| `python3 scripts/test_release_gate.py` | PASS (66 contract cases) |
| im-down / im-up packet parity | PASS, `no-drift` both ways (cards untouched) |
| im-down poison control | `REJECTED`, exit 2 (stale HEAD + branch drift) |
| `python3 scripts/validate_spec_conformance.py` | Needs `npx`; not re-run here beyond prior green on this tree — no skill frontmatter changed |
| `python3 scripts/test_link_skills_guard.py` | Environment: no `pwsh` on PATH (suite says a skip would be a false pass). Not caused by this change; no PowerShell guard path touched |

No lint/type tool is named by this repository's workflows; none was invented. Vale's error-level
Taste rules apply to `*.md`; the edited prose avoids the Register/Evidence/Voice/Vale error tokens
(perhaps/possibly/arguably, clearly/obviously…, passive "it was decided", "in order to", …) and
`validate_vale_style.py` (scope + digest) passed.

---

## Companion artifacts

- New test: `scripts/test_product_definition_currency.py` (no docs-directory registration; not
  under `docs/`).
- PR body: `.scratch/issue-334/pr-body.md` (this file), committed on the branch as the runner
  reads it for the PR description.
- Audit source `docs/audit/product-definitions-currency-S498.md` lives in the research repo and
  **does not exist in this worktree**; this PR does not claim to ship it.
- Ticket #334: referenced by number here and in DESIGN.md's re-dereference note. The ticket text
  is the standing order; no local tracker file is added.
- Mutation receipt under `docs/assurance/`: **does not exist yet** — none was required and none
  was written. No entry is added to a receipts index because this PR adds no receipt.

---

## What this PR does not do

- It does not decide the Users hypothesis, the intended-audience question, the social card's
  primary line, or the GitHub-About vs package.json description authority. Those stay open.
- It does not rewrite RETIRED.md, README.md, CATALOG.md, AGENTS.md or any skill card.
- It does not install a hook. Nothing here is a discipline that must fire deterministically.
