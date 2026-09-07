---
"mrbinnacle-skills": patch
---

`scripts/validate_brand_kit.py` chose the files it scans by walking the filesystem. It asked the working tree what was there, never the index, so the scanned set was whatever a clone happened to hold.

Measured on a working clone the day this landed: exit 1, 54 breaches, and not one of them in a file this repository tracks. Forty-eight sat under a `.sandcastle/worktrees/` sandbox and six under `node_modules/`. The same command was green in CI, which clones only tracked content. So the local signal and the CI signal disagreed, and the local one is the one a contributor sees first — a red gate naming files nobody will ever ship, with nothing the reader can do about it except delete a file the checker had no business reading. This repository has already written down what that costs, in the design note beside the word-list digest: a contract that reddens for reasons its reader cannot act on gets muted.

Selection is now the tracked set. Each surface glob is resolved as before and then intersected with `git ls-files --cached`. The glob stays in `assets/tokens.json` because `scripts/validate_vale_style.py` refuses a Vale binding to any glob the token file does not declare, so moving selection out of the token file would redden that check; what changed is the denominator, not where the pattern lives. The declared-hex surfaces use the same denominator, because they had the same hole.

When git cannot name the tracked set — no index, or a tree that is not a repository — the checker refuses and says why. It does not fall back to a walk, which would run a different check under the same name, and it does not report an empty scan, which would print as a clean run.

The chosen reading is recorded in `copy.words_to_avoid_scope`, so the next reader learns the scope from the token file instead of from a probe.

Four controls, and they are one control in four directions:

- an untracked markdown file carrying a listed word leaves the run green, which is the ticket's probe as a fixture;
- a gitignored one does too, which is the larger of the two classes the live tree held;
- the same word in a **tracked** file is still reported, which is the direction the first two cannot prove — a fix that simply stopped scanning passes them both;
- a tree whose index cannot be read draws a refusal naming the reason.

Both mutations were run before this landed. Restoring the walk turns the first two red — each naming its own probe file — and turns the live-tree and surface-count cases red with them. Replacing the refusal with an empty set turns only the fourth red, and it does so only because that assertion matches a string unique to the refusal lane; the looser wording it started with passed on that mutant, which is the control being killed by the wrong mechanism rather than by the behaviour it was written to pin.

`scripts/test_validate_brand_kit.py` now builds each fixture as a real git repository with its surfaces staged. Before this, a fixture tree had no index, and a tree with no index is one the checker refuses to scan rather than one it finds clean.

Two refusal messages change wording, from `matched no file` to `matched no tracked file`, and their assertions change with them. The refusal order also changes: the tracked set is read after the token file is validated, so a tree with neither still refuses on the token file, which is the problem its reader can act on.

`MrBinnacle/skill-harness#473` made the same change to that repository's DC-16 contract two days earlier, after the same probe found the same defect. The two repositories share the word list by design and now share the denominator.
