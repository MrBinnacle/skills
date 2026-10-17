# Three decisions, and what they share

Each card in this repository names one trap. This page looks underneath three recorded
decisions instead, so that an engineer can recognise what went on in them when no card applies.
It describes; it does not instruct. It changes no policy and binds no card.

The three share a structure without sharing a single cause. In each, a representation of
the work (a draft's framing, a reviewer's brief, an install arrangement) kept certain
distinctions and dropped others, and the people relying on it could not see the drop from
inside it. The representation could hide relevant alternatives from anyone relying on it
alone. Interventions can reduce a burden or move it elsewhere, and these cases expose the
difference. Structure appears on both sides, as the thing that froze a bad framing and as the
thing that repaired one.

## A mechanism chosen before the requirement was clear

On Windows, a text-mode write turns a whole LF file into CRLF and still reports success. The
[`uniform-eol` admission record](../../dispositions/2026-09-08-S432-uniform-eol-admission-retest.md)
counted four such conversions across three repositories. Its first draft argued for a hook. It
cited "retrieval measured 0 of 4" and read a rubric rule as though it were a measurement.

Two reviewers withdrew both points. The 0-of-4 figure had been measured on a different card.
The draft had presented measurements about the wrong object. Its framing was "card
or hook", and that framing had dropped a third option: a version-control check that works in
any agent tool. The requirement was only that a converted file must not land unnoticed. The
draft had fixed on a mechanism before asking which mechanisms could meet it.

The admission decision came first: the candidate was deferred, not admitted, because the
maintainer already held a guard repair that the candidate's own record said would make it
redundant. Building that guard came after, and the build turned up three defects of its own,
each fixed with a test. The guard reduced dependence on remembered precautions while introducing
code that has to be maintained. The record's later observation log records the guard catching
conversions on four dates, one deliberate and three unplanned. Those are observations by the same
maintainer, not an independent trial. The record also keeps what the guard cannot reach: a file git never sees still needs a habit,
and that case has one recorded occurrence. The record still calls the choice of layer
undecided.

## A brief that set the reviewer's limits

Pull request #245, merged on 2026-09-06, records the
[case](../../_quarantine/reviewer-horizon/worked-case.md). A reviewer was asked how to migrate
14 cards to two new authoring rules. It was sent those two rules and one size rule, not the
section they came from. Its answer conflicted with a rule it had never been sent, and the first
write-up blamed the reviewer.

The brief was re-sent with the full conventions section and one added instruction: treat the
rules as evidence of one maintainer's decisions, not as constraints. The second answer found
defects in the rules themselves. Pull request #245 repaired five of them before any card was
migrated, because migrating 14 cards to a defective rule would have multiplied the defect.

The fix sent more text, not less. What changed was who decided what the reviewer could see and
question. The selected brief was a representation, and its omission was invisible to
the one reading it. The limits are real too. This is one case, written up by its author. The
licence to challenge the rules came only after a person questioned the first write-up. So the
case shows judgment recovered once a collision was noticed, not a briefer who got it right by
default.

## A simplification that removed a pin

Until 2026-09-15, maintainers installed the published cards as links back into a clone of this
repository. The intent was that a `git pull` would update every installed copy, so drift between
the two would be impossible. [`AGENTS.md`](../../AGENTS.md), under "Source of truth & maintainer
workflow", records what happened in that Windows linked-directory arrangement. Git recorded the
linked files as ordinary tracked files, so a second repository tracked this repository's bytes
in its own index, and neither index knew of the other. A routine checkout there removed one
link, and every file under it left that index in one operation with nothing reported. A
`git restore` on one linked path could have written a stale copy through the link and reverted
a merged commit here.

The link was the simpler arrangement, and it removed a capability: a statement of which version
is in use. The fix added structure back, as a pinned plugin install that records a version and a
commit. The added structure restored version identity, at the cost of an explicit update step:
a pinned copy lags the clone until the install is updated.

## Reading across the three

The first two are related framing failures, not one mechanism. In the `uniform-eol` draft the
author's own framing left out an option, and its evidence pointed at the wrong card. In the
reviewer brief the framing was handed to someone else, who could not see what it had left out.
The third is different again: a simplification dropped a distinction the work needed, the
version pin. None of the three is settled by "less" or "more". Each turned on which
distinction carried the requirement, who was in a position to notice it was missing, and where
the cost of the fix landed.

All three come from one maintainer's work in one repository. They show that the pattern recurs
here. They do not show that it transfers elsewhere.
