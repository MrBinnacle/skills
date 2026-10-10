# Worked example — both faces, one session

Observed in a research session, 2026-08-25.

## First face: two successful sweeps stopped one layer high

A frozen research charter defined an adequacy criterion: a representation is inadequate when it
merges two states that license different downstream decisions.

Two prior-art sweeps ran across two sessions. Both were competent. Both returned real, citable,
correct material — evaluation schemas, reporting standards, rough-set applications,
decision-analysis practice. One of them concluded that a central element of the criterion "does
not reduce to prior art."

Neither sweep went below the applied layer, because neither had a reason to: both had succeeded.

A third pass asked only *what is this an instance of?* — and the criterion turned out to be
**Blackwell's sufficiency ordering for comparison of experiments, published 1951**. The charter
was its deterministic, finite, fixed-decision-set special case, and the charter's own deliberate
restriction to a *declared* decision set was precisely the choice not to take Blackwell's
universal quantifier.

Three further results followed from the same question:

- a matroid/greedy-optimality question behind a proposed elimination procedure;
- the junta problem behind a minimal-field-subset question;
- a game-theoretic result showing the criterion's own two-category vocabulary had no place for a
  distinction that is actively harmful.

⚠ **Honest limit.** Those results were read from secondary sources that state them formally. No
primary was read in full. That does not weaken the pattern — the point is that the material was
reachable in one pass by one question, and two prior sweeps never asked it.

## Second face: a name-grep manufactured an absence

A tool's `SKILL.md` was grepped for `init`. Zero hits. The conclusion was recorded and stated
aloud: the tool has no setup flow, so its config file must be hand-authored.

Both halves were wrong. The command table two lines further down carried the same capability
under the name `teach`, and the tool's own preflight explicitly *forbade* hand-authoring that
file.

The word was absent. The capability was not.
