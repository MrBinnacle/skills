---
name: walk-the-recipe-as-target-user
description: |
  Validation discipline for any "documented workflow" (README reproduction
  recipe, getting-started guide, install script, onboarding doc, deploy
  procedure). Simulate the ACTUAL target user's environment — different
  auth path, different SDK credentials, different OS, different tooling —
  and walk every documented step as that user would. Each step that breaks
  for the target user is real friction. Each step that silently assumes
  "you already have X set up" is an undocumented precondition. Use when:
  (1) the workflow was written by a developer whose machine has every
  privilege/credential/tool pre-configured and you're worried real users
  don't, (2) "first-touch hardening" or "on-ramp polish" or any phase
  whose stated purpose is making the workflow reachable for non-developers,
  (3) you've just changed the underlying CLI/API surface and the
  documented workflow predates the change, (4) a literal-spec adherence
  move (do the checklist items the doc names) would miss the friction the
  doc was MEANT to address. Catches the structurally-invisible
  "works-on-my-machine" failure mode that the original author cannot see.
metadata:
  type: discipline
---

# Walk the Recipe as the Target User

## Problem

A documented workflow — README reproduction recipe, onboarding script, install procedure, deploy guide — works perfectly for the developer who wrote it. They have all the credentials, all the SDKs, all the tooling already installed. They wrote the recipe by literally running the steps and confirming each one. They aren't lying about it working.

But they wrote it on a privileged-environment machine. Their `ANTHROPIC_API_KEY` is set. Their `KUBECONFIG` points to the cluster. Their `gcloud auth` is current. Their AWS SSO session is fresh. Their `node_modules` is hydrated. Their docker daemon is running.

A real user — a T1 reader, a new hire, a contractor, an external evaluator, an open-source maintainer reviewing a PR — has a DIFFERENT environment. Their version of "I cloned and tried to follow the README" is structurally different from the author's "I followed my own README."

The differences are invisible to the author because the author cannot reproduce their own absence-of-a-credential. The documented recipe stays accurate as far as the author can see, and the recipe stays broken for the real user.

The literal-spec response — "go through the 6-item hardening checklist the planning doc names" — does not catch this failure mode. The 6 items address the author's THEN-CURRENT best guess of friction. Reality friction may have moved, may include items the author never considered (because their own privilege blinded them), or may have been introduced by recent changes the doc predates.

## Trigger conditions

Apply this discipline when ANY of these hold:

1. **You're about to ship a "polished on-ramp" / "first-touch hardening" / "reproduction recipe ready for external eyes"** and the polish items came from a planning doc rather than from observing a real first-touch attempt.
2. **The workflow predates a recent change to the underlying CLI/API surface** — new flags, new env vars, new auth modes, new prerequisites that the recipe doesn't mention.
3. **The documented target user has a meaningfully different environment** from the author — different auth (subscription vs API key), different OS (Windows vs Unix), different tooling (npm vs pnpm vs yarn), different access tier (no admin, no enterprise features).
4. **A "hard right over easy wrong" prompt forces you out of literal-spec adherence** — the spec gives you a checklist; the real question is "does the recipe work for the audience it's meant to serve?"
5. **You're about to dispatch a re-implementation of items that may have already shipped** — verify against actual repo state first; the recipe may need a different fix than the planning doc anticipated.

## Solution

### Step 1 — Identify the target user profile explicitly

Don't simulate "a generic user." Name the specific environment profile the recipe is FOR. Examples:

- "A Claude Code subscription-auth user with no direct ANTHROPIC_API_KEY but OPENROUTER_API_KEY set"
- "A contractor on Windows 11 with Python 3.11 but no admin rights"
- "An external reviewer on macOS who has Docker but no Kubernetes context"
- "A new hire whose laptop has nothing pre-installed except Git"

If the recipe doesn't have a clear target user profile, that's itself the first friction: who is this FOR?

### Step 2 — Inventory the recipe's implicit preconditions

Read every step. For each, ask:

- "What env var does this assume is set?"
- "What credential does this assume is valid?"
- "What SDK does this assume is installed?"
- "What tool does this assume is in `PATH`?"
- "What service does this assume is reachable?"
- "What state does this assume already exists (DB, file, config)?"

The author probably didn't list these. They are the failure modes for any user who doesn't share the author's privileged baseline.

### Step 3 — Walk the steps mentally (or actually) as the target user

For each step, ask: "If I were the target user, would this work?"

- If yes: move on.
- If no: WHY does it fail? Missing credential? Missing tool? Missing precondition? A wrong assumption baked into the recipe? Each failure is a real piece of friction the doc must address.
- If unsure: note it explicitly. Don't assume it works.

If you can actually execute the recipe in a target-user environment (sandbox, VM, fresh container, disabled credentials), do so — observed reality beats imagined reality. Even imagined-only is much better than not asking.

### Step 4 — Catalog the gaps

For each piece of friction, classify:

- **Documentation gap**: the recipe should have warned about / documented / provided alternative for this precondition. Fix in docs. Cheap.
- **Engineering gap**: the recipe's assumption is wrong for the target user, and no documentation workaround exists; the code needs to change. More expensive; may require dispatch.
- **Author-blindness gap**: the recipe is plausible but the author never noticed it fails for the target user because the author's environment can't reproduce the failure. Same fix as the above two, but flag the meta-pattern for future recipes.

### Step 5 — Apply the appropriate response

For documentation gaps: inline doc edits, single cohesive commit. (See `[[two-phase-doc-honesty-then-engineering]]` for the pattern when both doc and engineering gaps surface together.)

For engineering gaps: standard engineering dispatch via `[[subagent-driven-development]]`.

For author-blindness: document the meta-pattern in the project's session-log so future polish passes don't re-introduce it.

## Verification

You applied this discipline correctly when:

1. The target user profile is NAMED in the catalog (not "generic user").
2. Every documented step has been walked through that profile's lens.
3. The friction list includes things the original planning doc didn't anticipate — the doc was a best-guess from the author's view, not the ground truth from the user's view.
4. At least one of the documented "completed" items turns out to need a different fix than the doc named (because reality moved since the doc was written, or because the doc's framing was author-eyed).
5. The recipe, after the fixes, actually works in the target-user environment (verified by walking it again or by an actual run).

You misapplied this discipline when:

- You walked the recipe as YOUR OWN environment again, not the target user's. (Same author-blindness, different excuse.)
- You stopped after fixing the literal-spec items the planning doc named.
- You treated "the recipe runs in my dev shell" as evidence "the recipe works."
- You didn't catalog the implicit preconditions — you just spot-fixed the most obvious issue.

## Example

From the skill-harness 2026-06-09 session:

The SOP doc `docs/dispatch/post-v0.1-signal-acquisition-plan.md` §#2 listed 6 punch items for "first-touch hardening" — written 2026-06-08 from the author's view. The doc had been substantially completed in commit `09af6ae` (5/6 items + 1 partial).

The literal-spec response would be: do item 5 (the partial), update the SOP doc to ✅, ship.

The user invoked "hard right over easy wrong." The hard right was to walk the documented `reproduce-case-study.ps1` recipe as a Claude Code subscription-auth user — the case-study author's own profile, named explicitly in the case study as "HALT 2." This profile has `OPENROUTER_API_KEY` set, no `ANTHROPIC_API_KEY`.

Friction surfaced that the SOP doc did not anticipate:
- `reproduce-case-study.ps1` hard-refused on missing ANTHROPIC_API_KEY with no helpful message (author-blindness — author had the key, never saw the failure)
- README's reproduction recipe said nothing about OpenRouter or the W2 fallback (recipe predates the recent CLI change)
- The script didn't expose `--subject-model` even though W2 added it (recipe predates the change)
- The case study's own author cannot reproduce the case study with current code, because `skill init` (extractor) is Anthropic-direct-only and they have no key

The doc-honesty pass and the extractor OpenRouter fallback engineering dispatch BOTH came out of this walk. Neither was on the original 6-item punch list. The literal-spec response would have shipped a polished recipe that STILL didn't work for the case-study author's own machine — a self-reproducing failure mode in the case-study reproducibility itself.

## Notes

- The author cannot do this discipline reliably on their own work — they have the environment that makes the recipe work, by definition. Best results come from someone who genuinely has the target environment (a different team member, an external reviewer, a fresh sandbox). Second-best is the author deliberately simulating with discipline.
- For each project, the target-user profile is project-specific. Don't import "the canonical T1 user" from a different project; derive from the artifact's documented audience.
- This discipline composes with `[[halt-as-deliverable]]` — the walk often catches things that, once surfaced, are themselves uncopyable credibility signals ("we noticed our own recipe was broken for our own author's profile") if the project is in a phase where that signal matters.
- Don't use this discipline as a stick to beat documentation authors with. The author-blindness pattern is structural, not a personal failing. The fix is the walk, not the blame.
- For very small recipes (single command, no preconditions), the discipline is overkill. Use when the recipe has multiple steps and meaningful prerequisites.

## See also

- `[[two-phase-doc-honesty-then-engineering]]` — the execution response when this walk surfaces both doc gaps and engineering gaps.
- `[[halt-as-deliverable]]` — the narrative reframing when the walk catches something publicly worth catching.
- `[[downstream-instruction-framing]]` — applies when writing the recipe in the first place: frame for a less-informed reader operating closer to the evidence than you are.
- `[[strategic-frame-audit-no-twin-product]]` — sibling discipline at the strategic level: when there's no competitor product to copy a recipe from, the walk discipline becomes more important because no external recipe will catch your gaps for you.
