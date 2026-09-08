---
"mrbinnacle-skills": patch
---

A README claim about this tree is now checked against the tree, and a card-set number in prose is
now refused.

## The defect class

On 2026-09-08 three reader-facing surfaces were found asserting things that were false, with every
gate green: the front page stated the card count eleven times, `_quarantine/README.md` said in bold
that no candidate carried an `EVIDENCE.md` when three did, and a card README documented three
subdirectories and a command path that do not exist.

The repository already had three derive-and-compare checks — the origin-tier and controlled-results
checks in `validate_scoreboard.py`, and `validate_disposition_counts.py`. Every one is a regex
anchored to a known sentence in a known section; `validate_disposition_counts.py` guards four
phrases inside `## Admission method` alone. All three defects sat in sentences no anchor reaches.

A fourth anchored regex would have guarded the sentences that were deleted and missed the next one.
So this adds two mechanisms that are not anchored to sentences.

## 1. `scripts/check_prose_claims.py` — structural claims, checked against disk

**Enumeration.** A group README names the cards in its group. That set must equal the directories on
disk in **both directions**. A card the page omits is as much a defect as a card it invents; the
omission direction is the shape `_quarantine/README.md` had.

**Documented paths.** A README that draws its own layout in a fenced block is making a claim about
the filesystem. Every path in such a block must exist beside it. This is the third defect exactly.

Both checks discover their own inputs, so both run under the population-integrity contract vendored
byte-equal from `skill-harness` at `scripts/vendor/population.py`. That contract reports a third
verdict, `UNINTERPRETABLE`, when the analysed set cannot be established as the declared set — a
refusal is not a pass. `skill-harness` registers it as a general invariant and names its own
`tests/test_receipts_index.py` as the first consumer; this is the second. The copy is pinned by
digest in `scripts/vendor/POPULATION_SOURCE.json` and a local edit to it fails the check, the same
rule `validate_vale_style.py` applies to the vendored Vale style.

## 2. `styles/Claims/Stated-count.yml` — the number is banned, not verified

Verifying a stated number leaves the number on the page. That was tried: `validate_scoreboard.py`
derived the card count into the ruled banner line per run, and the repository still shipped a
rendered SVG and a social card telling a stranger a number no reader's browser regenerates. The
Vale rule refuses `N cards` and `N candidates` in prose instead, at error level, bound to `README.md`
and the group READMEs.

It is bound only where Vale is actually run. `_quarantine/` is deliberately outside both run sites,
so binding a rule there would declare an assurance that never executes — which is the shape of
defect this rule exists to catch. Quarantine prose is covered by the checker instead.

**Stated plainly: the rule cannot see `publishes 14 of them`,** where the number is adjacent to no
noun it can anchor on. Nothing lexical can. That form is covered by there being exactly one surface
where a number is derived on read, the card-evidence table CI rebuilds.

## Controls

`scripts/test_check_prose_claims.py` carries seven, each planting one defect into a copy of the live
tree and requiring the check to refuse it **by name** — not merely to exit non-zero. The origin-tier
fixture in this repository passed for the wrong reason earlier the same day, when a banner change
made it fail before it reached the thing it tests, so a bare exit-code assertion is not enough.

Three controls found real bugs while being written:

- The digest check read the script's own directory and ignored `--root`, so it always examined the
  live repository whatever tree it was pointed at. Its control ACCEPTED a deliberately edited
  contract. A check no fixture can exercise cannot be shown to work.
- The path parser read an indented tree as a flat list, so the repository's own README was reported
  as naming three directories that do not exist — they exist, one level under `skills/`.
- The README enumeration walked the filesystem and reached an untracked sandcastle worktree. It now
  enumerates with `git ls-files`, which is what a reader can actually fetch.

An eighth condition is covered by `case_no_group_readme_is_uninterpretable`: with no input the check
exits 2, not 0. A detector that receives nothing reports no defect, and that is the failure the
whole contract exists to prevent.

CI runs the suite and the check in `validator`, with two poison controls beside them, and the Vale
ban's poison control in the `vale` workflow where Vale is installed.

## Also corrected

`README.md` carried two more counts this work surfaced: `two cards ... ship the Python scripts`, and
`the two card directories` describing the installer's fixed structure. The first is a subset tally
that rots; the second is not a card count at all, and the phrase was rewritten rather than teaching
the regex an exception.

*Revisit if:* a false claim is found on a reader-facing surface that neither mechanism could have
caught, which is the evidence that the class needs a third.
