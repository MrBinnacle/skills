---
"mrbinnacle-skills": patch
---

Make the brand token file enforceable, and close the two colour gaps it recorded against itself.

`assets/tokens.json` described the brand and nothing read it. It said so in its own `known_gaps` block, and that block stayed an accurate description of the repository for twelve days: the kit declared structural neutrals for dark surfaces only, both banners carried the sibling instrument's confirmed-success green, and no source file or workflow opened the token file at all.

**The colour gaps are closed first, because the token check could not land green while they were open.** `assets/banner-dark.svg` drew its receipt seal in `#3fb950` and `assets/banner-light.svg` in `#2da44e` — `harness.prompt`, the measurement instrument's colour, which dressed the inventory as a measurement. Both now draw it in a declared structural neutral. No accent was substituted: replacing a borrowed hex with a newly minted one would close the gap by inventing a token. `color.structural_light` declares the light counterpart of the dark primitive set, so the light banner's `#1f2328` and `#57606a` are declared rather than undeclared-but-shipping.

**`scripts/validate_brand_kit.py` then runs three checks over the token file**, wired into `tests.yml` on both operating-system cells with a poison control per assertion:

1. **Banned copy.** Any surface named in `copy.words_to_avoid_surfaces` containing a word from `copy.words_to_avoid` is refused, naming the word and the file. Both lists are data: adding a word is a one-line edit to the token file.
2. **Hash pairs.** Files that must change together record the sha256 of both halves; either drifting from its recorded hash is refused. No pair is recorded yet — the social preview has no checked-in SVG source, and `asset_pairs.pairs_pending` states why. The checker refuses a token file that records neither a pair nor a reason, so the emptiness cannot go quiet.
3. **Declared hexes.** Every colour in `assets/*.svg` must be declared as a token value under `color`.

**The scope boundary is narrower than a naive check would draw it, and it is pinned by its own fixture.** README **body** prose, code comments and working documentation are out of scope. Banned words appear in all three deliberately — `AGENTS.md`, `SECURITY.md` and several skill cards use `load-bearing` in exactly the sense the word is good for. A check that caught those would be wrong, and the fixture asserting they pass is the first case in the suite.

**Two defects the controls found, recorded because a control that finds nothing proves less than one that finds something:**

- The first hex scan read every string in the token file, so `color.usage_rules` — the sentence stating that `#3FB950` belongs to the sibling instrument and must not be used here — read as a *declaration* of that colour. Planting the instrument green back into a banner passed: the ban was its own permission. Only a `value` field on a token object declares a colour now.
- SVG copy is parsed with `ElementTree` rather than pattern-matched, ported from the sibling instrument's scanner. A regex over `<text>` alone is blind to `aria-label`, and both banners carry their entire public statement in one.

This DETECTS breaches. `main` has no branch protection and no required checks, so a nonzero exit is a signal, not a gate.
