---
"mrbinnacle-skills": patch
---

Binnacle HUD for Pi: the panel only displays now, and `alt+h` opens one menu. Before, the panel had its own text field and `alt+h` moved the keyboard between it and the prompt; a heads-up could not be sent to the agent in `panel` mode, and copying one with the mouse took whole terminal rows. Now each heads-up in the menu offers Send to the agent now (steers a running agent, or starts a turn on an idle one), Copy to the clipboard, and the four marks; Log and Memory are typed at the prompt or through the menu. Before a note is shown, the turns that arrived while the observer worked are read once more, and a note they already settled is recorded as stale and never shown: on 2026-11-27 a note arrived two seconds after the agent had fixed what it named. The prompt, now `observer-2026-11-28`, adds a `stakes` and a `decision` field to each note. The lifecycle is a TLA+ model checked with TLC in `mechanisms/binnacle-hud/model/`.
