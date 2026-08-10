---
"mrbinnacle-skills": patch
---

Fold the doctrine that has evolved in the maintainer's live operating rules back into the
published `CLAUDE.md`, and fix a companion list that had gone stale.

The published file was written self-contained at v1.0 and has not moved since, while the live
file it came from kept changing. This ports what actually changed, rather than replacing the
file — the published version holds expanded prose the live one has since compressed behind
pointers to a private reference, and a straight copy would have lost it.

What is new:

- **§0** — a project delta may pin a standing model for its sessions; when it does, the delta
  wins over the frontier-vs-fast heuristic. `im-up` and `im-down` are named as one
  implementation of the state load and the state write.
- **§0.6** — the per-project fluency profile: a delta can declare which domains the user owns
  and which the agent researches and recommends in, which is what makes the
  is-this-really-a-values-decision test cheap to apply. The values-decision marker is now named
  (`[values decision]`) rather than described.
- **§0.7** — the full twenty-role roster, inline. It was truncated to ten roles and an "and so
  on", which is not a roster anyone can work from.
- **§1.5** — three authoring conventions that were missing: a visible description is a standing
  cost paid every session whether the skill fires or not, so budget the collection rather than
  each description alone; frame a skill around what must be true before an action rather than a
  fixed script, with discipline skills as the stated exception; and structure a long directive
  skill as problem / supporting information / steps, tuning loudness before adding rules.
- **§11** — `im-down` named as the write side of the checkpoint, `im-up` as the read side.
- **§14 (new)** — keep a quick-reference of the skills you have to remember on purpose,
  organized by the moment you reach for them, listing only what the reader can actually run.
  Skills that fire on an error are excluded: the failure surfaces them.

What was deliberately not ported:

- The `/loop` loop-survival detail. `AGENTS.md` already carries it, better adapted to this repo.
- The maintainer's private skill roster. Naming skills a reader cannot install is the dead-pointer
  failure this collection fixed in its evidence records last release; §14 states the rule instead.
- The session-close carve-out from the private conventions, which exempts a close ritual from
  `disable-model-invocation`. This collection ships `im-down` with it set, so publishing the
  carve-out as doctrine would contradict what is in the box.

The companion list named seven skills; nine ship. `im-down` and `im-up` were missing, and
`closure-mode-at-boundaries` was filed under error-triggered traps when it is a human-invoked
procedure. The list is now grouped by when you would reach for a skill instead of by bucket.
