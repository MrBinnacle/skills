---
"mrbinnacle-skills": minor
---

CI adopts the specification's own validator, and it rejected two published cards on its first run.

Every conformance instrument in this repository was written by its maintainer, which means every one of them can be wrong in the same direction as the cards it grades. `skills-ref` is the Agent Skills specification's reference implementation. Adopting it is the only check here whose author has no stake in this collection passing.

**It earned its place immediately, and it refuted the premise it was adopted under.** The ticket recorded that all published cards and all quarantine candidates pass it unchanged, so the adoption would "lock conformance in rather than creating work". Re-measured on 2026-08-24: **17 of 31 cards were rejected.** Two of those are real defects that shipped.

`click-clirunner-env-none-deletes` and `router-skill-predicate-gap` each carried an unquoted YAML description scalar containing a `: ` or a `{`. Claude Code's own parser tolerates both and the cards work in the product; **a specification-conformant reader cannot load either.** No gate in this repository saw it, because no gate here reads frontmatter at all. Both descriptions are now quoted, with the string values unchanged — 187 and 200 characters, still inside the published 200-character bar.

**The remaining rejections are declared divergences, named and scoped rather than ignored.** A blanket tolerance would make the gate decorative, so each allowance is a pattern, a tree, and a stated reason, and anything not on the list fails:

- On the published tree, exactly one allowance: `disable-model-invocation` is not in the specification's frontmatter vocabulary and is a real Claude Code key with load-bearing behaviour — it is what stops a procedure card auto-firing. Dropping it would change how four published cards behave in the product in order to satisfy a document.
- On the candidate tree, the allowances promotion already closes: bare `author` / `date` / `version` keys, which `AGENTS.md` step 2a strips, and a description over the specification's 1024-character limit, which step 2a rewrites to 200 — a stricter bar than the specification's.

**The asymmetry is the decision.** `skills/` is what ships and is held to the specification. `_quarantine/` is a queue whose entry conditions `AGENTS.md` already states. Measured the same day, 11 of 16 candidates fail on those three classes alone, so enforcing the published bar over the queue would have reddened the build on the day it was adopted and stopped the harvest rather than improved it. A candidate failing for **any other** reason — malformed YAML, a missing `name` — still fails, which is the property that keeps a non-conforming card out of the promotion queue.

Tolerated divergences are printed on every run. A silent allowance is a silent gate.

**Changeset headers are checked, because one got through.** A changeset naming the package `@mrbinnacle/skills` instead of `mrbinnacle-skills` passed all seven validators and all four CI checks and failed only at `changeset version` — after the merge. `changeset status --since=origin/main` now runs in the pull-request job.

**Both new gates ship with a poison control, and the second control was caught being vacuous before it landed.** The frontmatter control plants the exact class that rejected two live cards, into a clone under `RUNNER_TEMP`, and requires the gate to catch it *and* to fail naming `Invalid YAML in frontmatter`. The changeset control was first written to assert only a non-zero exit — and it reddened identically with and without the poison file, because an unrelated "no changesets found" error produces the same exit code. It now asserts the message that distinguishes the two, on a tree that otherwise passes. That is this collection's own `success-test-accepts-any-output` card and the `mutation-killed-by-the-wrong-mechanism` trap, both firing on the same six lines.

`actions/setup-node` is pinned to a full commit SHA with the version in a trailing comment. CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside a 24-hour window; a floating tag is not a pin.

**The gate count is now eight, and that is a cost this repository counts.** It is an eighth validator rather than an inline shell step for one reason: a gate that does not answer the roster grep is invisible, which is the defect corrected in the pass immediately before this one. `AGENTS.md` records the roster, the four deliberate specification divergences, and the `GITHUB_TOKEN` the release step has always needed and never stated.

*Revisit if:* `skills-ref` adds `disable-model-invocation` to its vocabulary, at which point the published allowance is dead and should be deleted rather than left standing.
