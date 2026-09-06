# Field report — `self-documenting-code` and the mattpocock skills, run together on a live repo

- **Date:** 2026-08-17. **Repo:** a private linter project, a read-only Notion structure linter.
- **Scope of the run:** one ticket implemented end to end, then a clarity pass over the whole
  source tree — 16 TypeScript files, 2,213 lines.
- **Skills exercised:** `mattpocock-skills:implement`, `mattpocock-skills:codebase-design`,
  `self-documenting-code`, plus the built-in `code-review`.
- **Evidence class.** Everything under "What happened" is observed in one session. Everything under
  "Proposed" is inference from that single run. **n = 1.** Where a claim is second-hand from a
  previous session, it says so.

---

## 1. What was invoked, in what order

| # | Skill | Why | Effect |
|---|---|---|---|
| 1 | `mattpocock-skills:implement` | User invoked it with a ticket number | Governed the whole build: implement → typecheck often → full suite at the end → `/code-review` → commit |
| 2 | *(built-in)* `code-review` | Step 4 of `implement` | Returned 6 findings, 3 of them defects the implementation had just introduced |
| 3 | `self-documenting-code` | User invoked it, then widened scope to the whole project | Produced 8 findings; 7 applied, 1 recorded-not-corrected |
| 4 | `mattpocock-skills:codebase-design` | **`self-documenting-code` did not require it — I loaded it because the user said the skill was "engineered with pocock skills in mind"** | Supplied the vocabulary the findings report is written in, and settled two design calls |

**Correction worth making explicitly, because it would be easy to over-claim:** step 2 was the
**built-in** `code-review`, not `mattpocock-skills:code-review`. The two are separate skills with
the same slash name in this environment. This report says nothing about the quality of Pocock's
code-review skill from *this* session. (The repo's state file records that in the *previous*
session, `mattpocock-skills:code-review` was invoked and **both of its sub-agents idled and neither
ever returned a report** — three notifications from one, four from the other — so both axes were
re-run in the main context. That is second-hand here and belongs to whoever wants to chase it.)

---

## 2. `self-documenting-code` — what it caught, prevented, and protected

### 2.1 Caught (8 findings, evidence-backed)

Each of these came from a specific dimension in `references/assessment-model.md`. The dimension is
named because that is the part of the skill doing the work.

| Dimension | Finding | Consequence if unfixed |
|---|---|---|
| **Failure behavior** | Two test-harness copies compared `String(got) === String(want)`, so `check('x', 1, '1')` passes — and so does `check('x', [1], '1')` | A type-loose assertion inside the instrument certifying a product whose entire purpose is detecting false-green reporting |
| **Executable examples** | Section assertions written `/GAPS[\s\S]*<id>/`, which spans the rest of the report — an ID appearing only in a later section satisfied a test claiming it appeared in `GAPS` | The test claimed section membership and did not test it |
| **Vocabulary** | A rule method named `report()` returning findings, in a codebase where `Report` already names the artifact carrying the disposition and the coverage vector | One term, two concepts, in a glossary-governed repo |
| **State and units** | Four different string identities all typed `string` — raw ID, normalized ID, manifest key, alias — where the alias must **never** address anything | Silent substitution of a title where an ID belongs; the repo had already shipped that exact bug once |
| **State and units** | `unit: string` on a coverage row, where the governing ADR declares exactly four units | A fifth unit by typo; `resource` vs `resources` reads as two units in one vector |
| **State and units** | `mark(key, '', 'evaluated')` — the `''` is an alias parameter whose empty value means *keep*, not *clear*, and nothing at the call site said so | A reader "fixing" it clears the report label of every evaluated resource |
| **Contract** *(abstraction gate)* | One `Finding` type constructed by two ten-field object literals differing in four fields | A field added to one path and missed on the other |
| **Contract** | The reason a link is null stated twice — once as prose in a type, once as a string literal in the renderer | Two copies of one fact, guaranteed to drift |

**The first two are the ones worth telling Matt about**, because they were found by turning the
skill's dimensions on the **test code**. The assessment model does not scope itself to production
code, and nothing in it exempts a test harness. Most clarity guidance implicitly does. Here that
non-exemption found the loosest comparison in the repository.

### 2.2 Prevented (2 changes I would otherwise have made)

The rule **"write the question before the correction"** (`## Reader-question method`) killed both:

- Renaming a CLI helper `value()` → `optionValue()`. I could not state a reader question it
  answered; the function is three lines from its call sites. The skill's own false-positive list
  covers it: *"short local names in a small and obvious scope."*
- Splitting a 50-line orchestration function. Same failure — no question, just discomfort. The
  false-positive list again: *"a long function that represents one linear algorithm clearly."*

This is the highest-value part of the skill in my experience of running it. Without that rule, both
edits would have shipped as "cleanup", each with a nonzero chance of a behavior change, in a diff
the user would then have had to review for no benefit.

### 2.3 Protected (the part a naive pass would have destroyed)

This repository comments unusually heavily, and almost every comment is an **ADR citation** —
`ADR-0005 decision 3`, `spec §1.2`, `Principle 3` — plus the observed incident that produced the
constraint. A generic "self-documenting code means fewer comments" pass strips those. That would
have been the single most destructive edit available, because those citations are the repo's audit
trail: the project's rule is that ADRs are *never edited*, only superseded, so the code comment is
the only place stating which decision governs a given line.

Two parts of the skill prevented it, and they are the parts I would tell Matt not to trim:

1. The **comment rule**'s six-way classification — translation / rationale / authority / hazard /
   contract / history. Only the first is removable, and it is removable *only after the code states
   the same fact*.
2. The **false-positive list** naming it outright: *"comments that cite authority, rationale, units,
   hazards, or compatibility."*

### 2.4 The verification discipline is what made the riskiest change safe

Replacing two loose comparison helpers with one strict `Object.is` harness is exactly the change
that can silently delete coverage. The skill's finding test, clause 5 — *"verification can show that
behavior remained stable"* — forced a baseline **before** the edit: 52 and 73 assertions, zero
failures. After the swap: 52 and 73, zero failures. **Identical counts are the proof that nothing
had been passing on the looseness.** Without the pre-baseline the swap would have been unfalsifiable.

---

## 3. Three gaps in `self-documenting-code`, with proposed fixes

### Gap 1 — no disposition for *"real, and not yours to fix"*

**The case.** A rule reported the evidence value `unreached` for a resource that was skipped **by
design**, not for want of access. The governing ADR's remedy column for that value reads *"widen
access, or raise the request budget"* — neither of which can help. So the report names a remedy the
operator cannot act on.

That finding passes **all five clauses** of the finding test: a reader question with no reliable
answer, exact code evidence, real consequence, no smaller correction, and a verifiable fix. But the
correction is not an edit — it requires an architectural decision recorded in an ADR, which is
above the authority of a clarity pass.

The skill's priority ladder is Required / Recommended / Optional. Optional is defined as *"taste,
local style, or alternative designs with no demonstrated benefit"* — which this is not, and
filing it there is where it goes to die. I had nowhere to put it, so I used a repo-local convention
(an evidence file). **A project without that convention would have dropped the finding entirely.**

**Proposed fix — a fourth priority in `references/assessment-model.md`, after Optional:**

```markdown
### Recorded

Use this priority when the finding passes all five clauses of the finding test but the
correction is not an edit — it requires a decision, an external authority, or a change to a
frozen artifact.

Name the authority that must decide, and where the finding is now recorded. Do not downgrade
it to Optional: it is not a matter of taste, and Optional is where it goes to die.

Examples: a value whose taxonomy is set by an architecture decision record; a constraint owned
by another team; a defect inside a file under a compatibility freeze.
```

And one row in the report template's Findings table legend, plus a bullet in `## 7. Report the
result`: *"Which findings were recorded rather than corrected, and who must decide them."*

### Gap 2 — scope resolution has no fallback when the diff is empty

`## Select the mode` says: *"If the user gives no scope, use the current diff. If the diff is empty,
use the named file or smallest relevant module."*

I invoked it immediately after committing. The diff was empty and **no file was named**, so the
rule fell through to "smallest relevant module" with nothing to select it by. I improvised: scope =
the last commit. That is almost certainly what the rule intends, and it should say so.

**Proposed:** *"If the diff is empty, use the working tree's last commit (`git show --stat HEAD`)
before falling back to a named file. An empty diff most often means the work was just committed,
not that there is nothing to review."*

### Gap 3 — no re-entry when a concurrent process changes the code mid-pass

The workflow is linear: baseline → vocabulary → diagnose → choose → change one slice → verify →
report. In this run, a background code review returned **while I was in step 5**, carrying six
correctness defects, three of which were in code the clarity pass was actively editing. Two of them
shared a root cause with a finding I had already logged.

I merged the two workstreams by hand: correctness first, clarity second, one commit. That was the
right call, but the skill has no step for it, and under end-of-session fatigue the tempting move is
to finish the refactor and treat the review as "next session's problem" — which produces a commit
whose clarity changes are built on code known to be wrong.

**Proposed — a short subsection under `## Required workflow`:**

```markdown
### If new information arrives mid-pass

A concurrent review, a failing CI run, or a bug report can land while a slice is open. Do not
carry on and do not discard the pass.

1. Stop at the current slice boundary; do not leave a half-applied refactoring.
2. Classify the new information: correctness defects outrank clarity findings, always.
3. Re-run the baseline — the new information may have invalidated it.
4. Check whether any new defect shares a root cause with a logged finding. Fix the cause once.
5. Then resume the pass. Report both streams separately so the reader can tell a behavior fix
   from a clarity change.
```

---

## 4. `mattpocock-skills:codebase-design` — how it composed, and one proposed extension

I loaded it purely for vocabulary. It did more than that:

**It settled two design calls the clarity skill could only frame.**

- The `mark(key, '', 'evaluated')` ambiguity has two candidate fixes: add a `markEvaluated(key)`
  method, or export a named constant `KEEP_ALIAS`. `self-documenting-code`'s abstraction gate is
  neutral between them. **Depth-as-leverage is not:** adding a method widens the module's interface
  for the benefit of one call site, which is exactly the shallow direction. The constant costs zero
  interface. That is the deciding argument and it came from the Pocock skill.
- The two ten-field object literals → one constructor passed both gates independently:
  `self-documenting-code`'s abstraction gate condition 2 (*prevents an invalid state*) and
  codebase-design's deletion test (*delete it and the complexity reappears across N callers*).
  **Two skills, two framings, same verdict** — which is a useful signal that the change was not
  taste.

**Proposed extension to `codebase-design` — a mutation check is a second adapter.**

The skill says: *"One adapter means a hypothetical seam. Two adapters means a real one. Don't
introduce a seam unless something actually varies across it."*

This repo injects its rule object at two points so that a mutation check can disable **one clause
at a time** and assert the exit code moves. In production there is exactly one adapter, so by a
literal reading the seam is hypothetical and unjustified. It is not: the mutated rule **is** the
second adapter, and it varies across the seam in the only way that matters — it is what proves the
mechanism is load-bearing.

That is not hypothetical in this codebase. Disabling one clause moved the process exit byte from
`2` to `0` and flipped the report's disposition from *disclaimed* to *unqualified*: a run that
should refuse to render a verdict instead printed a clean bill of health over data it never read.
No other test in the suite detected that; the seam is the only reason the check can exist.

Suggested wording, appended to that bullet:

> A test double counts. So does a deliberately broken implementation used by a mutation check — if
> a seam exists so a control can disable the mechanism and prove the result moves, the mutant is
> the second adapter and the seam is real.

This also strengthens the skill's own line *"the interface is the test surface"*: the interface is
the **mutation** surface too, and that is a sharper reason to place a seam than testability alone.

---

## 5. `mattpocock-skills:implement` — one real ordering defect

The skill's body is five instructions. Two observations, one of which is a genuine bug.

### 5.1 The bug: `/code-review` is asynchronous, so "review then commit" does not hold

> *"Once done, use /code-review to review the work. Commit your work to the current branch."*

The ordering is explicit and correct in intent. But `/code-review` runs as a **forked background
agent**: it returns a task notification minutes later. I launched it before committing, waited,
committed when it had not returned, and it landed ~7 minutes after the commit — carrying six
findings, three of them defects in the commit it was reviewing. The fixes became a second commit.

The instruction as written cannot be satisfied as written whenever the review is backgrounded, and
nothing in the skill acknowledges that.

**Proposed:** make the asynchrony explicit and give the agent a rule for the wait:

```markdown
Once done, use /code-review to review the work.

/code-review may run as a background agent and return minutes later. Do not commit while it is
outstanding — a review that lands after the commit turns its findings into a second commit and
loses the property that the reviewed tree is the committed tree. If you must commit first (long
review, end of session), say so explicitly in the commit message and treat the follow-up as a
fix commit rather than an amendment.
```

### 5.2 The `/tdd` instruction did not fire, and the reason may be worth encoding

> *"Use /tdd where possible, at pre-agreed seams."*

I did not invoke `/tdd`. The honest reason: this repo's test convention is hand-written "red test"
scripts whose central artifact is a **mutation check** — a test that disables a mechanism and
asserts the result moves. The ticket pre-specified those seams. Red-green-refactor on a
mutation-check suite is an awkward fit, because the first test you write is not "assert the feature
works" but "assert that breaking the feature is detectable", which needs the feature to exist.

*"Where possible"* already licenses this, so the skill is not wrong. But an agent reading it gets no
guidance on what makes TDD *not* possible, and the default reading of a `/tdd` instruction is that
skipping it is a failure. A sentence naming one or two legitimate carve-outs would make the
judgment call explicit rather than sheepish.

---

## 6. The composition thesis, stated for Matt

The two skills fit together better than either advertises, and it is worth documenting because it
is not obvious from either description.

`self-documenting-code` asks *does this code state its own mechanics?* `codebase-design` asks *is
this the right module shape?* Run alone, each has a characteristic failure mode:

- **Clarity alone** renames things inside a bad shape. Every name improves; the module is still
  shallow.
- **Design alone** produces a defensible seam nobody can read, and — critically — has no rule about
  comments, so a design pass can strip the very facts that make an interface usable.

They interlock at one specific point, and it is the most useful thing I found:

> `codebase-design` defines **Interface** as *"everything a caller must know to use the module
> correctly: the type signature, but also invariants, ordering constraints, error modes, required
> configuration, and performance characteristics."*
>
> That is a principled reason to **keep** the exact comments `self-documenting-code`'s comment rule
> protects. An invariant that the type system cannot express, and the authority behind it, are part
> of the interface. They are not commentary on the implementation — they are the interface, written
> in the only medium available.

So: the comment rule is not a concession to legacy code. Under Pocock's own definition of
Interface, rationale and authority comments are **interface documentation**, and deleting them
makes the module shallower by removing what a caller must know. Neither skill currently says this,
and both would be stronger for saying it.

---

## 7. Metrics, for whatever they are worth at n = 1

| | |
|---|---|
| Files in scope | 16 TypeScript files, 2,213 lines |
| Findings | 8 (2 Required, 5 Recommended, 1 Optional) + 1 Recorded-not-corrected |
| Changes prevented by the reader-question rule | 2 |
| Files declared out of bounds by the compatibility gate | 2 (frozen primary sources; a rename in either requires an architecture decision first) |
| Assertions before | 52 + 73, zero failures |
| Assertions after | 53 + 92, zero failures |
| Behavior changes | 0 intended; live end-to-end run byte-identical before and after |
| Defects found by the clarity pass | 2 with live consequences (loose comparison, unanchored section assertion) |
| Defects found by the code review | 6, of which 3 were introduced by the commit under review |

The last row is the honest framing for anyone tempted to read this as a clarity-skill success
story: **the clarity pass and the code review found disjoint defect sets.** Neither substitutes for
the other. The clarity pass found defects in the *verification machinery*; the review found
defects in what the program *claimed*.

---

## 8. Before sending any of this

- Everything here is one session on one repository, by one agent. Nothing has been replicated.
- The proposed wording changes are drafts, not tested against other codebases.
- Section 4's extension claim rests on this repo's mutation-check convention, which is unusual.
  It generalises only to codebases that treat "the control must be able to fail" as a rule.
- The `mattpocock-skills:code-review` sub-agent failure in section 1 is **second-hand** — recorded
  in this repo's state file from the previous session, not observed in this one. Verify before
  reporting it upstream.
