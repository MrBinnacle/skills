---
"mrbinnacle-skills": minor
---

Pi now has the Binnacle HUD, as the extension `mechanisms/binnacle-hud/`. It loads with this package's other Pi extensions. `alt+h` opens the panel. `/log` keeps a thought that never reaches the model. `/hud add` and `/hud send` give the agent Memory lines once you confirm them, and those lines stay in its system prompt through `/compact`. An observer reads new turns at pauses, on the session's model, and raises at most one note. It drops any note whose quoted evidence is not in what it read. `/hud observer off|panel|forward` decides whether notes stay with you or also go to the agent; the default is forward.

A test runs Pi 1.6.1's real agent loop with scripted model replies and checks every request: the Log and an unsent Memory never leave, sent Memory reaches the agent and not the observer, and a note reaches the agent only in forward mode and only when the agent did not already know it. Whether the observer's notes are worth an interruption is unmeasured; `mechanisms/binnacle-hud/eval/` holds the replay used to measure it.
