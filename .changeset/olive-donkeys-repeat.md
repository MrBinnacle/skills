---
"mrbinnacle-skills": patch
---

Take the skill names out of the CLAUDE.md template, and finish dropping the slogan.

The published `CLAUDE.md` is a template adopters copy wholesale into their own
`~/.claude/CLAUDE.md`. Its §14 tells them: "list only what the reader can actually run —
naming a skill they don't have costs them context and teaches them to distrust the rest of
the list." The file then broke that rule five times in its own numbered sections, naming six
skills from this collection inside rules the adopter is meant to run, each hedged "(in this
repo)". Copy the file without installing the collection and five of your operating rules
point at things that don't exist.

- §0 and §11 named `im-up` / `im-down` while describing the session load and the checkpoint
  write. The rule that actually matters there is that the two are one mechanism in two
  halves, so the sections now say that instead.
- §1 named `skill-necessity-gate`. It now states the test itself: settle whether something
  should be a skill at all before authoring one, because a skill that fails that question
  still taxes context every session.
- §4 named `downstream-instruction-framing`, `parallel-review-disposition-schema` and
  `subagent-research-reliability` in three bullets that existed largely to point at them.
  Each bullet now carries its own discipline directly — no blanket "don't re-litigate"
  framing, fix a shared output schema before parallel verifiers run, confirm a research
  subagent's tool grant includes web tools before dispatch because one without them answers
  from memory and reads identically.

Nothing is lost for a reader who does have the collection: all nine skills are still listed
under **Companion skills in this repo**, below the horizontal rule, where a heading scopes
them. The header now says which part of the file is the template and which two sections are
this repo's worked examples, so the copy boundary is visible rather than inferred.

`AGENTS.md` picks up the constraint as a repo convention, so a future edit doesn't quietly
reintroduce it — and notes that `AGENTS.md` itself is under no such restriction, since it is
never copied anywhere.

Also corrected: `CLAUDE.md` and `AGENTS.md` each described the template as "the doctrine this
repo runs on." It is a template the repo publishes; `AGENTS.md` is what governs work inside
the repo. The README's half of this was fixed when the front page was rewritten.

Finally, the three remaining sites of the retired "earn its keep" tagline are gone —
`RETIRED.md` (twice) and the pull request template — which the front-page rewrite had
deliberately left for a separate pass. The epigraph in `RETIRED.md` keeps its actual claim:
a list that shrinks when the models improve is the one telling you the truth about which
skills the model still needs.
