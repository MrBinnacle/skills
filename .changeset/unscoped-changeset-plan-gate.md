---
"mrbinnacle-skills": patch
---

Repair the changeset header that blocked every release, and close the scoping hole that hid it.

`.changeset/quarantine-starts-shipping.md` declared the package `@mrbinnacle/skills`. The
workspace package is `mrbinnacle-skills`. The two names do not match, so `changeset version`
refused to assemble a release plan and exited with `Found changeset quarantine-starts-shipping
for package @mrbinnacle/skills which is not in the workspace`. No release could be cut from
`main` while that file was present. It arrived on `main` in `f539b47` on 2026-08-24 and was
still there when this change was written.

A check for exactly this defect already existed. The comment above it in `tests.yml` names the
incident that motivated it. That check runs `changeset status --since=origin/main`, and
`--since` compares the current ref against `origin/main` — so on `main` the compared set is
empty, the check exits 0, and it reports `NO packages to be bumped`. The gate written to catch
this class of defect could not see the instance of it sitting in the same directory. CI was
green on every run.

The fix is one additional line: an unscoped `changeset status`, which assembles the full
release plan over every pending changeset and therefore fails on a bad header regardless of
when it landed. The scoped call stays, because it is the one that catches a bad header on
arrival in a pull request. The two answer different questions and the repository needs both.

A poison control ships with it, and it asserts the two calls **disagree**. It commits a
changeset naming an out-of-workspace package, points a ref at that commit so the poison is
present in the tree both refs share, then requires the scoped call to exit 0 and the unscoped
call to exit non-zero with `which is not in the workspace`. If the scoped call ever starts
failing there, the control no longer reproduces the defect and fails loudly rather than passing
quietly. The sequence was executed before it shipped: scoped exit 0, unscoped exit 1, message
matched, working tree restored.

The control restores with `git reset --soft`, never `--hard`, so a fault in the control cannot
destroy a working tree.

Two findings are recorded rather than smoothed over. First, adding a gate after a defect does
not remove the defect: this check shipped on 2026-08-24 and the changeset it was written for
survived it by sitting outside the window the gate looks at. Second, a scoped check reports
success in the vocabulary of a passing run — `NO packages to be bumped` — which reads as
health rather than as silence about an unexamined set.
