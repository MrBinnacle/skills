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

- **2026-08-23 / corpus harvest across 28 project directories, 614 files:** a rotation pass
  searched every reachable session record and handoff for this card's origin failure. It found
  the pattern institutionalized in a second, unrelated project: four phase-handoff documents
  each carrying a `## DECISIONS ALREADY MADE (do not re-litigate)` section, and a planning
  boilerplate that templates it, so every handoff generated from it inherits the framing.

  **These are dated 2026-04-29 (three of them, one drafting pass), 2026-05-02, and 2026-06-02
  for the boilerplate. All of them PREDATE this card's 2026-06-07 origin, and none is counted
  as an occasion.** Recurrence means the failure happened again after the discipline existed;
  that is the question `Occasions counted` exists to answer, and these cannot answer it. They
  are recorded here because they are evidence of a different and useful kind: the origin
  incident was not a one-off misstep but the moment a standing practice got caught. A
  boilerplate had been emitting the refused framing into every handoff for five weeks before
  anyone named the rule.

  The three same-day documents would in any case be fan-out from one drafting pass, which
  criterion 2 already refuses to count separately.

  **Open policy question, surfaced rather than decided:** neither `ADMISSION.md` nor
  `AGENTS.md` says whether pre-origin corroboration belongs in `Occasions counted` at all.
  This card stays `RECURRENCE-THIN` at 1 under the reading above. A different reading, that
  the row records occurrences of the failure regardless of when the card was written, would
  move it to 2 and drop the label. The maintainer owns which reading the collection uses. The
  evidence is preserved here either way.

  **Negative results from the same sweep, recorded because an unsearched card and a searched
  card with no finds are not the same claim.** `closure-mode-at-boundaries`: no occurrence
  outside the card's own files. `github-pages-deploy-verification`: zero matches anywhere in
  the corpus. `git-pull-rebase-trap`: 28 matches, every one of them the card, its guard, its
  fixtures, research about it, or a project convention citing it, which is adoption rather
  than occurrence and is consistent with the insurance diagnosis. `im-up`: the only hit is the
  2026-08-23 skipped-close already counted on `im-down`; counting it twice would be the
  fan-out the policy refuses.
