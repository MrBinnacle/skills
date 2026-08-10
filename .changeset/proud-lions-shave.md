---
"mrbinnacle-skills": patch
---

Rewrite the README's reference section so each skill says what it actually does.

Every entry described the problem the skill addresses or the principle behind it, and none
described the behaviour. "Structured wrap-up at phase boundaries" does not tell a reader
whether the skill runs tests, prints a list, or refuses to continue — so a visitor could not
tell what they would get by installing it.

Each of the nine entries now states three things in order: when it fires, what it does step by
step, and what the reader is holding when it finishes. Concrete detail — the config file a
skill reads, the script it runs, the check that has to pass before it will sign off, the exact
condition that makes it reject — is drawn from each `SKILL.md`, not summarised from the
section it replaces.

Two smaller fixes ride along. The list voice was clipped noun-stacks with a bolted-on audience
tag on all nine entries, sitting directly beneath ordinary prose; the entries are now written
the way the rest of the page is. And the ordering is now broadest-reach first within each
group, narrowing to the specialist cases, with the sentence that states the ordering rule
rewritten to match — the page previously described an order it was not using.
