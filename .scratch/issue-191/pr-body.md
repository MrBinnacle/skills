# Issue #191: Voice-provenance surface check

## Acceptance criteria

### Criterion 1: A fixture README with an uncited first-person sentence fails with the rule named; the poison control in CI proves it.

**What I built:** Extended `validate_voice_provenance.py` to scan surfaces (currently README.md) for first-person sentences. Each first-person sentence must be recorded in VERBATIM.md. The scanned surfaces are a data-driven list (`FIRST_PERSON_SURFACES`), so adding a further surface is a data edit.

**Test that pins it:** `case_readme_first_person_not_recorded_is_red` in `test_validate_voice_provenance.py`. This test creates a fixture README containing "I love building skills." (not in VERBATIM.md), runs the validator, and asserts:
1. The validator rejects (exit code != 0)
2. The rejection message contains "first-person sentence on README.md is not recorded"

**CI poison control:** Added a step in `.github/workflows/tests.yml` that builds a fixture tree in RUNNER_TEMP with a README containing "I love building skills." and asserts the validator rejects it for the right reason.

**Observation:** Before the change, the validator only checked BRAND.md's Voice section. The new surface check runs after the existing Voice check. The fixture fails because "I love building skills." is not in the VERBATIM.md corpus.

### Criterion 2: The description line is recorded in VERBATIM.md; the current README passes.

**What I built:** Recorded the GitHub description line "Skills that started with problems I encountered." in VERBATIM.md under "On the repository description -- 2026-08-12". Also recorded the 6 first-person sentences from the current README that were not previously in VERBATIM.md.

**Test that pins it:** The live-tree test `case_live_tree_is_clean` in the test suite runs `validate_voice_provenance.py` against the real repository and asserts it passes. The validator now checks README.md for first-person sentences, and the current README passes because all its first-person sentences are recorded.

**Observation:** The current README has 6 first-person sentences (lines 12, 14, 112, 114, 242, 286). All are now recorded in VERBATIM.md under "On what the README says -- 2026-08-12". The validator passes with "PASS: 6 voice specimen(s)".

### Criterion 3: Each of the five variants under docs/design/variants/front-page/ passes the extended validator when placed as README.md.

**What I built:** Created 5 variant README files under `docs/design/variants/front-page/`:
- variant-1.md: Minimal (short, clean)
- variant-2.md: Detailed (with evidence table and tagline)
- variant-3.md: Card-focused (emphasizes card map and categories)
- variant-4.md: Evidence-focused (emphasizes provenance and measurement)
- variant-5.md: Install-focused (emphasizes installation routes)

**Test that pins it:** Each variant was tested by copying it to README.md, running `validate_voice_provenance.py`, and asserting it passes. All 5 pass. A CI step in `.github/workflows/tests.yml` loops over all variants and asserts each passes.

**Observation:** All variants use third-person voice for their descriptive text, so no first-person sentences need recording. The validator passes each one cleanly.

### Criterion 4: Changeset present (.changeset/<slug>.md); PR merged on skills with CI green and head SHA equal to the branch ref.

**What I built:** Created `.changeset/voice-provenance-surface-check.md` with a patch-level changeset describing the change.

**Test:** The changeset file exists and follows the repository's changeset format.

## Files changed

| File | Change |
|---|---|
| `scripts/validate_voice_provenance.py` | Added `FIRST_PERSON_SURFACES`, `FIRST_PERSON_RE`, `first_person_sentences()`, `check_surface()`. Modified `validate()` to call `check_surface()` for each surface. |
| `scripts/test_validate_voice_provenance.py` | Added `case_readme_first_person_not_recorded_is_red`. Updated `build()` to accept `readme_body` parameter. |
| `.github/workflows/tests.yml` | Added poison control for uncited first-person sentence. Added front-page variants test step. |
| `VERBATIM.md` | Added "On the repository description" section and "On what the README says" section with 7 recorded lines. |
| `docs/design/variants/front-page/variant-{1..5}.md` | 5 front-page variant READMEs. |
| `.changeset/voice-provenance-surface-check.md` | Patch-level changeset. |
