# Meta skills

Skills about the skill system itself: whether a skill can be reached. This bucket installs as the `mrbinnacle-meta` plugin, and its [`plugin.json`](.claude-plugin/plugin.json) is the authoritative list of what it installs. The card's `EVIDENCE.md` records where it came from and what has and has not been measured; an installed card is not thereby shown to work.

- [**dead-predicate**](dead-predicate/SKILL.md) — a live router rule can match nothing because the ordinary word is missing from its patterns, a JSON string escape left a pattern inert, an earlier rule shadows it, or the skill it names was renamed; use it when a hook did not fire or before claiming a rule is hook-enforced, and test the negative first against the live hook with a positive control in the same run ([the receipt](dead-predicate/EVIDENCE.md)).
