---
"mrbinnacle-skills": patch
---

The binnacle-hud README now says that v4.0.0 does not contain the mod, and gives a way to load it from a clone with `claude --plugin-dir` until the next release. It also bounds its privacy wording to what the mod's code does: kept thoughts stay in session state, the mod does not send the Log to Claude or make network calls, other plugins can read the Log and intercept writes to it, and a phone thought crosses Remote Control. Whether a thought stays out of a later model request is marked as not verified.
