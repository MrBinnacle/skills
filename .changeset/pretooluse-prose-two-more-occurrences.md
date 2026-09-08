---
"mrbinnacle-skills": patch
---

`pretooluse-prose` records two more occurrences, and the second is a shape the card had not seen.

Both come from `guard-git-pull-rebase.py`, the hook the `pull-rebase` card prescribes. The first is the card's known shape at a larger scale: five blocks in one working day across two repositories, three of them first-hand to a session whose whole task was writing about the trap that guard polices. Among those three, the one worth the entry is a payload where the token was deliberately split as `'git ' + 'pull'` and blocked anyway, because the predicate's gap `[^|;&\n]*?` spans the concatenation. Splitting a token defeats a literal scan and not a gapped one, so the workaround an author reaches for first leaves them thinking the guard is unpredictable rather than over-broad.

The second occurrence is not prose at all. `git fetch origin pull/292/head:pr292` is blocked, because `pull` is a path segment in GitHub's pull-request ref namespace. The guard therefore refuses to fetch any pull request by ref, in any repository whose config arms it, whatever that pull request contains — and it refuses a form of the `git fetch` remedy the `pull-rebase` card itself prescribes. Verified by importing the guard's own `targets_bare_pull` over a case table: both the short and fully-qualified ref forms block, while ordinary fetches, pushes and both explicit-intent pulls pass and a genuine bare pull still blocks.

That widens what the card's remedy has to cover. Every prior occurrence says writing about a trap is how you trip its guard; this one costs a routine review workflow with no prose involved. It is counted under the card's general rule — a predicate that decides whether something will RUN must read command structure, not text — and flagged where it sits outside the card's narrower prose framing, because widening that framing is a card-text change this record does not make.

Neither occurrence is a falsifier under the card's re-screen trigger. That trigger falsifies on an instance where command-position anchoring and heredoc stripping fail to prevent the false positive; this guard never had either applied, so the remedy is absent rather than defeated.

`EVIDENCE.md` moves from 5 occasions to 7, the screen-result row from five incidents to seven, and the front-page card-evidence table from 5 to 7 to match. No verdict, date or claim changes: the card remains UNMEASURED on both screen result and paired verdict.
