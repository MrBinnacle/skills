# PR body for issue #284

## Acceptance criterion 1: Delete `_quarantine/subagent-research-reliability/`

### What I built

Deleted the directory. It contained only `PROVENANCE.md` — no `SKILL.md`.

### Verification

Read `PROVENANCE.md` and confirmed the patch it describes is already in the live card:

- `PROVENANCE.md` claims `grep -c "dead letter"` returns `3` against the promoted card.
- Measured: `grep -c "dead letter" skills/orchestration/subagent-handback/SKILL.md` returns `3`.
- The three occurrences are at lines 13, 48, and 70 of `SKILL.md` — the dead-letter failure mode, the return-channel instruction, and the recovery variant.
- `git log -S "dead letter" -- skills/orchestration/subagent-handback/SKILL.md` shows commit `541522a` (PR #286, "Name each published card after the word a reader reaches for") as the commit that introduced the content.

The directory is residue of a promotion that already shipped. No content is lost by deleting it.

### What was there

`_quarantine/subagent-research-reliability/PROVENANCE.md` (206 lines) documented:
- The patch: three edits to `subagent-handback`'s SKILL.md (+78/−26), introducing Check 0 (dead-letter return channel), widening Check 2, and adding a third failure mode.
- Two independent occurrences (2026-08-18/19 and 2026-08-24) motivating the patch.
- Route-testing evidence (4 agents, SendMessage vs file path).
- The finding that the patch was already applied (the grep count matched).

None of this is unique to the quarantine copy — it is provenance documentation, not a pending patch.

### Gate

After deletion, `_quarantine/` has 25 directories (down from 26). All eight validators pass. The conformance suite runs 60 cells: 46 PASS, 0 FAIL, 14 CANNOT-CHECK.

---

## Acceptance criterion 2: Add a check refusing quarantine-published name collisions

### What I built

Added O8 ("no quarantine-published name collision") to the conformance gate:

1. **`SECURITY.md`** — added O8 to the standing obligations list. Updated "seven" to "eight" in the machine-check preamble.
2. **`scripts/validate_conformance.py`** — added `Obligation("O8", ...)` to `OBLIGATIONS`, added `check_quarantine_no_name_collision()` function, registered it in `REPO_CHECKS`.
3. **`scripts/test_validate_conformance.py`** — added three test cases and registered them in the isolated suite.

### The check

`check_quarantine_no_name_collision(root)` does:
1. Lists published card names via `find_cards(root)` (the same discovery O7 uses).
2. Lists `_quarantine/` subdirectory names.
3. Reports FAIL if any name appears in both sets. Reports PASS otherwise.

### Tests and what they prove

| Test | What it plants | Assertion | Why it matters |
|---|---|---|---|
| `case_quarantine_name_collision_is_red` | `_quarantine/alpha-card/` (matching published `alpha-card`) | O8 is FAIL, collision names `alpha-card` | Proves the check catches a real collision |
| `case_quarantine_no_collision_is_green` | `_quarantine/unique-candidate/` (no published match) | O8 is PASS | Proves the check stays silent when names are distinct |
| `case_no_quarantine_dir_is_green` | no `_quarantine/` directory at all | O8 is PASS | Proves absence is not a failure |

Each test builds a real tree in a temp directory and runs the checker as a subprocess (the `run_checker` helper), matching the suite's existing poison-control pattern. The tests are isolated — each gets its own temp directory.

### Mutation campaign

The check function has three branches: no quarantine dir, collision found, no collision. All three are exercised by the three test cases. A mutant that deletes the collision detection would fail `case_quarantine_name_collision_is_red` (the O8 cell would be PASS instead of FAIL). A mutant that always returns FAIL would fail both green cases. A mutant that omits the quarantine-dir-absent branch would fail `case_no_quarantine_dir_is_green` (the function would raise on `quarantine.iterdir()`).

### Gate

All eight validators pass after the change. The conformance suite confirms:
- `SECURITY.md states the same number of obligations the checker runs` — 8 == 8.
- `SECURITY.md states the same obligation identifiers, in the same order` — O1-O8 match.
- `O8 no quarantine-published name collision` — PASS on the live tree (14 published, 24 quarantine, 0 collisions).
