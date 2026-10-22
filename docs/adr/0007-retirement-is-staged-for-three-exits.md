# Retirement is staged for three exits

Status: accepted, 2026-10-20. Builds on [ADR 0002](0002-a-release-is-a-delivery-event.md) and
leaves it untouched: its release arithmetic is applied below, not changed.
[ADR 0003](0003-a-cards-name-is-part-of-the-declared-surface.md) is undisturbed, because nothing
stays in the tree during a watch.

This ADR records the decision adjudicated on
[#482](https://github.com/MrBinnacle/skills/issues/482) (comment of 2026-10-20). It decides
nothing beyond that comment.

## Context

Retirement here has only immediate exits (`AGENTS.md` → Retirement). Every one takes effect at
once, and no step watches a card whose usefulness is in doubt before it leaves. The owner ruled
"add a staged step" (S513). #482 asked for four pre-registration choices, fixed before any card
enters the stage so the outcome cannot be fitted after the fact: the regression signal, the
watch window, the exit, and where the state lives.

The strongest case against a watch was already on #345 (triage note of 2026-10-04, option B).
Installed copies are pinned, so adopters keep a retired card until they update, which is a grace
period by construction, and a `CUT` receipt has already measured. A watch with no instrument
behind it reads nothing. Two facts sharpen that case. The screen path (rule A2) in the harness's
`aggregation/verdict.py` withholds `CUT(subsumed)` for every card whose value class is not
transformative-lift, and the harness classifies 0 of 11 portfolio cards that way. And the
withdrawn-on-the-policy route fires on a card whose record counts zero occasions over its whole
life, so its watch is expected to read zero.

The want survives narrowed. The consumer-protection rationale of Homebrew and Kubernetes
deprecation windows does not transfer: this collection has a pinned installed base and no
dependents. The reversible-removal rationale does transfer. That is the scream test from server
decommissioning: disconnect, wait with a rollback path, then decommission. The design guards
against the one real warning in that literature, a dead control whose signal cannot fire.

## Decision

**Three retirement exits pass through a watch before they become final.**

1. **What the watch is.** A scream test over the maintainer's own session records, not a
   consumer deprecation window. The card leaves the served set on day one, as today. The window
   asks whether the failure the card guarded against comes back while the card is gone.
2. **The regression signal.** An independent occasion of the card's origin failure, counted by
   `AGENTS.md` → "Recording a new occurrence". On the `CUT(subsumed)` route only, a guard-blocked
   entry into the hazard also counts, because that verdict claims the model handles the hazard
   unaided. Dispatches, installs and usage counts are not signals.
3. **The window and the exit.** 90 calendar days and at least 180 observed sessions, whichever
   closes later. It extends once by 90 days. The hard cap is 180 days. The 2 in the exit table
   is `ADMISSION.md` criterion 2, so a restore is a re-admission on field evidence and no new
   bar is invented.
4. **Which exits take the stage.** `CUT(subsumed)`, pre-registered platform-fix and
   withdrawn-on-the-policy. Not `CUT(no_lift)`, because a field occasion cannot reverse a
   measured no-lift. Not `CUT(harmful)`, because a card measured to make outcomes worse is not
   held in limbo.
5. **Where the state lives.** One row in a new `## On watch` table in `RETIRED.md`, placed before
   `## Retired from the collection`. The retiring changeset opens it. Only the rotation pass
   edits it afterwards. A scheduled conformance obligation, O9, fails when a watch is past its
   close date. The mechanism is one table and one date probe, with no new directory and no new
   validator, sized to a low expected yield.

### Route table

| Route | Watch |
| --- | --- |
| `CUT(subsumed)` | Opens. A guard-blocked hazard entry counts as an event. |
| Pre-registered platform-fix | Opens, unless the card is guarded (see the frozen list). |
| Withdrawn-on-the-policy | Opens, unless the card is guarded. |
| `CUT(no_lift)` | None. Deletes at once, as today. |
| `CUT(harmful)` | None. Deletes at once, as today. |

### Exit table

| Events in the window | Exit |
| --- | --- |
| 0 | Retire. The row moves to `## Retired from the collection`. |
| 1 | Extend once by 90 days, then retire. |
| 2 | Restore. This is `ADMISSION.md` criterion 2. |

### Frozen

A change to any of these needs a superseding ADR.

- The signal definition, with its two exclusions (dispatches, and installs and usage counts) and
  the one `CUT(subsumed)` inclusion of guard firings.
- The exit table.
- The route table.
- The clock starts on the day the maintainer's install receipt records a `gitCommitSha` at or
  after the retiring merge, not at the merge. A served card acts through its description with no
  invocation, so a card still installed would make the window read zero by construction.
- A guarded card's watch is not opened on the platform-fix and policy routes unless the guard is
  disarmed. The default is No (see the `[values decision]` below).
- The state location and its sole editor.

### Tunable with recorded evidence

A dated `AGENTS.md` edit that cites closed watches may change:

- the 90-day floor;
- the 180-session floor;
- the one 90-day extension;
- the 180-day cap;
- the `## On watch` column set;
- whether O9 also checks the `CHANGELOG.md` entry.

### The guard `[values decision]`, default applied

Whether to disarm an independent guard for the length of a watch on a guarded card is a
risk-tolerance call on the owner's own working trees, and only the owner holds it. The applied
default is No: guards are not disarmed. A guarded card (today, `pull-rebase`) is then
unobservable on the platform-fix and policy routes, so its watch is not opened. The
`RETIRED.md` row reads `watch not opened: unobservable (guard <name>)` and the exit runs as
today. On the `CUT(subsumed)` route the guard's firings are the signal and the watch runs
normally. To change the default, say so in the retiring PR; the row then records
`guard disarmed <date>, re-armed <date>`. No work waits on this.

### Release arithmetic

ADR 0002 applies unchanged. Deprecate is a minor release. Close-to-retire is no release event.
Restore is a minor release. No watch is opened retroactively on
`claude-code-stop-hook-envelope` or `skill-necessity-gate`, because pre-registration cannot be
backdated.

## Considered and rejected

**No watch.** Installed copies are pinned, and a `CUT` receipt has already measured. Rejected
because the owner ruled for a staged step with this argument in front of them, and reversible
removal is the rationale that transfers.

**A `_watch/<card>/` directory with a sidecar, mirroring `_quarantine/`.** Rejected on cost
against a low expected yield. One table row carries the state.

**A row in the maintainer's private knowledge repository during the watch.** Rejected because
public CI cannot read it, so O9 could not check it.

## Consequences

- `AGENTS.md` → Retirement, rotation pass steps 1 and 7, and `RETIRED.md` carry the rules, in
  [#512](https://github.com/MrBinnacle/skills/issues/512). O9 follows in
  [#513](https://github.com/MrBinnacle/skills/issues/513).
- The retired-table count that `validate_scoreboard.py` reads stays correct only if
  `## On watch` sits before `## Retired from the collection`.
- Nothing changes for an installed user. This ADR changes how future retirements run, not
  anything a user has installed.

## Decision status

- **Non-negotiable:** that a release is a delivery event. Inherited from ADR 0002.
- **Revisable with new evidence:** the tunable list above. *Revisit if:* the first three closed
  watches all read 0 occasions, in which case the policy route drops back to immediate
  retirement; a closed watch records an event the rotation pass cannot classify, in which case an
  eligible-session denominator is added as a tunable; the session floor is unmet at two
  consecutive floor dates, in which case volume is re-measured and 180 retuned; a restore from
  tag goes wrong in practice, in which case the `_watch/` directory design is reopened; or the
  owner reverses the guard default, in which case the guarded-card rule is reopened for every
  route.

## Superseding note, 2026-10-21: the exit table reads lifetime occasions

This append comes from [#551](https://github.com/MrBinnacle/skills/issues/551) (ruling comment
of 2026-10-21,
[#issuecomment-6321658174](https://github.com/MrBinnacle/skills/issues/551#issuecomment-6321658174)).
It rewrites no text above. The exit table is on the frozen list above, and this note is its
superseding record. It changes no row of the table. It states what the table counts for one
kind of card.

**What was wrong.** Decision 3 says the 2 in the exit table is `ADMISSION.md` criterion 2. The
table was written for a card whose record counts zero occasions. Under the #551 ruling, a
published card that counts one occasion can enter the watch through the withdrawn-on-the-policy
route. A window event is an occasion counted in the window, under Decision 2. Read as written,
the table answers one window event for that card with row 1: extend once by 90 days, then
retire. But that event plus the card's prior occasion makes two lifetime occasions, which clears
criterion 2.

**What changes.** During that watch, for a card that enters it at one lifetime occasion, the
table counts lifetime occasions. One window event restores the card, because it is the second
occasion that criterion 2 asks for.

**The guarded card.** A card whose failure an independent guard blocks, such as `pull-rebase`,
is off the #551 clock as unobservable. It is already off the watch, under the guard default
above.

**Where the #551 clock lives.** `AGENTS.md` → Retirement carries the #551 clock rule, which puts
a one-occasion card on this route, in a later change for #551. That clock is not the watch
clock on the frozen list above. This note does not restate the rule.

*Revisit if:* the #551 clock rule's reading changes. Then only the `AGENTS.md` rule changes, and
this note stands.
