---
---

CI now checks cross-product agreement against a real skill-harness checkout, not only the committed snapshot (#360). On ubuntu-latest, the `validator` job reuses the Evidence-scope drift step's checkout at `SKILL_HARNESS_REF`. It runs the standing-cost validator's live audit path and the conformance sweep with `--harness-root`, and a poison control shows that each of the two fails when the real harness disagrees. No card changes.
