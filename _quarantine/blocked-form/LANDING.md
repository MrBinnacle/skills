intentional-landing: true

Landed 2026-09-07 by the S428 close, untracked since it was authored (frontmatter
`date: 2026-09-07`, version 1.0.0). One file, `SKILL.md`, 6,392 bytes.

Landing is not admission. This candidate has had no section 1.5 authoring review, carries no
`EVIDENCE.md` and no `gotchas.md`, and counts no occasions. It is landed because untracked
working-tree state is the worse of the two available states: it has no history, no gate reads it,
no reviewer can see it, and while it sits untracked it fails `release_gate.py` G9 and blocks every
release of this collection.

`_quarantine/` is not published. `.claude-plugin/marketplace.json` names 14 paths and none of them
is under this directory, so nothing here reaches a reader who installs the collection.
