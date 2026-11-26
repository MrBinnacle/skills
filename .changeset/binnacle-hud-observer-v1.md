---
"mrbinnacle-skills": minor
---

The Binnacle HUD observer prompt is now `observer-2026-11-27`, and notes stay in the panel by default. On a replay of 199 checkpoints from 32 recorded sessions, judged in hindsight against the next 40 turns, the previous prompt raised 44 notes of which 13 were not true; this one raised 20 and none were not true, with 4 worth an interruption against 10. Because four in five notes are still not worth an interruption, `/hud observer` defaults to `panel`; `/hud observer forward` sets it back. The README states the numbers and the bar for returning to `forward`. `mechanisms/binnacle-hud/eval/hindsight.ts` builds and scores the hindsight judge. `bun test mechanisms` passed on Linux.
