intentional-landing: true

Landed 2026-09-07 by the S428 close, untracked since it was authored (frontmatter
`date: 2026-09-06`, version 1.0.0). Three files: `SKILL.md`, `gotchas.md`, `worked-case.md`,
12,560 bytes together.

This candidate's origin is not recorded. The S427 checkpoint band states that no band, session
packet or log names it, and that was measured rather than assumed. The other three candidates
landing in this commit were each named in a band before they were written. This one was not, and
nothing found since establishes where it came from.

That absence is a reason to land it and review it, not a reason to leave it untracked. An
unattributed card sitting in the working tree cannot acquire provenance; a tracked one has at
minimum the commit that landed it. The gap is recorded here so a later review starts from the
known state rather than from a guess.

Landing is not admission. No section 1.5 review, no `EVIDENCE.md`, no occasions counted.
`_quarantine/` is not published: the plugin manifest names 14 paths and none is under this
directory.
