# Changesets

This folder is used by [`@changesets/cli`](https://github.com/changesets/changesets) to
version the collection and generate the changelog.

**When you make a change worth recording**, add a changeset:

```bash
npx changeset
```

Pick the bump (patch / minor / major) and write a short, human-readable summary. The file it
creates in this folder is committed with your PR and merged to `main` alongside the change.

**Cutting a release** is a deliberate step (there is no auto-release CI). The merge of the
version-bump pull request is the delivery event — changed cards reach installed users then,
not when a tag is pushed. See [AGENTS.md](../AGENTS.md) step 4 and
[ADR 0002](../docs/adr/0002-a-release-is-a-delivery-event.md).

When you want to roll the pending changesets into a version, run:

```bash
npm run version
python scripts/release_gate.py --write
```

`npm run version` consumes every pending changeset, bumps `package.json`, and rewrites the
`## <version>` section of `CHANGELOG.md`. `release_gate.py --write` stamps every plugin
version in `.claude-plugin/marketplace.json` from `package.json` and reports release fitness
(every stale surface in one run). Commit the result and merge only when the gate is green.
