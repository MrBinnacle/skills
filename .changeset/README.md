# Changesets

This folder is used by [`@changesets/cli`](https://github.com/changesets/changesets) to
version the collection and generate the changelog.

**When you make a change worth recording**, add a changeset:

```bash
npx changeset
```

Pick the bump (patch / minor / major) and write a short, human-readable summary. The file it
creates in this folder is committed with your PR and merged to `main` alongside the change.

**A `major` changeset tells installed users what to do.** When the bump is `major` for any
package, the last line of the summary has this exact form:

```text
Action for installed users: <text>
```

Write `None.` as the text when an installed user has nothing to do. A release headed "Major
Changes" sends a user looking for a break, and this line answers whether there is one. The
line is optional for `minor` and `patch`. CI runs `python scripts/check_installed_user_action.py`,
which refuses a major changeset whose last non-blank line does not start with
`Action for installed users:` and carry text after the colon, and names the file.

**Cutting a release** is a deliberate step (there is no auto-release CI). The merge of the
version-bump pull request is the delivery event — changed cards reach installed users then,
not when a tag is pushed. See [AGENTS.md](../AGENTS.md) step 4 and
[ADR 0002](../docs/adr/0002-a-release-is-a-delivery-event.md).

When you want to roll the pending changesets into a version, run:

```bash
npm run version
python scripts/release_gate.py --write
```

`npm run version` consumes every pending changeset, bumps `package.json`, and writes the new
section of `CHANGELOG.md`. It then runs `scripts/finish_changelog.py`, which dates that
section's heading as `## v<version> - <date>` (today, in local time) and moves the changelog
preamble back above it, since `changeset version` inserts the section directly under the
title. Set `GITHUB_TOKEN` (a token with `public_repo` scope, such as `gh auth token`) before
running it, because the changelog generator looks up each changeset's pull request, and push
every commit you want credited first. `release_gate.py --write` stamps every plugin
version in `.claude-plugin/marketplace.json` from `package.json` and reports release fitness
(every stale surface in one run). Commit the result and merge only when the gate is green.

**After the bump merges**, the README install receipt still names the previous version: the
install it would cite has not run yet, and the `Install form` check warns rather than fails
while the receipt lags. Once the first push run of `tests.yml` on `main` passes at the new
version, run:

```bash
python scripts/refresh_install_receipt.py          # print the diff
python scripts/refresh_install_receipt.py --write  # apply it
```

It cites that run's id and date, and needs `gh` authenticated against the repository. Open the
result as its own pull request.
