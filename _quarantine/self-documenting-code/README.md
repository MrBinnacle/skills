# self-documenting-code

A candidate card for evidence-backed code reviews and behavior-preserving clarity refactors.

**This is a candidate in `_quarantine/`, not a published skill.** It is not in the marketplace
manifest, `npx skills add` does not install it, and being here claims only that the card was
written. See [`_quarantine/README.md`](../README.md) for what admission requires.

## Try it without installing

The card is a Markdown file. Copy this directory to one of these locations and Claude Code will
load it:

```bash
# Project
.claude/skills/self-documenting-code/

# Personal
~/.claude/skills/self-documenting-code/
```

## Package structure

The files are flat. There is no `references/`, `assets/` or `scripts/` subdirectory.

```text
SKILL.md                     the workflow and its resource routing
review-protocol.md           the review procedure
assessment-model.md          how a finding is graded
refactoring-patterns.md      the behavior-preserving edits
python.md                    language-specific guidance
claude-code-integration.md   how the card is meant to fire
claude-rules-template.md     a template an adopter copies
report-template.md           the output shape
snapshot.py                  evidence capture
validate_package.py          the card's own package check
evals/                       functional and trigger test cases
EVIDENCE.md                  provenance and evaluation record
gotchas.md                   append-only record of observed failure modes
PROVENANCE.md                where the card came from
FIELD-REPORT-2026-08-17.md   a dated run of the card against a real repository
```

## The package check currently FAILS on this directory

Run it from inside this directory:

```bash
python validate_package.py .
```

Measured 2026-09-08, it exits 1 with:

```text
ERROR: unexpected top-level entries: EVIDENCE.md, FIELD-REPORT-2026-08-17.md, PROVENANCE.md,
       assessment-model.md, claude-code-integration.md, claude-rules-template.md, python.md,
       refactoring-patterns.md, report-template.md, review-protocol.md, snapshot.py,
       validate_package.py
ERROR: scripts/snapshot.py is missing
```

This is a real disagreement, recorded here rather than hidden. The checker was written against a
nested layout — `references/`, `assets/`, `scripts/` — and the card ships flat. One of the two is
wrong and neither has been changed yet, because editing the card's substance is a promotion-gate
matter and not a README fix.

Nothing in this repository's CI runs this checker. Candidates are not gated, which is why a red
self-check sat here unreported.

A second disagreement, for whoever resolves the first: `validate_package.py` permits a
`description` of up to 1,024 characters. This collection's bar is 200, enforced on published
cards by `scripts/validate_card_files.py`. This card's description is 156 characters and clears
the stricter bar, so the two checkers disagree about the rule and not about this card.

## What is not claimed

Behavior remains unmeasured. The functional and trigger evals under `evals/` have not been run in
clean Claude Code sessions. One 0.1.0 session on a private TypeScript repository reported eight
findings, which is recorded in [`EVIDENCE.md`](EVIDENCE.md) as an observation, not a measurement.

*Revisit if:* the package checker and the card's layout are reconciled, which retires the whole
"currently FAILS" section above.
