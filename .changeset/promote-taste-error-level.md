---
"mrbinnacle-skills": patch
---

Five of the six vendored Taste rows (Brevity-and-order, Dressing, Evidence, Register, Voice) are
now ERROR level, enforced by a second, ungated Vale pass in CI. Generic-ness stays warning: one
hit remains in a canonical ADR this pass could not edit. Thirty-two pre-existing findings across
the collection were fixed as uncontroversial prose corrections; one README line kept its original
wording because it is a cited `VERBATIM.md` specimen, carved out with an inline Vale exception
instead.
