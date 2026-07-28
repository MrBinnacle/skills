# Changesets

This folder is used by [`@changesets/cli`](https://github.com/changesets/changesets) to
version the collection and generate the changelog.

**When you make a change worth recording**, add a changeset:

```bash
npx changeset
```

Pick the bump (patch / minor / major) and write a short, human-readable summary. The file it
creates in this folder is committed with your PR and merged to `main` alongside the change.

**Cutting a release** is a deliberate, manual step (there is no auto-release CI). When you want
to roll the pending changesets into a version, run:

```bash
npm run version
```

That consumes every pending changeset, bumps `package.json`, and rewrites the `## <version>`
section of `CHANGELOG.md`. Commit the result; tag it by hand if you want a tag.

Note: distribution is via the `npx skills add MrBinnacle/skills` installer, which tracks
`main` — so versions and tags are an informational reading aid, not a pin consumers resolve.
The value here is disciplined, per-change changelog notes and a mechanical version bump, not
package publishing (the package is `private`).
