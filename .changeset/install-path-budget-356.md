---
"mrbinnacle-skills": patch
---

A Windows install without `core.longpaths` now stays inside the path limit by a CI check, not by luck: every tracked path must fit what remains after a 37-character default config root and the 59-character temporary clone directory the HTTPS install form uses (#356).
