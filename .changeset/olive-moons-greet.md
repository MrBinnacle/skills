---
"mrbinnacle-skills": minor
---

Rename the session-boundary pair to `im-down` (producer, session close) and `im-up` (receiver,
session start). The old names described the machinery; these describe what the operator is
actually doing — signing off, and coming back. They also resolve a real collision: the previous
receiver name was identical to a widely-installed local skill of the same name, so the two
could not coexist in one library.

No behavior changes. Directory names, frontmatter `name:` fields, bucket README, top-level
README, and the pair's own cross-references all move together, and the validator drift
assertion tracks the new directory names.
