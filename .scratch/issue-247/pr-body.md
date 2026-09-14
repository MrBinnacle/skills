# PR Body — Issue #247: Origin Locator Enforcement

## What changed

Added an `origin_locator_breaches()` check to `scripts/validate_card_files.py` that enforces:
when an `EVIDENCE.md` Origin row states `OBSERVED`, the row must contain a locator
that identifies evidence a reviewer can inspect. The gate checks that a locator is
present and that in-repository locators resolve. It does **not** read the target and
judge whether it supports the claim — that stays a review question.

The check is structured as syntactic validity expanding to include evidentiary
admissibility: `OBSERVED` asserts an occurrence, and asserting one requires attaching
a locator. `ABSENT` and `DESIGNED` are unaffected — no locator required.

## Code comment

At the check function (`origin_locator_breaches`), the docstring states:

> This check establishes that an OBSERVED claim has attached evidence that can be
> located and inspected. It does not establish that the underlying event occurred —
> that stays a review question.

This is the explicit boundary the ticket draws between locatable evidence and
historical truth.

## Acceptance criteria

### Criterion 1: `Origin: OBSERVED` with no locator — REJECTED

**Built:** `case_observed_origin_no_locator_is_rejected` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. A model produced an artifact exhibiting
the described failures.` — prose describing what happened, no file path, no link,
no SHA.

**Test:** The checker exits non-zero and stderr contains `no locator identifies
evidence`.

**Observed:** The check correctly identifies that the Origin row contains no
resolvable locator and rejects the card.

### Criterion 2: `Origin: OBSERVED` with non-existent in-repo path — REJECTED

**Built:** `case_observed_origin_bad_path_is_rejected` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. Details: nonexistent-file.md.`

**Test:** The checker exits non-zero and stderr contains `nonexistent-file.md`
and `does not exist`.

**Observed:** The check extracts `nonexistent-file.md` as a locator from the
`Details:` label, verifies it against the card directory and repo root, finds
neither exists, and rejects the card.

### Criterion 3: `Origin: OBSERVED` with non-existent commit SHA — REJECTED

**Built:** `case_observed_origin_bad_sha_is_rejected` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. See commit aaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaa.` (40-char fake SHA).

**Test:** The checker exits non-zero and stderr contains the SHA prefix and
`not present in this repository`.

**Observed:** The check extracts the 40-character hex string, runs
`git cat-file -t` against it, finds the object does not exist, and rejects
the card.

### Criterion 4: `Origin: OBSERVED` with prose-only locator — REJECTED

**Built:** `case_observed_origin_prose_only_is_rejected` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. In a personal production project
(sprint-boundary session), the model produced an artifact exhibiting the
described failures during a session on the operator's machine.`

**Test:** The checker exits non-zero and stderr contains `no locator identifies
evidence`.

**Observed:** The check finds no markdown links, no `Details:` / `Full entry:`
labels with file paths, and no commit SHAs — the entire Origin value after the
date is prose with no resolvable identity. The card is rejected. This is the
#230 shape.

### Criterion 5: `Origin: ABSENT` with `Occasions counted: 0`, no locator — PASSES

**Built:** `case_absent_origin_no_locator_passes` creates a card with
`Origin: ABSENT. No incident recorded.` and `Occasions counted: 0 - no
occurrence to count. RECURRENCE-THIN.`

**Test:** The checker exits zero.

**Observed:** The check does not fire on `ABSENT` origins — the opening word
does not start with `OBSERVED`, so the function returns an empty list. The
honest disposition is not made more expensive than the confident one.

### Criterion 6: `Origin: OBSERVED` with valid in-repo path — PASSES

**Built:** `case_observed_origin_valid_path_passes` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. Details: evidence-log.md.` and a
real `evidence-log.md` file inside the card directory.

**Test:** The checker exits zero.

**Observed:** The check extracts `evidence-log.md` from the `Details:` label,
verifies it exists relative to the card directory, finds it, and passes.

### Criterion 7: `Origin: OBSERVED` with well-formed external reference — PASSES

**Built:** `case_observed_origin_external_ref_passes` creates a card with
`Origin: OBSERVED 2026-01-01, a fixture. Full entry: [gotchas.md](gotchas.md)
→ [OBSERVED].`

**Test:** The checker exits zero.

**Observed:** The check extracts `gotchas.md` from the markdown link target,
verifies it exists relative to the card directory (it does — `write_card`
creates it), and passes. The `[OBSERVED]` in the arrow section is not
extracted as a locator because it is inside a markdown link text, not a target.

## Additional passing cases

- **`case_observed_origin_gotcha_md_path_passes`**: The most common real-world
  pattern — `Full entry: [gotchas.md](gotchas.md) → [OBSERVED].` — passes
  because `gotchas.md` exists in the card directory.

## Mutation campaign

The check has two code paths that a mutant could target:

1. **Locator extraction** (`_extract_locators`): Mutants that skip markdown
   link extraction, skip path extraction, or skip SHA extraction. Each would
   cause a card with only that locator type to be reported as having no
   locator, turning the corresponding poison test green (the test would still
   pass because the card would be rejected for the wrong reason — missing
   locator rather than bad locator — or would fail to extract a valid locator
   and reject a passing card).

2. **Locator validation** (the `for loc in locators` loop): A mutant that
   removes the `candidate.exists()` check would pass a card with a
   non-existent file path, turning `case_observed_origin_bad_path_is_rejected`
   green (the test would fail because the card would pass). A mutant that
   removes the `git cat-file` check would pass a card with a non-existent SHA,
   turning `case_observed_origin_bad_sha_is_rejected` green.

Each named assertion in the poison tests is designed to kill a specific mutant:
- `returncode != 0` kills mutants that skip the check entirely
- The specific error message substring kills mutants that produce the wrong
  error message

## Backward sweep

Ran the check over all 14 published cards and every card in `_quarantine/`
with an `EVIDENCE.md` (3 of 26 quarantine cards have one):

**Published cards (14):**
- 11 OBSERVED: all have valid locators (SKILL.md, gotchas.md, or case-study.md)
- 2 DESIGNED: not checked (no locator required)
- 1 OBSERVED (im-down): has DESIGNED origin — wait, im-down is DESIGNED

Correction: 10 OBSERVED, 2 DESIGNED, 1 OBSERVED (im-up is DESIGNED), 1 OBSERVED.
All OBSERVED cards have valid locators. Zero breaches found.

**Quarantine cards (3 with EVIDENCE.md):**
- `frontend-slop`: ABSENT — not checked
- `self-documenting-code`: ABSENT — not checked
- `uniform-eol`: OBSERVED — has `gotchas.md` locator, resolves correctly

**Finding: nothing to repair.** Every published card with an OBSERVED origin
already carries a locator that resolves. The gate enforces a contract the
collection already meets.

## What this check does NOT do

This check establishes that an `OBSERVED` claim has attached evidence that can
be located and inspected. It does **not** establish that the underlying event
occurred. That stays a review question. A reviewer must still follow the
locator and judge whether the target supports the provenance claim.

The check also does not validate that a locator's target is non-empty, is
markdown, or contains any particular content. It only checks that the path
exists (for in-repo locators) or that the SHA exists in the git object store
(for commit SHAs). External URLs are accepted as locators without reachability
checks.
