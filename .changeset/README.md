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

Before you commit, read the new `CHANGELOG.md` section as a reader outside the repository
would, because each entry is copied verbatim from its changeset. Check that each "Action for
installed users" line is true for this release, that no entry promises "the next release",
and that each entry describes its change rather than giving a command.

**After the bump merges**, finish the release in two steps.

1. Merge the pin pull request. `release-pin.yml` runs on the push that changes `package.json`
   and opens it with `GITHUB_TOKEN` (#517), which needs the repository setting "Allow GitHub
   Actions to create and approve pull requests". Select **Approve workflows to run** on it, then
   merge it. The release gate is red on `main` and on every PR until it merges. Tag the release
   squash commit `v<version>` as well, because no workflow pushes a tag. The pin check verifies
   the tag only once it resolves, so the tag and the pin merge can land in either order
   ([AGENTS.md](../AGENTS.md) step 4).
2. Refresh the install receipt in `docs/product/runtime-delivery-matrix.md`. The receipt cites
   the first passing push run of `tests.yml` on `main` at the new version. `tests.yml` and
   `release-receipt.yml` have been untracked since #630 (2026-10-24), so no such run exists, and
   the script below exits 1 with `no passing push run of tests.yml on main`. Record that line
   on the release pull request until #690 brings a hosted test run back. Then run:

```bash
python scripts/refresh_install_receipt.py          # print the diff
python scripts/refresh_install_receipt.py --write  # apply it
```

It needs `gh` authenticated against the repository. Open the result as its own pull request.

**Last, check what the public sees.** After the tag is pushed, publish the release on GitHub
from its `CHANGELOG.md` section, then run:

```bash
gh release create v<version> --title v<version> --notes-file <the section> --latest
python scripts/check_release_public.py
```

The check fails when the tag is missing or off `main`, when any `v*` tag has no published
GitHub Release, when another release is marked Latest, or when the newest Pages deploy is older
than the last change it deploys, or when the repository social preview GitHub serves is not
`assets/social-preview.png`. Each failure names its fix. It also prints the one check it cannot
make: the skills.sh listing. The release is done when it prints `PASS` and that listing is
checked.
