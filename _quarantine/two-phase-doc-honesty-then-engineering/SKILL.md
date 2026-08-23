---
name: two-phase-doc-honesty-then-engineering
description: |
  Response pattern after a state-drift catch surfaces BOTH doc inaccuracies
  AND a deeper engineering gap the docs were obscuring. Split the response
  into two phases that ship on different cadences: Phase A is an inline
  doc-honesty commit (truthful documentation of current state, orchestrator-
  direct, no authorization needed). Phase B surfaces the engineering gap to
  the PM as a separate dispatch decision (needs greenlight, costs more
  agent budget). Both ship; neither blocks the other. Use when: (1) a stale
  planning doc / spec / handoff catches mid-task and you're about to either
  silently re-do already-shipped work OR ship a doc-only fix that papers
  over a real engineering gap, (2) a "hard right over easy wrong" prompt
  forces you out of literal-spec adherence, (3) any catch where the
  documentation truth is small/fast and the engineering follow-on is
  larger/needs-authorization. Sibling to halt-as-deliverable (which covers
  the reframing of the work product); this skill covers the execution
  response after the catch is named.
metadata:
  type: pattern
---

# Two-Phase Response: Doc-Honesty Inline, Engineering Dispatched

## Problem

A state-drift catch (the documented plan says X is PENDING but reality is X is DONE; the docs promise Y but the code can't deliver Y for the named target user; the case study cites a number that's no longer reproducible) surfaces TWO different kinds of work:

1. **Documentation inaccuracy** — the docs misrepresent current state. Fixing this is a few edits to README / examples / case-study / SOP doc. Fast. Low blast radius. No authorization needed beyond standard commit discipline.
2. **Engineering gap** — the docs were obscuring a real code-level limitation. Fixing this requires actual implementation work, possibly a subagent dispatch, possibly meaningful cost, definitely PM authorization in a budget-conscious context.

If you bundle (1) and (2) into one effort, you either:
- Wait on (1) because (2) needs authorization that hasn't arrived yet, leaving the docs lying to readers for hours/days
- Pre-emptively dispatch (2) without authorization, violating the spend / scope discipline
- Skip (2) and ship (1) as if the doc-honesty pass "closed" the issue, which it didn't — it just made the lie visible

If you bundle them, you also create one commit / one push / one PR / one review cycle where there should be two — confusing the audit trail of what changed and why.

The two-phase pattern keeps the responses cleanly separated by their natural cadence.

## Trigger conditions

Apply this pattern when ALL of these hold:

- A state-drift catch has fired (HALT-as-deliverable applies upstream of this skill — see `[[halt-as-deliverable]]` for the reframing step)
- The catch surfaces BOTH (a) wrong/stale documentation AND (b) a deeper code-level gap that the docs were obscuring or papering over
- Phase A (doc honesty) is well-scoped and doesn't need authorization (orchestrator-direct edits to README/examples/specs)
- Phase B (engineering work) is meaningfully larger and crosses a "needs PM authorization" boundary — meaningful agent budget, new external surface, code that changes user-visible behavior, scope that wasn't on the previously-greenlit list
- You can ship Phase A NOW without Phase B and the docs become honest about the gap (Phase B is then queued, not blocking)

If only (a) — just do the doc-honesty pass alone. If only (b) — just dispatch the engineering work. The two-phase pattern is specifically for the both-present case.

## Solution

### Phase A — Doc-honesty pass (immediate, inline)

Single cohesive commit that brings the docs into truthful alignment with current reality:

1. Update every stale assertion to reflect current state. If a SOP doc says "PENDING" but reality is "DONE in commit X", change it to "✅ DONE in commit X". If a README claims "17 UNMEASURED clauses" but the relevant counts have shifted, replace with the current accurate framing.
2. Where Phase B's engineering gap is visible to users, NAME IT in the docs honestly. Don't paper over it. Example: "API X requires environment variable Y; there is no fallback yet for users without Y (v0.2 backlog candidate)."
3. If Phase B is going to land soon, the doc-honesty pass can SAY SO with calendar context. Don't promise a date; say "queued for the next dispatch decision."
4. Single cohesive commit per `feedback-commit-shape`. Commit message references the state-drift catch (the upstream trigger) and lists each file changed.
5. Push immediately. The truthful docs are the deliverable for Phase A.

### Phase B — Engineering dispatch (separate, authorized)

Surface to PM as a closed-form question with:

1. **What the engineering work is** — specific code change, scope estimate (LOC, files touched), dispatch shape (which model, which worktree pattern)
2. **Why it matters now** — what user-visible behavior changes, what the case for / against doing it post-Phase-A is
3. **Cost estimate** — agent budget, API budget if applicable
4. **Recommendation** — say what you'd do; let PM accept/reject

If greenlit: dispatch via the standard subagent-driven-development pattern (implementer → spec review → quality review → fix cycle if needed → merge). Same shape as any normal engineering dispatch; only the trigger is unusual.

If not greenlit: the docs from Phase A still tell the truth about the gap. The codebase reality is unchanged. The catch surfaced the gap; the PM chose not to invest. That's a valid outcome.

### What you GAIN from splitting

- **Doc readers get the truth immediately.** A T1 reader who clones the repo while Phase B is queued sees honest docs naming the gap, not a stale promise.
- **PM gets a real decision to make**, not a fait accompli. The Phase B authorization question is separate from "do you want the docs to be accurate?" (the answer to which is always yes).
- **Audit trail is clean.** Phase A commit reads as "doc honesty pass"; Phase B commit reads as "feat: close the gap." Each can be reviewed on its merits.
- **You can ship Phase A even if Phase B never happens.** Sometimes the engineering work isn't worth doing yet; Phase A still has value because it stops the docs from lying.

## Verification

You applied this pattern correctly when:

1. Phase A commit ships and the docs are observably more truthful — a fresh reader can see the current gap rather than the stale promise.
2. Phase B is surfaced as a discrete question with the four elements above (what / why / cost / recommendation), not embedded mid-task as "should I just go do this thing too?"
3. The commit history shows two separate commits / two separate dispatch decisions, not one bundled commit.
4. If Phase B was eventually greenlit, the Phase A doc-honesty pass had to be UPDATED post-Phase-B to remove the "queued / backlog" hedges and replace with "fixed in commit Z." This update IS the close-the-loop signal that the cycle ran clean.

You misapplied this pattern when:

- You shipped Phase A and called the issue closed (even though the engineering gap is still there)
- You bundled both into one commit that the PM can't selectively approve
- You skipped Phase A and went straight to Phase B (the docs continued to lie during the dispatch window)
- You surfaced Phase B BEFORE shipping Phase A (the docs stayed stale while waiting on PM)

## Example

From the skill-harness 2026-06-09 session, second-half:

State-drift catch: SOP doc `docs/dispatch/post-v0.1-signal-acquisition-plan.md` §#2 marked 6-item first-touch hardening punch list as PENDING. Reality (commit `09af6ae`, 2026-06-08): items 1-4 + 6 already shipped. Item 5 was partial (legend defined but placed under wrong command's output). Walking the documented reproduction recipe as a T1 reader on Claude Code subscription auth surfaced a deeper gap: the extractor on `skill init` was Anthropic-direct-only and couldn't run for the case-study author's own environment profile, which the case study itself documented.

**Phase A** — commit `6c9ff3f`:
- Updated SOP doc item-status from PENDING to ✅ DONE
- Updated README's stale "17 UNMEASURED clauses" claim
- Added README "API-key requirements" subsection naming the extractor / run-ablation asymmetry honestly
- Rewrote `reproduce-case-study.ps1` ANTHROPIC_API_KEY missing-key error message to name the gap + workarounds
- Updated case-study closing paragraph from "are queued and will land" to "landed in [commits]" + named the remaining extractor gap as v0.2 candidate
- Item 5 legend placement fix
- Softened unverified `npx skills add` claim in `ai-slop-sentinel-pointer.md`
- Single cohesive commit, +104/-14 across 7 files, orchestrator-direct
- Pushed immediately

**Phase B** — surfaced to PM with: scope, dispatch shape (Sonnet 4.6 implementer in worktree, single cohesive commit, ~2-3 hours agent work), URL-verification risk note, recommendation. PM greenlit.
- Implementer commit `b5b9fe6` + fix-cycle `7d86687`
- Spec + quality + re-review all clean
- FF-merged to main
- Case-study author can now reproduce the case study end-to-end on subscription-auth
- Updated checkpoint + case study to reflect the close-the-loop ("queued candidate" → "landed in commits b5b9fe6 + 7d86687")

The audit trail reads cleanly: state-drift catch → Phase A doc honesty → PM greenlight → Phase B engineering → close-the-loop documentation.

## Notes

- This skill is the *execution response*; the *narrative reframing* of the catch is the domain of `[[halt-as-deliverable]]`. Both apply when discipline catches something the author missed; they answer different questions ("how do we ship this?" vs "what does this become?").
- For catches that DON'T surface an engineering gap (just stale docs), skip Phase B entirely. Just do the doc-honesty pass.
- For catches where the engineering work is small enough to bundle with the doc fixes AND doesn't cross an authorization boundary, the two-phase split adds overhead. Use single-commit bundle instead. The pattern is for the both-meaningful case.
- The "PM authorization" boundary is project-specific. In a solo project, it might be "I am the PM and I decide." In a structured project, it might be a documented owner map (per skill-harness's `docs/dispatch/post-v0.1-signal-acquisition-plan.md` line 252). The skill works either way — just apply your project's authorization rule.
- Don't let Phase B's engineering work block Phase A's doc honesty. The whole point of splitting is that the docs become honest FAST while the engineering work proceeds on its own cadence.

## See also

- `[[halt-as-deliverable]]` — the upstream skill: when discipline catches author's own mistake, the catching itself becomes the deliverable. Two-phase applies when the deliverable-of-the-catch is "now we know about gap Y; fix in two steps."
- `[[downstream-instruction-framing]]` — apply when drafting the Phase B brief for a downstream agent or contractor. The brief itself is an artifact for a less-informed reader.
- `[[subagent-driven-development]]` — the standard pattern for Phase B engineering dispatches (implementer + reviews + fix cycle).
