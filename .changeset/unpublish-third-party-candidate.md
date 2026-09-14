---
---

chore: remove the third-party `self-documenting-code` candidate from `_quarantine/`.

The card is authored by theswerd and was landed from the public `theswerd/aicode`
repository on 2026-09-06 under #216. The owner ruled on 2026-09-14 that it is not
published and is kept as a measurement subject for the local harness only.
`dispositions/2026-09-04-S404-notion-proposal-review.md:206` had already settled
the narrow form of the question for a different upstream-owned skill: compose it,
do not republish another author's skill under this collection's identity.

Both copies are archived outside every git repository with per-file digests. The
canonical upstream install is preserved because `PROVENANCE.md` established that
the frozen baseline #216 criterion 5 asked for was never at HEAD in either form.

`_quarantine/` is not part of any published plugin: the marketplace manifest does
not reference it and the package is private. So no package behaviour changes, this
changeset is empty, and the release is not bumped by it.
