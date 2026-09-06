---
name: self-documenting-code
description: Use when reviewing code for clarity, refactoring names or flow without behavior changes, exposing units or side effects, or deciding which comments to keep.
---

# Self-documenting code - 0.2.0 candidate

Find where production and test code mislead a reader. Return evidence-backed findings, or small clarity edits with check results.

One 0.1.0 session on a private TypeScript repository reported eight findings. A loose test helper let a list match a string. A section test accepted an item from a later section. The reader-question rule also stopped two needless edits. Other skills ran alongside it. This is one session, not a measured verdict.

## 1. Set scope and mode

Use review mode for findings; do not edit. Use refactor mode when changes are requested. Skip documentation-only work and reviews with no clarity goal.

Honor explicit scope. Otherwise use the current diff. If empty, inspect the last commit with `git show --stat HEAD`. State the chosen scope. If no clear target exists, ask. Do not widen scope yourself.

Read repo rules, nearby tests, schemas and docs. Mark public names and frozen files.

## 2. Save a baseline

Record the revision, `git status --short` and diff. Run focused checks before edits. Record assertion counts for harness changes. Separate existing failures. Mark missing checks and their limits.

## 3. Apply the assessment model

Use all seven dimensions. Tests and test helpers are not exempt.

| Dimension | Reader question |
|---|---|
| Vocabulary | Which domain concept is this? |
| Contract | What enters, exits and stays true? |
| Control flow | What sequence and decisions apply? |
| State and units | What state or measurement is this? |
| Side effects | What does this operation change? |
| Failure behavior | How can it fail, and who handles it? |
| Executable examples | Which behavior does this test promise? |

Use one domain term per concept. Ground answers in names, types, branches, I/O, error paths and tests.

## 4. Apply the finding test

**write the question before the correction**

For each finding, write:
- The reader's unanswered question.
- Exact code evidence.
- How the gap can cause harm.
- The smallest correction.
- A check that can show behavior stayed stable.

All five are required. Without harm, mark Optional. Without a check, mark Unverified. Do not edit either by default.

Use Required for misleading behavior or safety risks. Use Recommended for clear maintenance cost. Optional changes need a broad-cleanup request.

Use Recorded as a disposition when a real fix needs outside authority. Keep its priority. Name who must decide and where the finding is recorded. If either is unknown, say so in the report. Do not bury it as Optional.

Do not flag consistent framework idioms, obvious short local names, domain math, clear linear algorithms, useful repetition or generated code. Protect comments carrying authority, rationale, units, hazards or compatibility.

## 5. Change one slice

Choose the smallest established refactor.

Apply the **abstraction gate**. A new abstraction must name a stable concept, prevent an invalid state, expose an effect or lifecycle, unite repeated policy, or create a testable boundary around volatile infrastructure.

Classify comments: translation, rationale, authority, hazard, contract, history. Only translation may be removed, and only after code states the same fact. Keep external reasons and obligations in comments or docs, not longer names.

Do not edit generated or vendored code, active migrations or frozen sources without authority. Preserve APIs, serialized keys, CLI flags and data formats. Public renames need approval and a migration plan. Check callers; use language-aware rename tools when available.

Separate bug fixes. Get approval before changing behavior. Review each slice's diff.

For module-shape choices, use `mattpocock-skills:codebase-design` if installed.

## 6. Re-enter when facts change

When a review, CI result or concurrent edit arrives, stop at a safe slice boundary. Address correctness first, within your authority. Re-read changed code. Record a fresh baseline without discarding the first. Fix shared causes once, then resume. Report bug fixes separately from clarity edits.

## 7. Verify and report

Run focused tests, configured format/lint/type checks and broader relevant tests. Use repo tools; install nothing. Compare with the baseline. For harness edits, compare cases and counts; check that bad inputs fail. Inspect the final diff for behavior drift and accidental public or generated changes.

Use built-in `code-review` for correctness if available. This pass does not replace it.

Report scope, revision, mode and limits. For each finding, use step 4 plus priority, disposition and risk. State edits, preserved behavior and interfaces, retained or missing rationale, and check results. Never claim checks that did not run.

Return no findings when none survive. Stop when the remaining gaps need external facts. Record those facts instead of forcing them into names.
