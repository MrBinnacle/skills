---
"mrbinnacle-skills": minor
---

The release gate answers whether the repository is fit to release, not only whether one surface is fresh.

Three checks join the manifest-version lockstep check (#149) as siblings in `scripts/release_gate.py`, each behind a refusal this repository or its sibling actually earned:

- **G2 - the plan assembles.** Every pending `.changeset/*.md` must name a package the workspace contains, and unreadable frontmatter is refused the same way `changeset version` would refuse it. This is the gate's own unscoped `changeset status`: the scoped `--since=origin/main` form examined an empty set whenever it ran on `main`, which is how a misnamed package kept CI green from 2026-08-24 while blocking every release (#144 fixed CI; G2 gives the gate its own verdict).
- **G3 - nothing left unconsumed at release time**, in the new `--release` mode. Between releases, pending changesets are the process working; at the merge of the version bump they are fatal, because a file left behind means some change silently misses the release it was filed against.
- **G4 - a dated changelog section for the released version.** The version `package.json` declares must appear under a `CHANGELOG.md` heading that carries a date; a sibling repository tagged a release whose section had never been rolled.

Failures are listed together, not first-fail: one tree failing all three shows all three in one run. Each check ships a poison control in CI that plants exactly its own fault and requires the message naming it. The argument-less command keeps answering "are the surfaces healthy today", so it still passes while changesets legitimately accumulate between releases.
