---
"mrbinnacle-skills": patch
---

`O7` no longer crashes on a manifest of the wrong shape, and its absent-manifest case is no longer vacuous.

An independent cross-family review of the change that shipped `O7` found five defects. All five are fixed here, and the two that mattered were reproduced before being fixed rather than taken on the reviewer's word.

**A manifest that is valid JSON of the wrong shape aborted the whole report.** `data.get("plugins", [])` assumes the top level is an object. `[]`, `null`, `123` and `{"plugins": ["x"]}` all parse, so the JSON handler never saw them; each raised `AttributeError` out of the check, past both handlers, and took `O1` through `O6` down with it before a single obligation rendered — while the obligation's own text promised `FAIL`. Reproduced on all four shapes, then guarded: shape violations now raise a `ManifestShapeError` that subclasses `ValueError`, so they land in the existing unreadable-manifest handler and report `FAIL` like any other. Six shapes are now fixtures, and each asserts twice: that `O7` is `FAIL`, **and that the other obligations still rendered**.

**The absent-manifest case could not tell its own branch from a different one.** Deleting the `is not a file` branch entirely left a `FileNotFoundError` that the `OSError` handler converted into the same `FAIL` verdict — so the case passed with the branch it exists to pin removed. Reproduced by mutation: the full suite exited 0 with the branch gone. The case now asserts on the message, and the same mutation fails it by name. The reviewer mutation-tested the other four breach branches and all four were killed by name; only this one survived, which is why it is the one worth recording. **A verdict-only assertion cannot distinguish two code paths that return the same verdict** — that is this collection's own `success-test-accepts-any-output` card, one level up.

**Three smaller ones.** `CANNOT-CHECK` on an empty published tree contradicted the rule that `CANNOT-CHECK` is reserved for `O5` alone, and it discarded already-computed breaches; an empty tree is now `FAIL`, because a manifest compared against no cards has checked nothing. Path spelling — `././skills/x`, or a backslash separator — resolved on disk but failed a raw `startswith`, so a legitimately published card could be reported under the most alarming label this check emits, "named but not published"; separators and `.` segments are now folded before any prefix test, and `..` is refused. And a `SKILL.md` under `skills/` at any depth other than `skills/<bucket>/<card>` resolved, passed the leading-segment test, contributed a phantom name, and was validated by neither direction — the exact hole the two-direction design exists to refuse. The depth is now checked against the same depth `find_cards()` globs.

Every one of these is the same shape as the defect `O7` was written to catch: a check that looks complete because it names two directions, while a third state has no name at all.

*Revisit if:* the plugin manifest format gains a nested or non-list `skills` form, at which point the shape guard is stating a contract the loader no longer holds.
