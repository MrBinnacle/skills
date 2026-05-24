# Swarm Composition

The standard SME swarm for closure mode at workflow boundaries. Each agent ranks the candidate set with one-paragraph rationale per candidate and at least one cross-cutting flag.

## Roster (5 roles, role-based)

| Role | Purpose |
|---|---|
| **Architect** | Initiative-level verdict per candidate; cross-fork sequencing constraints; primary-reference check (is the citation actually the best work on the problem, or just the first thing in this codebase?) |
| **Security** | Trust-contract impact per candidate; residual-risk delta; flag if any candidate needs its own pressure-test pre-flight |
| **Planner** | Sequencing; base-rate fit; natural pairings with open work items; momentum-window decay |
| **Critic** | Frame-rejection — what is MISSING; false-precision check on cost estimates; phantom-dependency verification |
| **Domain SME** | First-principles read for any in-scope domain (UI designer, DB schema reviewer, ML systems reviewer, etc.) |

The named SME for any in-scope domain MUST be in the swarm. Generic agents do not substitute.

## Role-to-runtime mapping

Different agent runtimes have different built-in role subagents. Map closure-mode roles to your runtime's nearest equivalent.

| Role | OMC plugin (oh-my-claudecode) | Native Anthropic Claude Code | Codex / Gemini | Fallback: prompt a general agent into the role |
|---|---|---|---|---|
| Architect | `oh-my-claudecode:architect` | named `architect` subagent | architect mode / role prompt | "You are a strategic architect. Evaluate each candidate for initiative-level risk and cross-fork sequencing. Apply a primary-reference check: is the citation the best work, or the first thing found?" |
| Security | `oh-my-claudecode:security-reviewer` | named `security-reviewer` subagent | security review mode | "You are a security lead. Evaluate each candidate's trust-contract clause impact, residual-risk delta, and any pre-flight pressure-test requirement before drafting." |
| Planner | `oh-my-claudecode:planner` | named `planner` subagent | planning mode | "You are a sprint planner. Evaluate each candidate's sequencing, base-rate fit, and natural pairings with open work items. Flag muscle-memory window decay where relevant." |
| Critic | `oh-my-claudecode:critic` | named `critic` subagent | adversarial review mode | "You are an adversarial critic. Reject the FRAME, not just rank within it: what is MISSING from this candidate list? Then run a false-precision check on every cost estimate and verify any dependency claim by grep." |
| Domain SME | varies per domain | varies per domain | varies per domain | "You are the named SME for {domain}. Apply first-principles reasoning to each candidate; refuse if you would not stake your reputation on the recommendation." |

Concrete copy-pasteable prompts for each role with brackets for project-specific context are in [prompt-templates.md](prompt-templates.md).

## Minimum viable swarm

If you have only 2 agents available — single-engineer project, expensive parallel dispatch, runtime limits — the **minimum viable swarm is Critic + Architect**. These two together catch the most common frame failures:

- Critic surfaces phantom claims, missing candidates, and false-precision costs.
- Architect catches sequencing constraints and Bannister-failure primary references.

The other three roles are valuable but not mandatory. A 2-agent swarm catches most of the failure modes that a 5-agent swarm catches; a 0-agent "let me just pick" closure run catches none of them.

## Per-agent prompt requirements

Every prompt must include:

1. **Self-contained context.** Stack summary, last-completion identifier, recent commits, relevant open items. Agents start cold — no shared session context.
2. **The candidate set verbatim.** Copy from wherever the candidates were authored. Do not paraphrase.
3. **The SME role.** Name the lens explicitly: "You are the security-lead SME consulted on a fork-pick decision."
4. **The ask:**
   - Rank candidates with one-paragraph rationale per candidate.
   - Surface at least one cross-cutting flag — sequencing constraint, hidden coupling, frame challenge, phantom claim, false precision.
   - Keep responses focused; a word budget helps.
5. **The Critic carve-out.** The Critic is specifically assigned frame-rejection: "what is MISSING from this list?" The Critic's value at a boundary is rejecting bad frames, not just ranking within them.

[prompt-templates.md](prompt-templates.md) provides ready-to-fill templates for each role.

## Dispatch shape

Send all SMEs in a single message with parallel agent calls. Do not serialize — they should not see each other's output. Parallel dispatch is what makes the swarm cheap enough to default to.

If your runtime does NOT support parallel agent dispatch in a single message, serialize the swarm but cache each agent's verdict before invoking the next. Serial dispatch is more expensive but the discipline still applies.

Capture each verdict. Proceed to [transition.md](transition.md) — the step that turns N voices into an executed action list.
