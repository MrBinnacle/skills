# EVIDENCE — click-clirunner-env-none-deletes

Provenance record per the collection's evidence convention (see top-level README →
"The receipts, explained"). Fields are honest by construction: UNMEASURED means exactly that.

RECURRENCE-THIN: one counted occasion. ADMISSION.md criterion 2 asks for a failure that is
not a one-off, and this card has not yet shown one. The 2026-08-23 event recorded in
gotchas.md is link rot in the card's own citations, not another instance of the trap, so it
is deliberately not counted. The label comes off when a second independent instance of the
`env=` trap itself is recorded and counted.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-06-09, in the measurement harness that sits upstream of this collection. A CLI test built its `env=` argument as a filtered copy of `os.environ` with one key removed, on the assumption that omission deletes. It does not. A second API key stayed present during the invocation, a model-aware resolver in the system under test rewrote the model identifier, and the test made a live twelve-minute API call the test existed to prevent. The assertion still passed, because the expected string reached the output down a different code path. Details: SKILL.md → Example. |
| **Occasions counted** | 1 — 2026-06-09 origin, a filtered-dict `env=` leaving a key present and a test making the live call it was written to prevent (gotchas.md). |
| **Dispatches recorded** | No recorded dispatch, measured 2026-08-24. The figure is a tautology and is stated only so the row is not blank: this card sat in `_quarantine/` until 2026-08-24, so it was never installed and the platform counter had nothing it could have counted. It is not evidence about demand, recurrence or worth. Re-measure after one release cycle in the published tree. |
| **Validated against** | The library's own published signature, checked three times on three dates. Originally against `click/testing.py:534` on Click 8.1.x; re-checked 2026-08-23 after CI link rot exposed the dead `8.1.x` ref; re-checked 2026-08-24 against the current published source, which types the parameter `env: Mapping[str, str \| None] \| None` on `CliRunner`, `CliRunner.invoke` and `CliRunner.isolation`. The `str \| None` value type is the API stating that `None` is a meaningful value rather than an omission. The behaviour claim survived all three checks; only the citations rotted. |
| **Screen result** | UNMEASURED. The card is a library-behaviour trap, and the failure it names is deterministic rather than model-dependent: a model that knows the signature avoids it and one that does not falls in, with no judgement in between. The Full-vs-Null screen protocol measures lift on a task with an oracle, and the honest evidence class here is the dated signature check plus one incident record. |
| **Paired verdict** | UNMEASURED (see Screen result). Methodology reference: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md). |
| **Standing cost** | Description ≈ 40 tokens, paid on every turn while the card is model-invocable. The retrieval moment is model-side — an agent writing a CLI test that asserts on an absent environment variable — which is the argument for paying it. Body 5.8 KB, loaded only on retrieval. |
| **Re-screen trigger** | Click changing `env=` to a replacement environment rather than an override map, or typing the parameter `Mapping[str, str]` so `None` is no longer a value. Either change makes the trap impossible to write and the card retires against this criterion with no screen required. The pre-registered check is the signature, not a version number or a line offset, because both of those rot on the library's schedule rather than the card's. |
