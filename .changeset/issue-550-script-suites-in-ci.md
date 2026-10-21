---
"mrbinnacle-skills": patch
---

CI now runs `scripts/test_refresh_dispatch_counts.py` and the frontend-slop oracle suite, which no workflow invoked. The dispatch-count suite gains a standard-library runner and no longer needs pytest. Installed users need do nothing.
