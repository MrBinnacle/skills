---
"mrbinnacle-skills": patch
---

The `session-packet` repository and parked-entry tests now give each test that spawns git a 30-second timeout instead of bun's 5-second default. A slow Windows CI runner had pushed three of them past the default on pull requests that did not touch `mechanisms/`. No shipped behaviour changes.
