---
"mrbinnacle-skills": minor
---

Retire `skill-necessity-gate`. The collection removed its own gate card because the gate card
could not pass its own gate.

`ADMISSION.md` criterion 1 requires an unaided failure that was observed, not predicted. The
card's own `EVIDENCE.md` answered `Occasions counted | 0 — no triggering occurrence`, and no
occurrence appeared across the card's whole life. The defect is not repairable by rewriting: an
occurrence can only be found. The S295 admission triage recorded the card `RECURRENCE-THIN` on
2026-08-15 and deferred the call; this change makes it.

A third retirement route is added to `AGENTS.md` before it is used. **Withdrawn on the policy**
covers a published card removed because it cannot satisfy the admission policy it is measured
against, with the card's own evidence record as the proof and no screen required, because the
failing criterion counts occurrences rather than measuring lift. The route is written narrowly:
it fires on a criterion the card's own record demonstrably fails, and the changeset must quote
the failing row.

Two rules outlive the card and move into `AGENTS.md` in the same commit that removes the
directory:

- **The topology rule** (the card's Gate 3) becomes a rule in its own right — decide
  model-invocable against procedure by asking who does the strategic thinking, treat side
  effects as procedure, and surface the standing-cost maths so the human makes the close calls.
  `AGENTS.md` and `closure-mode-at-boundaries`'s evidence record both cited Gate 3 and now cite
  a rule that exists.
- **No self-authority** — a card's name, its role in this repository, its prior use, and the
  decisions it produced are not evidence for a verdict it reaches. This was unwritten anywhere
  in the repository while the retirement's own argument depended on it.

`ADMISSION.md` keeps its four questions unchanged and loses only its reference-method pointer.
The naming table drops the "gate card" term.

One reduction in assurance is accepted and named rather than slipped in: the policy-to-card
version lockstep in `scripts/validate_scoreboard.py` is removed with the card it compared
against. `ADMISSION.md` must still declare exactly one canonical version, which is the stronger
half of that check.

Conformance machinery follows the removal. The `admission-version-drift` poison fixture is
deleted rather than repaired, because its entire purpose was a disagreement between the policy
file and the gate card's header and there is no longer a second copy of the version to drift
from. The other three drift fixtures keep their breach and lose their gate-card scaffolding;
each was re-run and confirmed to still fail on its own named assertion rather than on an exit
code. The CI malformed-frontmatter poison control is repointed at `router-skill-predicate-gap`
and gains an existence assertion, so a future removal cannot make it vacuous in silence.
