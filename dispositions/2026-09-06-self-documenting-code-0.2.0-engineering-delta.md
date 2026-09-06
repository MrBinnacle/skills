# 0.2.0 candidate: engineering notes

ABSENT: an observed unaided clarity failure, its count, a frozen fixture and
counterfixture, a measured screen, and a paired verdict.

The candidate is complete as an instruction card. The supplied evidence does
not settle admission. It supports one useful assisted run, not the required
origin failure. No result is claimed for 0.2.0.

## Version and package

Create a separate candidate folder containing these four files. Do not overlay
it on 0.1.0. The baseline stays frozen for later comparison.

The candidate has no scripts, dependencies or subdirectories. All four files
use the allowed `.md` format. Its version is in the heading and these notes.
Frontmatter contains only `name` and `description`.

The router names clarity reviews, behavior-preserving name and flow changes,
units, side effects and comment decisions. It stays below 200 characters.
Documentation-only tasks and reviews without a clarity goal are excluded in
the body.

## What moving to the candidate gives a maintainer

The opening now says what the agent does and what it returns. It uses the two
test-machinery defects as the reason to reach for the card. It names the single
session and does not turn that session into a general performance claim.

Every pass now follows seven steps. The assessment model is inline. An agent
does not need to find a separate reference to reach the mechanism that worked.

The candidate also gives clear handling for three cases seen in the field:
an empty diff, a real fix outside the agent's authority, and new correctness
information during an edit.

These are design gains. They are not measured gains in accuracy, speed or cost.

## Mechanism retained

The assessment model has seven dimensions, not just the five that produced
the reported findings. All seven remain: Vocabulary, Contract, Control flow,
State and units, Side effects, Failure behavior and Executable examples.

The field findings map to the model as follows. This preserves defect classes,
not private identifiers or quoted code.

| Dimension | Recorded defect class |
|---|---|
| Failure behavior | Two test-helper copies used loose comparison and could accept a list as equal to a string. |
| Executable examples | A section-membership pattern accepted an item from a later section. |
| Vocabulary | A method and a report artifact used one term for two concepts. |
| State and units | Four string identities were interchangeable in the type system, though an alias must never act as an address. |
| State and units | An unrestricted string represented a unit whose governing decision allowed exactly four values. |
| State and units | An empty alias argument meant keep, not clear, without saying so at the call site. |
| Contract | Two ten-field constructors differed in four fields and risked drifting apart. |
| Contract | A missing-link reason lived in both type prose and renderer text. |

The named rule "write the question before the correction" survives intact.
So do the false positives that stopped the two edits: a short local name and
a long but clear linear algorithm.

The five-part finding test remains. A missing harm claim makes an item
Optional. A missing stability check makes it Unverified. Neither invites an
edit by default.

All six comment classes remain. Only translation comments may be removed,
and only after code carries the same fact. The explicit protection for
authority, rationale, units, hazards and compatibility also remains.

The abstraction gate keeps all five grounds from the supplied patterns file.
The compatibility gate protects public contracts and frozen sources.
Verification still starts before the risky edit.

The field report shows codebase-design settling two module-shape choices.
The candidate points to `mattpocock-skills:codebase-design` when installed.
It does not reproduce that skill's design discipline or require its presence.

## Judgments on the three field gaps

### Recorded is a disposition

The report proposed a fourth priority. The candidate instead keeps priority
and disposition separate. A finding can be Required and Recorded.

A blocked fix is not less serious because the agent cannot make it. The
report must name the deciding authority and the record location. If either
is unknown, it must say so. The final report is still a record when the
repository has no local evidence-file convention.

### Explicit scope comes first

A named user scope always wins. With no explicit scope, the candidate uses
the current diff, then inspects the last commit. If that gives no clear target,
it asks.

This adopts the field workaround without letting a last-commit fallback
override a file the user named. It drops the unsupported instruction to pick
a "smallest relevant module" without a basis for choosing one.

### New facts restart the relevant checks

The candidate stops at a safe slice boundary, puts correctness first, rereads
changed code and records a fresh baseline. It keeps the original baseline.
Shared causes get one fix.

This does not grant permission for behavior changes. Bug fixes remain separate
and need authority. A stricter assertion helper changes what the test harness
accepts, even if product output stays the same.

The field proposed this re-entry procedure. The candidate has not yet been
run with it.

## Disposition of every baseline file

| Baseline file | Candidate decision |
|---|---|
| `SKILL.md` | Superseded by the separate candidate card. The workflow, boundaries and report contract remain in a shorter form. |
| `references/assessment-model.md` | Folded inline. The dimensions, finding test, priorities and false positives belong in every pass. A subdirectory buys nothing for this single domain. The worked example and repeated lists of facts code can carry are omitted. |
| `references/refactoring-patterns.md` | The six comment classes, five abstraction grounds and core compatibility rules are inline. The catalog, code examples and detailed search checklist are omitted to keep the card small. |
| `references/review-protocol.md` | Not shipped. Evidence-only findings, empty results and rechecking remain. The separate cold-review prompt, restricted input bundle and adjudication procedure are omitted. The field records built-in correctness review, not use of this protocol. |
| `references/claude-code-integration.md` | Not shipped. Installation, persistent rules, language-server setup, hooks and plugin planning are outside a clarity pass. The candidate installs nothing. |
| `references/python.md` | Not shipped. The Python-specific type, exception, naming and tool examples were not exercised in this field run. Repository checks and language-aware renames remain as general instructions. |
| `assets/report-template.md` | Its essential fields are folded into steps 4 and 7. The separate template layout and placeholder text are omitted. |
| `assets/claude-rules-template.md` | Not shipped. Persistent project policy is outside this card's scope. Its core clarity constraints already appear in the workflow. |
| `scripts/snapshot.py` | Not shipped. It records Git state and file hashes, not behavior stability. The report does not say it ran. Revision, status, diff and check results provide the baseline this candidate needs. |
| `scripts/validate_package.py` | Not shipped. It validates the old layout, requires the snapshot script and allows a 1,024-character description. It cannot certify this candidate against the house rules. No replacement executable is supplied. |
| `evals/evals.json` | Not shipped in the candidate. Its five cases remain frozen with 0.1.0. Every `files` array is empty. They are prompts and output assertions, not frozen code fixtures. |
| `evals/trigger-evals.json` | Not shipped in the candidate. Its 20 queries, split into 10 positive and 10 negative labels, remain frozen with 0.1.0. Negative routing examples are not a behavioral counterfixture. |
| `README.md` | Not shipped. These notes state the candidate package and its limits. The old installation and validation instructions describe a different layout. |

The detailed external-context examples are also shortened. Design trade-offs,
legal authority, performance workloads, security assumptions, release dates
and dependency quirks still belong outside names and control flow. The six
comment classes and the final stop rule carry that boundary without repeating
the full list.

The snapshot and validator remain untouched in the baseline. The candidate
asks the agent to run neither. It names no unshipped helper script.

## What would make it screenable

Neither supplied eval file contains a frozen behavioral fixture and
counterfixture. Routing labels do not fill that gap. No empirical contract
has been added here.

A screenable package needs JSON files that freeze:
- The task, source text, context and allowed actions.
- A defective case with expected, evidence-backed findings.
- A close clean case where those findings and edits are forbidden.
- The required output fields and pass/fail rules.
- The checks that establish behavior or harness coverage.

Use synthetic source text. Do not copy private code. Store it inside JSON,
not as a TypeScript file in the skill folder. Any test workspace that needs
other file extensions must live outside that folder.

A useful first fixture would exercise both test-machinery defects. Its
counterfixture would use a sound comparison and a bounded section check.
Both could retain an obvious local name, a clear linear function and
authority comments. That would test detection and restraint together.

Freeze the inputs and scoring rules before running trials. Compare unaided
runs, 0.1.0 runs and candidate runs under matched conditions. Record companion
skills rather than silently changing them between runs.

No new runtime is needed for a review-only screen. If an executable scorer is
later added, use Python's standard library, ship it flat, and name it in
SKILL.md.

Synthetic tests cannot supply the missing historical origin. An observed
failure without the card still needs its own record.

## Evidence decisions and unresolved facts

The prevention claim is not an unaided incident. The report says what would
have shipped without the rule, then records that it did not ship. The earlier
identity bug lacks recorded unaided conditions. Neither can fill criterion 1.

The report's finding totals conflict. Its narrative gives eight findings,
seven applied and one recorded. Its metrics give eight plus one recorded.
The candidate opening uses the narrative's reported eight. EVIDENCE.md keeps
both accounts. The underlying finding log would be needed to settle the total.

The assertion totals describe different stages. The immediate harness swap
kept 52 + 73 checks. The full pass ended at 53 + 92. Both had zero failures.
Equal counts do not prove that no case was replaced or lost. The candidate
therefore asks for case coverage and failing controls, not counts alone.
That added check has not been tested as part of 0.2.0.

The byte-identical end-to-end result supports that recorded run. It does not
prove behavior is unchanged for all inputs.

Built-in `code-review` was the review skill used here. It was not
`mattpocock-skills:code-review`. The second-hand account of idle subagents is
omitted. The mutation-seam proposal and implementation skill's commit-order
and TDD issues are also omitted. They concern other skills, not this card's
procedure.

All private repository identifiers and code quotes are omitted. Dates,
relevant counts, dimensions and defect classes remain. The gotchas log dates
the observations, not an invented candidate run.
