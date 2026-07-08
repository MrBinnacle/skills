# Modes B & C — library audit and absence detection

## Mode B — Library audit / anti-bloat
Use when a skill library feels heavy or you suspect the description budget is overflowing.

1. **Measure the standing cost.** Count model-invocable skills (those WITHOUT
   `disable-model-invocation: true`). Each loads ~100 description tokens always. Compare to
   the budget (~1% of context ≈ ~2k tokens on a 200k window). If model-invocable-count × 100
   ≫ budget, Claude Code is truncating/dropping least-used descriptions — some skills are
   silently undiscoverable. Confirm with `/doctor` / skill diagnostics.
2. **Reclaim budget cheaply.** For every skill you always trigger by hand (procedures,
   side-effecting workflows), set `disable-model-invocation: true`. Safe, immediate win, zero
   behavior loss for skills you invoke explicitly.
3. **Find merge candidates (GD-4).** Cluster skills by domain; overlapping clusters that get
   used together are merge candidates (e.g. many near-duplicate frontend/design skills). Not
   all must merge — but N always-loaded near-duplicate descriptions is the GD-2 tax made real.
4. **Retire rot.** Retire a skill when: statelessness makes it re-explain context every run
   (needs state, or a merge) · it encodes volatile decisions (current libs/services) that rot
   and burn tokens each request · its always-on description cost exceeds its firing frequency
   (→ `disable-model-invocation` or remove).
5. **The nuclear option (Pocock's blank-slate reset).** Periodically delete everything —
   skills, plugins, MCP servers, global CLAUDE.md — run the raw agent, and re-add ONLY the
   guardrails that prove actually necessary. Libraries accrete; the reset is the counter-force.

## Mode C — Absence detection (what skills are MISSING?)
Use to find skills that should exist but don't. The signal is repetition-without-crystallization.

**Signals, in priority order:**
1. **Repetition-without-crystallization** — the same reasoning / prompt / multi-step
   instruction performed manually across distinct sessions.
2. **"Freaking often" friction** — the felt annoyance of re-typing something.
3. **Workflow-merging** — two skills you always run together → a missing combined skill.
4. **Too-simple dismissals** — candidates rejected for being trivial; re-examine on frequency.

**Instrument (make it empirical):**
- Park candidates in the skills folder; count reach-for-it frequency; promote the frequent ones.
- Mineable from a session corpus: scan for repeated prompt shapes / repeated tool-call
  sequences → surface candidates.
- Run each surfaced candidate through Mode A (Gate 0 especially — many "absences" are
  mis-layered facts, not missing skills).

**Meta-caution:** absence detection can become "produced N candidates, therefore thorough."
The output that matters is *promoted skills that passed the Gate 2 worth eval*, not candidate count.
