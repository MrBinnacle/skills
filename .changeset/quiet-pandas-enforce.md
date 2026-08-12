---
"mrbinnacle-skills": patch
---

`im-down`: enforce the close-before-packet order instead of documenting it.

A session close is two commands in a fixed order — the durable close commits, moving `HEAD`, and only then may the packet record `HEAD`. Reversed, the close moves `HEAD` out from under a packet that already recorded it, and the receiver rejects that packet as stale in the *next* session. The skill's `gotchas.md` carried this as `[ANTICIPATED]`; it has now been observed twice in a project that had already written the order into an always-loaded file.

Prose cannot hold the constraint, because whoever types the second command cannot see the effect of the first. So the requirement is now declarable: a config carrying `"close_commit": { "pattern": "RITUAL:" }` makes produce mode refuse a packet whose `HEAD` commit message lacks that pattern, and name the repair. Projects that declare no `close_commit` are unaffected.

The stale-HEAD check is untouched and still does its own job — `close_commit` checks that the close happened, not that nothing follows it.
