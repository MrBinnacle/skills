# DESIGN.md — the visual system for `MrBinnacle/skills`

**Values live in [`assets/tokens.json`](assets/tokens.json)** — colour, type, shape, wordmark
construction, card geometry, the rejection checklist. Read it; do not read a copy. This file
carries what the JSON cannot: the reasoning, the gotchas, and what is still open.

Live repository facts outrank both. If an asset in `assets/` disagrees with either file, the
asset is the fact — surface it and fix the file, rather than working around it once per reader.

**An asset ships when every line of `tokens.json > copy.rejection_checklist` reads *no*, and
every number on it resolves to an artifact you opened.** That is the bar for this whole document.

---

## Dressing

The one failure this system exists to prevent, and the word `tokens.json` already uses for it:
**dressing the inventory as a measurement.**

A skill being kept is an inventory fact. A skill having been measured is an evidence fact. Any
move that makes the first look like the second is dressing, and it breaks the only claim the
repository makes. Most rules below are one application of it:

- **Instrument green is dressing.** `harness.prompt` `#3FB950`, `harness.flagged` `#D29922`,
  `harness.cantTell` `#58A6FF` belong to `skill-harness`. Green reads as a confirmed-success
  state on the instrument. It is the sharpest available way to dress this repository's
  inventory, which is why it is the one colour rule stated as an absolute.
- **Monospace is dressing when it is decorative.** The mono/sans split is semantic: mono marks a
  value that came from somewhere checkable — a count, a verdict, a command, an identifier. Prose
  that merely describes those things stays in the sans face. Setting a claim in mono to make it
  look rigorous is dressing in type.
- **Polish is dressing.** The surfaces are plain on purpose. A polished surface over an honest
  limitation reads as a claim. This design succeeds when someone believes the numbers, not when
  they admire the card.

Hunt for dressing first when reviewing any asset. It is the failure that passes every other
check.

---

## Colour: two gaps closed, two remaining

`tokens.json > known_gaps` records what remains open, measured against the committed assets.
The two colour gaps — no light-mode neutrals, and instrument green on inventory assets —
closed on 2026-08-24.

**The token set is enforced.** `scripts/validate_brand_kit.py` performs three checks over
`assets/tokens.json`: banned copy on the surfaces named in `copy.words_to_avoid_surfaces`,
sha256 asset-pair hashes, and every hex in `assets/*.svg` declared as a token value. It runs
inside the `validator` job in `.github/workflows/tests.yml` on both operating-system cells,
with a poison control per assertion, and is a required status check on the protected branch.
**A green CI run is compliance, not silence.**

Two gaps remain open:
- **Social preview raster is unreadable.** `assets/social-preview.png` is a raster with no
  text layer; no check can read its copy or colours. Closing it is the social-preview rebuild
  (`MrBinnacle/skills#62`).
- **Compact mark still in the lockups.** `assets/lockup-horizontal.svg` and
  `assets/lockup-stacked.svg` still draw the retired MB compact mark. What replaces it is a
  design decision.

**Author new marks with `currentColor`**, not a literal hex. A file with no hex cannot violate a
token set, needs no light-mode neutral to exist, and inherits on either surface — which matters
because the kit declares dark-surface neutrals only. *Revisit if:* light-mode neutrals land, or
an asset needs more than one ink value.

⚠ `currentColor` does not survive `<img src="…">`; an asset embedded that way renders black. Use
`<picture>` with `prefers-color-scheme` as `README.md` already does, or inline the SVG.

---

## The mark

Construction is in `tokens.json > wordmark`. Three things it does not tell you:

**Why the nautical iconography is banned.** A binnacle is the housing that keeps a compass
readable and correct — it holds the instrument steady and corrects for the iron around it. A
compass rose or an anchor points at the sea; the name points at the *housing*. The rest of the
banned list — gear, robot, brain, circuit, sparkle — is the generic developer-tool iconography
the collection is trying not to resemble.

**Centre the letter band on the housing interior, not the raw grid.** With a 1.5px stroke the
housing's inner edges sit at 2.75 and 21.25 on a 24-unit grid.

**Check the `M`/`B` gap at 20px specifically**, which is the declared minimum. A nominal 2px gap
between stem centres leaves roughly a quarter-pixel of visible space at a 1.5px stroke, and the
pair reads as one glyph. *Revisit if:* the minimum size changes, or the mark is redrawn as
filled type rather than strokes.

---

## The social preview card

Geometry is in `tokens.json > social_preview`. Test at `640x320` and `320x160` before shipping —
the card is seen small far more often than large.

### Format and the render step — decided 2026-08-12

GitHub accepts **PNG, JPG or GIF under 1 MB**, and not SVG. Verified verbatim at GitHub's
documentation: the image must be *"at least 640 by 320 pixels (1280 by 640 pixels for best
display)."* The upload populates a repository **setting** through the web UI; it is not read
from a file in the tree. Two facts about the platform follow, and neither is negotiable:

1. A PNG must exist. An SVG alone cannot be the deliverable.
2. The final upload is a manual step by the owner. No CI job performs it or observes the result.

**Decision: the renderer stays out of CI.** The SVG is authored and checked in as the text source
of truth; the PNG is exported by hand at the moment of upload. CI gains no rendering dependency.

CI covers the text instead, reusing what already runs: `validate_scoreboard.py:121-126` extracts
`<text>` nodes from the two banners with a stdlib regex. Point the same extraction at
`social-preview.svg`, assert no `copy.words_to_avoid` entry appears, and pair it with a hash
record so an SVG edit that was never re-exported is visible. This is the check that would have
caught the retired tagline surviving on the card.

*Revisit if:* a rendered-output regression actually occurs — clipped text, wrong crop,
overlapping elements. That class is uncovered here by choice; catching it needs visual regression
tooling, which costs a second toolchain. Also revisit if GitHub changes the accepted formats.

⚠ Re-dereference those line numbers before citing them. They were exact when written; line
references rot.

---

## Accessibility

- **`aria-label` is a claim surface.** Every shipped SVG carries `role="img"` and a meaningful
  label, and `validate_scoreboard.py` checks the banners' labels against ground truth. Drift in a
  label is drift in a claim, not a cosmetic slip.
- **State reads without colour.** The crib palette encodes admitted / turned-away / retired; each
  must also be readable as text or shape.
- Both banners ship light and dark variants through `<picture>`. New surfaces follow that.

---

## Open decisions

The owner's, carried so they do not lapse.

- **The card's primary line.** Candidates exist and were independently reviewed. None is recorded
  here — writing one in would make it the default by inertia. *Revisit if:* the owner selects.
- **Card block count.** The live card carries five visual blocks against a stated structure of
  three. *Revisit if:* the owner rules, or the card is rebuilt from this spec.

---

*Voice and copy: [`BRAND.md`](BRAND.md). Values: [`assets/tokens.json`](assets/tokens.json), kit 0.1.*
