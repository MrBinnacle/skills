# gotchas — downstream-instruction-framing

## [ANTICIPATED]

- **"Revisit if:" clauses degrade into boilerplate.** Copy-pasting the same clause ("revisit if
  anything changed") onto every decision defeats the forcing function. Each clause must name a
  *specific, checkable* condition; if you can't, the decision is under-justified.
- **Directive discipline skills are the legitimate exception.** A skill whose entire value is a
  hard stop condition ("do not proceed past X") should stay imperative — softening it to
  proposal mood destroys the discipline. This skill governs *proposed work*, not guardrails.
- **The framing block itself gets trimmed under length pressure.** When a handoff is compacted,
  the "How to Treat This Document" section looks like removable preamble. It isn't — it's the
  part that keeps the rest from being executed blindly.
- **Downstream over-correction.** An agent given full license to disagree can re-open settled
  values decisions without new evidence. The "no arbitrary re-opening" clause in the template is
  load-bearing; keep it when adapting.
- **[ANTICIPATED 2026-08-12] Supersedes the first anticipated entry's universal wording.** A
  `Revisit if:` clause belongs only on a decision whose outcome could change with new evidence.
  Values decisions and explicit user constraints are non-negotiable; adding a clause to them is
  itself boilerplate and can falsely imply that better evidence transfers decision rights.

## [OBSERVED]

*(Append observed gotchas here as they surface. Do not delete entries — gotchas are
stress-test signal.)*

- **2026-06-07 / a private production project (security handoff):** the user caught an
  "Approved Decisions (Already Made — Do Not Re-Litigate)" header in a handoff doc and required
  correction; in the following turn, generalized the rule: "there's a time and a place for 'do
  not re-litigate' but it's never an ALWAYS framing." The before/after in SKILL.md's Example is
  that artifact pair verbatim (identifiers genericized). Direct origin of this skill.

- **2026-08-23 / corpus harvest, 1358 files across 28 project directories:** a rotation pass
  searched every reachable session record, handoff, audit and research document for this
  card's origin failure. Each card's search signature was required to locate that card's own
  known origin incident before its result counted; a signature that cannot find the occurrence
  we know happened cannot interpret a zero.

  **What the sweep located.** The refused framing is institutionalized in a second, unrelated
  project: four phase-handoff documents each carrying a `## DECISIONS ALREADY MADE (do not
  re-litigate)` section, and a planning boilerplate that templates it, so every handoff
  generated from it inherits the framing. Dated 2026-04-29 (three of them, one drafting pass),
  2026-05-02, and 2026-06-02 for the boilerplate.

  **All of them predate this card's 2026-06-07 origin, and none is counted.** Recurrence means
  the failure happened again after the discipline existed; that is what `Occasions counted`
  answers, and these cannot answer it. They are recorded because they establish something the
  origin entry alone does not: the incident was the moment a standing practice got caught, not
  a single lapse. A boilerplate had been emitting the framing into every handoff for five weeks
  before anyone named the rule. The three same-day documents would in any case be fan-out from
  one drafting pass.

  **The sweep also found the discipline visibly applied**, which is the more useful signal for
  a retention question. A 2026-08 audit synthesis heads its inherited-decisions section
  `do not re-litigate; surface a fork if you must` — the card's prescribed form, granting the
  fork the card exists to protect. That is compliance, not an occurrence.

  **Open policy question, surfaced rather than decided:** neither `ADMISSION.md` nor
  `AGENTS.md` says whether pre-origin corroboration belongs in `Occasions counted`. This card
  stays `RECURRENCE-THIN` at 1 under the reading above. The other reading, that the row records
  occurrences of the failure whenever they happened, moves it to 2 and drops the label. The
  maintainer owns which reading the collection uses; the dated evidence is preserved here for
  either.

- **2026-08-23 / the same sweep, run twice, and the first run was void.** The first pass
  scanned 614 files and reported a confident zero for
  `github-pages-deploy-verification`. A positive control run afterwards showed that card's
  signature could not locate its own documented origin incident: 0 of 4 patterns matched the
  gotchas entry describing it. **The zero was uninterpretable, not a finding.** The glob was
  also missing `docs/**` recursively, so the corpus was 45 percent short.

  Re-run with corrected signatures and a passing control on every card, over 1358 files:
  `github-pages-deploy-verification` still has zero occurrences outside the collection, and
  that zero now means something. `closure-mode-at-boundaries`: one external hit, an archive
  referencing the card. `git-pull-rebase-trap`: 34 external hits, every one the card, its
  guard, its fixtures, research about it, a deliberate end-to-end demonstration, or a project
  convention warning against it — adoption, not occurrence, consistent with the insurance
  diagnosis. `im-up`: only the 2026-08-23 skipped-close already counted on `im-down`.

  **The lesson belongs to the harvest, not to this card:** a sweep that reports absences is a
  test whose negative result is the product, and it needs the same positive control any other
  negative-finding run needs. See `success-test-accepts-any-output` rule 4, which this pass
  added on the same day and then violated in its own instrument.

- **2026-08-29 / the guard-caught candidates are ruled known negatives**
  ([MrBinnacle/skills#133](https://github.com/MrBinnacle/skills/issues/133)). A 2026-08-24
  harvest surfaced two hook-block events — 2026-08-04 and 2026-08-05, each a draft carrying
  this card's forbidden framing that `guard-downstream-framing.py` refused to persist — as
  candidates for the `Occasions counted` row. A two-family adversarial panel (grok-4.6,
  deepseek-chat-v3.1; receipt in the maintainer's research repository at
  `docs/audit/t1-133-cross-family-S353/`, linked from the ticket) reviewed the proposal to
  count them and refuted it on the policy text as written.

  **The ruling, and the line that makes it repeatable:** the row counts the failure this card
  claims to fix — **forbidden framing present in a persisted artifact a later reader could
  consume**. A draft the hook refused never became that. The near-miss/precursor-event
  distinction from safety science is the governing prior art: counting the barrier's hits as
  recurrences of the accident lets the intervention's success delete its own evidence. The
  panel also flagged the laundering direction — a hook catch is evidence the *hook layer* is
  doing the work, and converting it into recurrence credit for the card inverts its meaning.

  The two dates above are therefore recorded as known negatives: the next harvest that finds
  them stops here instead of re-deriving the same candidates into the same undecided state.
  `RECURRENCE-THIN` stands at 1. The 2026-08-23 entry's open policy question (pre-origin
  corroboration) is a separate fork and remains open; so does the parallel question on `im-up`,
  where the candidate false claims were completed and persisted before a receiver falsified
  them — the stronger case, per both panel seats, and not ruled here.
