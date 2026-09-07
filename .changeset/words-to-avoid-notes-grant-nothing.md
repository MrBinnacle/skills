---
"mrbinnacle-skills": patch
---

`assets/tokens.json > copy.words_to_avoid_notes` no longer grants permissions that no checker implements. Two entries said a listed word was "Permitted only when the failure it resists is named in the same sentence" and "Permitted only with proof attached"; neither `scripts/validate_brand_kit.py` nor `scripts/validate_vale_style.py` reads that object, so both words were refused flat like every other entry. A contributor who read a note and wrote the sentence it described was refused by a build the documentation said would accept it, and then had no way to tell which of the other documented rules were real.

Both conditional entries are removed and the historical note is kept. `scripts/test_validate_brand_kit.py` gains a case that binds the two together: a note whose text reads as a grant is allowed only once a checker reads `words_to_avoid_notes` and names that word, so the documentation and the check cannot drift apart again. The case asserts its own non-vacuity — the detector must fire on both removed sentences and must not fire on the historical note. `BRAND.md` said three words carried conditions; it now states the flat ban and points at the test that holds it.

The published word-list digest is unchanged. It is taken over `copy.words_to_avoid`, and this change touches only the notes beside it, so the sibling repository's vendored copy still agrees.
