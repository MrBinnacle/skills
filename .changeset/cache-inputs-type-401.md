---
"mrbinnacle-skills": patch
---

`im-up` and `im-down`: a receiver check whose `cache_inputs` is not a list of path strings is now refused with a named error. Before, a bare string was read one character per path and silently cached against the whole tree (#401).
