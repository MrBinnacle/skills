---
"mrbinnacle-skills": patch
---

`node mechanisms/verify-gate/demo.mjs` runs Pi's real agent loop twice with scripted model replies: without the verify-gate extension the agent ships a broken discount, and with it the agent is sent back to run `npm test` and reports the failure. The demo exits non-zero when the gate does not fire. `mechanisms/README.md` describes it under "See it fire".
