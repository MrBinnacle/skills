---
"mrbinnacle-skills": patch
---

The `vacuous-check` card's rule 4 example labelled RIGHT now does what it claims. Its probe printed `MISS` for a path that did not exist, so a mistyped suspect path still read as a true negative after the control passed, which is the defect the WRONG comment named. The probe now branches on grep's exit status and prints `HIT`, `MISS` or `ERROR`, and the WRONG comment names the break only the control catches: a mistyped `$MARKER` that prints `MISS` for every readable path. The card's `gh` bullet now states what a run on 2026-11-12 with gh 2.92.0 showed: on an HTTP 404, `gh api --jq` exits 1 and prints the unfiltered error body to stdout, so the jq filter is not what fills the capture. Rule 1 now says the stdout claim rests on two runs, on 2026-08-17 and 2026-11-12.
