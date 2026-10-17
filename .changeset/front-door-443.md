---
"mrbinnacle-skills": patch
---

The README, the landing page and the social preview now describe Skills as a knowledge base and a set of skill cards for engineering work with frontier models, and link the knowledge base from the front door. They say that Pi is the runtime this work targets first and that there is no tested Pi install yet. The `npx skills add MrBinnacle/skills` line is gone from the README and the social preview, because no receipt shows what it installs from the current tree. The README now tells Windows users with a `CLAUDE_CONFIG_DIR` longer than 108 characters to run `git config --global core.longpaths true` before they add the marketplace (#452). No card changes. Installed users need do nothing.
