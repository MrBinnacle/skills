---
"mrbinnacle-skills": patch
---

Rewrite the front page from scratch, and drop the slogan from the artwork with it.

The previous README opened with a tagline ("skills that have to earn their keep — with the
receipts to prove it") that also sat inside both banner SVGs, so the page was doing its
positioning with a slogan rather than with what the collection has actually found. The new page
is written from the sources instead:

- Opens with the question the collection came from, in the first person, with no tagline.
- Puts findings before features. The first substantive section says plainly that every one of
  the nine evidence records reads `UNMEASURED` on both controlled fields, that the admission
  screen turned away four of four candidates in July 2026, and that one shipped skill has
  already retired against its own pre-registered trigger.
- Removes the duplication. Every skill used to be described twice — once under a failure-mode
  heading and again in the reference section. The reference entries stay, keeping the three
  beats each (when it fires, what it does step by step, what you hold when it finishes); the
  failure-mode material is now a short passage on where the nine came from.
- Corrects the hand-invoked explanation. The page said the four hand-invoked skills are marked
  that way because "each one decides something you should stay in charge of," which states a
  preference as a rule and contradicts `skill-necessity-gate` at Gate 3. It now says what the
  frontmatter flag does, names the shipped default and the trade behind it, and tells the
  reader it is one line to delete.
- Corrects how `CLAUDE.md` is described. It is a template to copy, not documentation of the
  doctrine this repo runs on.
- Adds a "what this isn't" section and a reciprocal pointer to the harness repo.

Both banner SVGs lose the slogan and carry the collection's actual counts instead: 9 kept, 1
retired, 4 turned away at the gate. `RETIRED.md` and the pull request template still contain the
phrase and are left for a separate cleanup.
