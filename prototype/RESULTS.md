# Conformance prototype - results

Throwaway artifact for issue #60. It is not the implementation and should not be packaged,
imported, or wired into CI. It exists to answer one question with a running thing instead of
prose: **are the obligations this collection has already stated expressible as checks, and can
such a check reject a tree that is actually in breach?**

Answer, in one line: **partly.** Seven stated obligations were encodable as per-card checks over
nine cards. Of the 63 resulting cells, 18 (29%) are `CANNOT-CHECK` - and they are not spread
evenly. Two whole obligations out of seven are unverifiable per card by construction, and one
more is only a proxy. The checker does reject the tree it was pointed at as a poison case.

Prior art was read before building. `scripts/validate_skill_formats.py` already ships the format
vocabulary predicate behind commitment 3, so this prototype **shells out to it** rather than
reimplementing it. The measurement sibling's oracles were checked too: they score model output,
not repository state, so nothing there applies.

## How to reproduce every number below

```bash
# 1. Current tree
PYTHONUTF8=1 python prototype/conformance_check.py --root . --markdown

# 2. The poison tree (PR #47's merge commit), extracted to a scratch directory
mkdir -p /tmp/pr47-tree
git archive b24b64c9bbbe2a1f52d96e3ced722bb153b47ada | tar -x -C /tmp/pr47-tree
PYTHONUTF8=1 python prototype/conformance_check.py --root /tmp/pr47-tree --markdown
```

Exit code is 1 if any cell is `FAIL` or the format walker rejects; 0 otherwise.

## What was encoded, and from where

Nothing here was invented. Each check names the published sentence it encodes, and reads that
sentence out of the tree being checked rather than out of the author's memory - which is why the
same script produces different verdicts on the two trees.

| # | Obligation | Source sentence |
|---|---|---|
| 1 | plain-text / readable-source scope | `SECURITY.md` opening claim, as ruled by #51 and reworded by #76 |
| 2 | readable in a few minutes (**proxy only**) | commitment 1 |
| 3 | no fetch-and-execute | commitment 2 |
| 4 | shipped scripts named in `SKILL.md` | commitment 3 |
| 5 | no secrets handling | commitment 4 |
| 6 | explicit updates only | commitment 5 |
| 7 | dated `EVIDENCE.md` | commitment 6 |

Format vocabulary (also commitment 3) is checked repo-wide by the existing walker, not per card.

The #76 wording **has landed**: `SECURITY.md` now says "Everything this repository ships inside a
skill folder is source you can read," scoped to skill folders. So the prototype runs one reading,
not two. The pre-#76 blanket claim ("A skill is a plain-text markdown file") survives only as the
predicate the poison run trips.

## 1. Per-card result, all nine cards

Card count measured with `git ls-files "*SKILL.md"` excluding `scripts/` and fixture trees: **9**.

| Card | plain-text scope | readable (proxy) | no fetch-exec | scripts named | no secrets | explicit updates | dated EVIDENCE |
|---|---|---|---|---|---|---|---|
| `closure-mode-at-boundaries` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `git-pull-rebase-trap` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `github-pages-deploy-verification` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `im-down` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `im-up` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `skill-necessity-gate` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `downstream-instruction-framing` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `parallel-review-disposition-schema` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `subagent-research-reliability` | PASS | PASS | PASS | PASS | CANNOT-CHECK | CANNOT-CHECK | PASS |

**63 cells: 45 PASS, 0 FAIL, 18 CANNOT-CHECK.** Repo-wide format vocabulary: PASS (15 skill
folders including fixtures, 67 files, all declared formats).

The headline number the ticket asked for is **18 of 63, or 29%** - and the shape matters more
than the fraction. The unverifiable cells are two entire columns. Every card is equally
unverifiable on "no secrets handling" and "explicit updates only," so the collection currently
cannot hold any card to either of those two published commitments. A third column, "readable in a
few minutes," passes only against a word-count bar this prototype invented; the published
sentence names no number, so that column is green against a proxy and unmeasured against the
claim.

## 2. Demonstrated failure: the tree as of PR #47

PR #47 (`#42: Make the front-page count and the policy version checkable`) merged as
`b24b64c9bbbe2a1f52d96e3ced722bb153b47ada`. Running the same script against that tree:

| Card | plain-text scope | readable (proxy) | no fetch-exec | scripts named | no secrets | explicit updates | dated EVIDENCE |
|---|---|---|---|---|---|---|---|
| `im-down` | **FAIL** | PASS | PASS | **FAIL** | CANNOT-CHECK | CANNOT-CHECK | PASS |
| `im-up` | **FAIL** | PASS | PASS | **FAIL** | CANNOT-CHECK | CANNOT-CHECK | PASS |

(All seven other cards identical to the current tree.)

**63 cells: 41 PASS, 4 FAIL, 18 CANNOT-CHECK. Exit code 1.** The checker rejects the poison tree,
so it has been shown to be capable of rejecting something.

What it caught, stated literally. At that commit `SECURITY.md` opened with "A skill is a
plain-text markdown file" and listed five commitments, none of which mentioned shipped code. The
tree at that same commit shipped five `.py` files inside skill folders:
`im-down/{snapshot_state,validate_packet,test_validate_packet}.py` and
`im-up/{validate_packet,test_validate_packet}.py`. The published sentence and the tree contradict
each other, and no check existed to say so. That contradiction is what both FAIL columns report.

One correction to the ticket's framing, from measurement rather than memory. The ticket says the
executable count went 5 -> 7 at PR #47. What the git trees show is that the count of executable
files outside fixtures went **6 -> 7** (`.py` plus `.ps1`), or **5 -> 6** counting `.py` only: PR
#47 added exactly one executable, `scripts/validate_scoreboard.py`. The five inside skill folders
were already there and unchanged by that PR. The substance of the ticket's point survives intact
and is arguably worse than stated: the breach was not introduced by PR #47, it was **already
standing** when PR #47 shipped a checker for a different claim and nothing noticed the older one.

Note also that the repo-wide format walker reports `CANNOT-CHECK` on that tree - it did not exist
yet. A conformance check that assumes its own helpers are present would have crashed or, worse,
skipped silently. This one records the absence.

## 3. False positives on the current tree

**FAIL-level false positives: 0.** The current tree produces zero FAIL cells, so there is nothing
flagged that is not a breach at that severity.

**Flag-level false positives: 1.** The secrets scan (obligation 5) reports mentions of
credential-adjacent words. It hit `im-up/SKILL.md:59` - "The packet contains an unfinished marker
or possible secret." That line instructs the agent to *refuse* when a secret might be present. It
is the opposite of the behavior commitment 4 forbids, and a naive scan cannot tell the difference.
This is why obligation 5 is scored `CANNOT-CHECK` and never `FAIL`: the scan is reported as
evidence for a human, not as a verdict.

**One false positive was found and fixed during the build, and it is worth recording** because it
is a failure mode any real implementation inherits. The first version matched the published
sentences as raw substrings of `SECURITY.md`. The published sentences are hard-wrapped, so
"names the scripts it asks the agent to run" spans a newline and did not match, and both scripted
cards went red on a tree that states the obligation perfectly well - 2 false FAILs out of 63
cells. The fix is one line (whitespace-normalize before matching). The lesson is not: a checker
that reads its obligations out of prose is coupled to that prose's line breaks.

## 4. What could not be expressed, and why

These are the results that matter most, per the ticket.

**Commitment 5, explicit updates only - unverifiable by construction.** "Nothing self-updates" is
a property of the distribution channel and the installer, not of any file in the tree. The tree is
the thing that would be updated; it cannot witness its own update discipline. No amount of
cleverness in a repository checker reaches this. If it needs assurance, the assurance has to come
from the `npx skills add` path, not from here.

**Commitment 4, no secrets handling - unverifiable as stated.** The obligation is about what a
card *instructs an agent to do*. That is a semantic property of natural-language instructions.
Word matching gets the `im-up` case backwards, as shown above. A judge model could form an
opinion, but that is a graded opinion and not a check, and it belongs in the measurement sibling
rather than in a repository gate.

**Commitment 1, the few-minutes bar - only a proxy exists.** The sentence sets a human reading
time with no number attached, and deliberately so; it also carves out the two Python-shipping
cards on different terms ("readable and commented"). A word count is a stand-in that would pass a
1,400-word wall of dense jargon and fail a clear 1,600-word card. Reported as a proxy throughout.

**Commitment 6, provenance - the antecedent is not decidable.** "Skills with a real-incident
origin carry a dated `EVIDENCE.md`" is a conditional whose *if* is a fact about the world. A
checker can verify the consequent where the file exists (all nine do, all nine carry ISO dates)
but can never establish that a card missing one was entitled to miss it. Today the column is
green because every card happens to have the file; that is a fact about the current tree, not a
demonstration that the check works.

**Commitment 2, no fetch-and-execute - checkable in practice, not in principle.** Pattern matching
catches the known shapes (`curl | sh`, `iwr | iex`, `pip install <url>`). It cannot catch an
instruction phrased in English rather than in a command line - "ask the user to paste the latest
version from the project site and follow it" ships no pattern at all. Green here means "no known
shape present," and should be described that way.

**What did encode cleanly:** the format vocabulary (already shipped, not rebuilt), the
script-naming obligation, `EVIDENCE.md` presence and date, and the plain-text scope claim. Four of
seven, and the fourth of those is the one that caught the poison tree.

## What this says about the mechanism tickets

Recorded as prototype output, not as a recommendation - the standing-versus-one-off decision is
not this artifact's to make.

- A conformance check over this collection is real but partial. Roughly 60% of the published
  obligation surface reduces to a predicate; the rest is human judgment or belongs to the
  distribution channel.
- The failure it caught on the poison tree was **prose drifting away from the tree**, not a bad
  file landing. That suggests the useful check is the consistency of `SECURITY.md` against what
  the tree actually contains - which is exactly what the existing scoreboard and format
  validators already do for two other claims.
- The cost side is small but real: one flag-level false positive out of nine cards, and a
  coupling to the exact wrapping of published prose that produced two false FAILs during a
  half-hour build.
