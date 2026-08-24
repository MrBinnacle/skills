---
"mrbinnacle-skills": patch
---

The session-boundary pair's parity contract now covers every shared file, and a missing sibling is reported as not verified instead of passing (#123).

The suites' `no-drift` assertion guarded three files while eight were byte-identical across `im-down/` and `im-up/` — the packet-format document and all four fixtures sat outside the tuple, so a change to any of them turned no assertion red. The contract now names all eight, the run prints which files it compared (so a future narrowing is visible in output, not only in source), and a contract file absent from either card counts as drift rather than being skipped. On a single-card install the suite reports `parity NOT VERIFIED` and omits `no-drift` from its pass roster, instead of printing a passed check it never ran. Verified by a mutation matrix: one byte appended to each of the eight files in one card only turns both suites red via the parity message naming that file.
