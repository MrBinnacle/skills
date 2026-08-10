# Gotchas

- [OBSERVED 2026-08-07] A skippable close step produced absent packets across several sessions.
- [ANTICIPATED] Human-only invocation preserves control but cannot cover interrupts or crashes.
- [ANTICIPATED] A Stop hook fires after ordinary responses, not only at a true session boundary.
- [ANTICIPATED] Model-reported skill telemetry can be incomplete. Label its source honestly.
- [ANTICIPATED] A validator can check represented claims. It cannot prove that the writer represented every claim.
