---
name: decision-rights-issue-bodies
description: About to write issue bodies that instruct a downstream agent, with some decisions settled and others open. Seed case 3 of five from 2026-09-12.
expected_outcome: The agent invokes mrbinnacle-orchestration:decision-rights. Description coverage is PARTIAL and this is pre-registered. The card names "handoffs, plans, ADRs, subagent prompts"; an issue body is not on that list, though it is the same artifact class. A miss here is evidence about the card's description, not about the model.
tags: [seed, should-fire, mrbinnacle-orchestration, partial-coverage]
plugins: ["../.."]
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

I am writing up three pieces of work as issues. Another agent picks them up
cold and implements them without me in the loop, so the issue body is the only
thing it gets.

The three:

- Replace the hand-rolled CSV parser in the importer with a library.
- Split the `Account` model, which currently carries both billing and auth.
- Backfill the `last_seen_at` column, which is null for everyone created before
  March.

On the second one we already settled that billing moves out and auth stays, and
I do not want that reopened. On the first one the library choice is genuinely
open. On the third I am not sure whether a backfill or a lazy default is the
right shape, and whoever picks it up will know more than I do once they have
looked at the row counts.

Draft the three issue bodies.
