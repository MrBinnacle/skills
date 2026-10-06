# gotchas — vacuous-check (append-only)

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
  substring's absence — and never whether the operation occurred. Empty output from "the
  hook ran and did not match" is byte-identical to empty output from "the hook never ran."

  **What the card did not yet carry.** Rules 1 through 3 all defend a claim that something
  happened: assert the shape of success, compare identity, re-read external state. A claim of
  ABSENCE has no external state to re-read, so none of the three applies. Rule 4 was added for
  it: carry a known-good positive control in the same run, and treat a clean sweep of negatives
  as evidence against the harness before it is evidence against the subject.

  Standing note for this collection: the failure happened inside a pass whose entire job is
  auditing, on a card that already says the instrument is not exempt. It is not exempt.

- [OBSERVED 2026-09-08] Occurrence: a PR-readiness filter that could not fail. The filter was
  `select(.conclusion != "SUCCESS")` over a pull request's check rollup. It returns empty both
  when every check passed and when the rollup has barely populated, so it read as all-green at 4
  of 20 checks and a merge was attempted. An unrelated refusal stopped the merge. The filter was
  written an hour after a sibling fix of the same shape merged. The repair printed
  total/ok/pending/fail together, and that form caught the same trap again on the next PR.

- [OBSERVED 2026-09-12] Occurrence: a closed-ticket control that fails open. A build checked
  whether a cited ticket was closed through `gh issue view`, which returns nothing usable when
  `gh` is unauthenticated in CI, and its test skipped on the same condition. The replacement used
  `urllib` and mapped any network error to `None`, and `None` did not fail the check: it moved
  from always fail-open to sometimes fail-open, which reads as flakiness and invites a re-run.
  Mutation caught it, not a re-read of the code.

- [OBSERVED 2026-09-13] Occurrence, false-negative direction: a suppressed error counted as zero.
  A `git show <ref>:<path>` call had its path rewritten by the Windows MSYS shell, git exited 128,
  `2>/dev/null` swallowed the error, and `grep -c` counted zero lines of empty input. The zero
  entered an audit table as an absence. The same working session recorded several more
  clean-looking negatives of this family; they are one occasion, not several, because they are
  fan-out from one session. Each was caught when a second, differently shaped measurement
  disagreed with the first.

- [OBSERVED 2026-09-14] Occurrence, false-negative direction: 0 results from an issue-tracker
  phrase search read as "no duplicates". Six multi-word phrase searches returned zero; the same
  terms joined with `+` returned the duplicates. A search for one known duplicate, run first as a
  positive control, would have exposed the probe. This is rule 4's case: an absence finding with
  no control in the batch.

- [OBSERVED 2026-09-29] Occurrence: three boundary tests that could not go red. An independent
  verifier mutated a pull request's check (an unanchored match, a whole-file slice, a last-entry
  slice) and the suite stayed green under each mutant. The tests' fixtures carried input that
  the check refused for an unrelated reason after a semantics change, so each test passed
  whatever the code under test did. Fixed forward with tests only.

- [OBSERVED 2026-10-02] Occurrence: a vacuous needle in a citation suite (MrBinnacle/skills PR
  #339). The suite checked that a cited line contained a needle string; the needle lacked the
  backticks of the original text, so it matched the reverted text too, and the suite stayed
  green when the cited bullet was reverted. An independent verifier's revert found it; the
  fix-forward corrected the needle. The verdict and the fix are one occasion.

- [RECORDED 2026-10-05] Records reviewed and not counted here. A record of a band row that
  reported a measurement in the grammar of an executed check, when no check ran, describes a
  control that never runs; its own text places it one step before this card, so it is a
  neighbouring defect, not this one. A session close summary and a later fix note repeat the
  2026-09-13 and 2026-10-02 entries above and are merged with them as fan-out.
