# gotchas — success-test-accepts-any-output (append-only)

- [OBSERVED 2026-08-17] Origin incidents, both recorded in `SKILL.md` → Example. A retry loop
  testing `[ -n "$url" ]` printed `#44 OK {"message":"No server is currently available..."}`
  twice while zero comments posted, because `gh` writes API error bodies to stdout. In the same
  session, a test harness comparing `String(got) === String(want)` accepted `check([1], '1')`.
  Both sat inside verification machinery.

- [OBSERVED 2026-08-23] Third instance, and the first in the **negative** direction. During a
  rotation pass over this collection, a throwaway probe harness was written to test whether a
  router rule matched a given phrase. Its success predicate was
  `"<skill-name>" in result.stdout`, and its negative branch printed `MISS`.

  The harness invoked `skill_router_project.py`. The hook file is
  `skill-router-project.py` — underscores against hyphens. Python exited with a "can't open
  file" error, stdout was empty, and the predicate reported `MISS` for **all six probes**,
  including two phrases already asserted as passing fixtures in the rule's own committed test
  suite. The reading taken from that run was that the router matched nothing at all.

  It was one step from being recorded as the session's finding. What caught it was not the
  harness: it was noticing that two known-good fixtures had come back negative, which is not a
  shape a real predicate gap takes.

  **The mechanism is this card's, exactly.** The predicate tested the SHAPE of the output — a
  substring's absence — and never the fact that the operation occurred. Empty output from "the
  hook ran and did not match" is byte-identical to empty output from "the hook never ran."

  **What the card did not yet carry.** Rules 1 through 3 all defend a claim that something
  happened: assert the shape of success, compare identity, re-read external state. A claim of
  ABSENCE has no external state to re-read, so none of the three applies. Rule 4 was added for
  it: carry a known-good positive control in the same run, and treat a clean sweep of negatives
  as evidence against the harness before it is evidence against the subject.

  Standing note for this collection: the failure happened inside a pass whose entire job is
  auditing, on a card that already says the instrument is not exempt. It is not exempt.
