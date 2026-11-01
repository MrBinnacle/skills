---
"mrbinnacle-skills": patch
---

`tips-anywhere` settles a heads-up once any prompt to Claude quotes its line. Before this, a note the built-in band had already handed to Claude stayed waiting in the mod, so its question, still open on another app, sent the same note a second time when tapped. Seen live on 2026-10-28, three times in one session. A `prompt.submit` hook now marks the waiting note handed when a prompt (not a slash command) contains its line, whitespace collapsed. A later tap, `/tips do` or a held question then sends nothing. Two tests cover it: the live sequence, and an unrelated prompt that leaves the note waiting.
