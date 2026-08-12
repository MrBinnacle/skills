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
