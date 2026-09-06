# Evidence body — skills#246

## What was built

Extended `scripts/validate_card_files.py` with three new checks that enforce
normative requirements `AGENTS.md` states but nothing previously gated:

1. **SKILL.md size bounds** — fail if `SKILL.md` is outside 400–7,168 bytes.
2. **Local link resolution** — every relative link in a card's `.md` files must
   resolve to an existing file, matching case.
3. **Reader-facing auxiliary reachability** — every reader-facing auxiliary must
   be reachable from `SKILL.md` through local links (transitive). Exemption
   list for test/build support files (test scripts, fixtures, config examples).

## Acceptance criteria

### Criterion 1: SKILL.md size bounds

**What I built:** `size_breaches()` reads the byte length of `SKILL.md` and
returns a breach if it is below 400 or above 7,168. The 5,120 target is a
review trigger, not a gate.

**Test that pins it:** `case_skill_too_small_is_rejected` creates a card with
a 2-byte SKILL.md and asserts the checker reports "below the minimum".
`case_skill_too_large_is_rejected` creates a card with 7,169 bytes and asserts
"above the maximum". `case_skill_at_size_bounds_passes` creates cards at exactly
400 and 7,168 bytes and asserts they pass.

**Observed:** Before the change, the size check did not exist — a 1-byte
SKILL.md would pass. After the change, the checker correctly rejects undersized
and oversized files while accepting valid ones.

**Live tree violations:** 2 cards exceed the ceiling:
- `downstream-instruction-framing` at 7,620 bytes
- `subagent-research-reliability` at 9,325 bytes

### Criterion 2: Local links resolve with case matching

**What I built:** `link_breaches()` walks every `.md` file in a card, extracts
markdown link targets via regex, resolves each relative to the source file's
directory, and checks that the target exists on disk. Case-sensitive matching
catches Linux/Windows divergence.

**Test that pins it:** `case_broken_link_is_rejected` creates a card where
SKILL.md links to `nonexistent.md` and asserts the checker reports "link target
does not exist". `case_case_mismatch_is_rejected` creates a card with `bar.md`
on disk but a link to `Bar.md` and asserts rejection. `case_valid_links_pass`
creates a card with a valid link and asserts it passes.

**Observed:** Before the change, broken links and case mismatches went undetected.
After the change, the checker catches both. The live tree has no broken links
(all relative links resolve correctly), so this check currently passes on the
published tree.

### Criterion 3: Reader-facing auxiliary reachability

**What I built:** `reachability_breach()` does a BFS from `SKILL.md` through
local links (only following links that resolve within the card directory). It
then checks every file in the card: non-exempt files not in the reachable set
are violations. The exemption list uses fnmatch patterns (`test_*.py`,
`fixture-*.md`, `CONFIG.example.json`) and directory names (`evals/`). A stale
exemption (pattern matching nothing in the card) is also reported.

**Test that pins it:** `case_unreachable_file_is_rejected` creates a card with
an `orphan.md` not linked from SKILL.md and asserts the checker reports "not
reachable from SKILL.md". `case_transitive_reachability_passes` creates a card
where SKILL.md links to `intermediate.md`, which links to `leaf.md`, and asserts
the card passes (leaf is transitively reachable). `case_exemptions_pass` creates
a card with `test_validate.py`, `fixture-clean.md`, `CONFIG.example.json`, and
`evals/` — none linked from SKILL.md — and asserts it passes.
`case_stale_exemption_is_rejected` injects a pattern `test_foo.py` that matches
nothing in the card and asserts the stale exemption is detected.
`case_index_only_name_is_not_a_link` creates a card where `standalone.md`
appears in a table (index block) but has no markdown link, and asserts it is
reported as unreachable.

**Observed:** Before the change, unreachable files went undetected. After the
change, the checker correctly identifies them. The live tree has 12 cards with
unreachable reader-facing auxiliaries (primarily EVIDENCE.md and gotchas.md not
linked from SKILL.md, plus PACKET-FORMAT.md in im-up/im-down).

**Live tree violations:** 12 cards report unreachable files. The full list:

| Card | Unreachable files |
|---|---|
| click-clirunner-env-none-deletes | EVIDENCE.md, gotchas.md |
| git-pull-rebase-trap | EVIDENCE.md, gotchas.md |
| github-pages-deploy-verification | EVIDENCE.md, gotchas.md |
| halt-as-deliverable | EVIDENCE.md, gotchas.md |
| im-down | EVIDENCE.md, PACKET-FORMAT.md, gotchas.md, close_session.py, snapshot_state.py, validate_packet.py |
| im-up | EVIDENCE.md, PACKET-FORMAT.md, gotchas.md, open_session.py, validate_packet.py |
| mock-masked-stub-trap | EVIDENCE.md, gotchas.md |
| pretooluse-bash-guard-prose-false-positive | EVIDENCE.md, gotchas.md |
| success-test-accepts-any-output | EVIDENCE.md, gotchas.md |
| router-skill-predicate-gap | EVIDENCE.md, gotchas.md |
| downstream-instruction-framing | EVIDENCE.md, gotchas.md |
| parallel-review-disposition-schema | EVIDENCE.md, gotchas.md |

## Poison fixtures

Seven poison fixtures prove the gate catches each failure mode. Each makes the
checker go red, and a test proves it:

| Fixture | Proves | Test |
|---|---|---|
| card with SKILL.md < 400 bytes | Size below floor | `case_skill_too_small_is_rejected` |
| card with SKILL.md > 7,168 bytes | Size above ceiling | `case_skill_too_large_is_rejected` |
| card with link to nonexistent file | Broken link | `case_broken_link_is_rejected` |
| card with link differing by case | Case mismatch | `case_case_mismatch_is_rejected` |
| card with unreachable .md file | Unreachable file | `case_unreachable_file_is_rejected` |
| card with test file (exempt) | Exemption passes | `case_exemptions_pass` |
| card with stale exemption entry | Stale exemption | `case_stale_exemption_is_rejected` |
| card with index-only filename | Index ≠ link | `case_index_only_name_is_not_a_link` |

## Files changed

- `scripts/validate_card_files.py` — added `SKILL_SIZE_MIN`, `SKILL_SIZE_MAX`,
  `_EXEMPTION_PATTERNS`, `_EXEMPTION_DIRS`, `_is_exempt()`,
  `_extract_local_links()`, `size_breaches()`, `link_breaches()`,
  `reachability_breach()`; updated `validate()` to call the new checks; updated
  docstring and PASS message.
- `scripts/test_validate_card_files.py` — updated `skill_md()` to pad to 400
  bytes and include EVIDENCE.md/gotchas.md links; added 11 new test functions;
  updated `main()` isolated list; updated committed poison fixture assertions;
  updated live tree test to expect violations; updated `skill_md()` fixture
  SKILL.md files to include required links.
- `scripts/fixtures/card-missing-gotchas/skills/engineering/poison-card/SKILL.md`
  — updated to include links to EVIDENCE.md and gotchas.md and pad to 400+
  bytes.
- `scripts/fixtures/card-missing-evidence-row/skills/engineering/rowless-card/SKILL.md`
  — same updates.

## First run count verification

The gate reports 24 breaches across 14 published cards. This was verified by
running the checker against the live tree and confirming:
- 2 size violations (downstream-instruction-framing, subagent-research-reliability)
- 22 reachability violations across 12 cards (including stale exemption reports)
- 0 broken links
- 0 case mismatches
