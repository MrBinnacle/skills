---
"mrbinnacle-skills": patch
---

The skill-invocation phrase in AGENTS.md widens past skill-to-skill. "Call the Skill tool with
`skill-name`." now covers every place an agent reads an instruction to reach for a skill —
inside a card, in a slash command, in an AGENTS.md line, in a subagent dispatch — because none
of the last three sit inside a card and all three had the same inference problem. The same line
records that composing skills this way is endorsed: a card needing a discipline another card
already carries delegates to it rather than restating it, which keeps one meaning in one place
and keeps both cards inside the size bounds stated two lines above.

`applied-layer-answer-hides-the-governing-result` enters `_quarantine`. It was written to disk
in a prior session and never committed, so it sat in the working tree while absent from the
repository — and because the spec gate reads tracked files, the gate had never checked it. The
gate now covers 32 cards where it covered 31. Admitting it required meeting the size bounds:
`SKILL.md` was 9,183 B against a ~7 KB ceiling, so the worked example moved to a sibling file
reached by a pointer, leaving 6,369 B. Reading the conventions at source turned up three further
fixes — the description was 802 characters against a stated bound of 200 that 14 of 15 published
cards already meet, a trailing "See also" section violated the inline-at-moment-of-need rule, and
a References section explained why there were no references, which changes no reader's behaviour.
