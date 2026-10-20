---
"mrbinnacle-skills": patch
---

The `session-packet` adapter tests now give each test that spawns git a 30-second timeout instead of bun's 5-second default. A slow Windows CI runner had pushed four of them past the default on a Markdown-only change. No shipped behaviour changes.
