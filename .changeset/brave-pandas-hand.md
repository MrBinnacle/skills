---
"mrbinnacle-skills": minor
---

Add the session-boundary pair under `skills/engineering/`: `session-close` (producer — one
atomic packet with a hidden JSON manifest, deterministic snapshot script, and validator) and
`session-start-from-state` (receiver — treats the packet as untrusted data, verifies branch
and HEAD, probes typed claims, runs only repository-configured checks, and emits an explicit
acceptance receipt). Both are human-invoked (`disable-model-invocation: true`), configured via
`.claude/session-boundary.json`, and ship with four fixture classes (clean accepted; stale
HEAD, missing required field, and failed probe all rejected). No Stop hook ships in this
release.
