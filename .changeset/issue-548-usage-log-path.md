---
"mrbinnacle-skills": patch
---

`scripts/refresh_dispatch_counts.py` no longer carries a default log path. It reads `SKILL_USAGE_LOG`, then an untracked `.skill-usage-log.local`, and otherwise exits 2 with a message that names the variable. The de-personalization scan now covers the file. Installed users need do nothing.
