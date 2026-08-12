---
"mrbinnacle-skills": patch
---

`im-down`: enforce the close-before-packet order instead of documenting it.

A session close is two commands in a fixed order — the durable close commits, moving `HEAD`, and only then may the packet record `HEAD`. Reversed, the close moves `HEAD` out from under a packet that already recorded it, and the receiver rejects that packet as stale in the *next* session. The skill's `gotchas.md` carried this as `[ANTICIPATED]`; it has now been observed twice in a project that had already written the order into an always-loaded file.

Prose cannot hold the constraint, because whoever types the second command cannot see the effect of the first. So the requirement is now declarable: a config carrying `"close_commit": { "contains": "RITUAL:" }` makes produce mode refuse a packet whose `HEAD` commit message lacks that marker, and name the repair. Projects that declare no `close_commit` are unaffected.

The key is `contains`, not `pattern`, because it is a literal substring test — named `pattern`, a project would reasonably write `"^RITUAL:"` and get a check that matches nothing and refuses every packet.

The stale-HEAD check is untouched and still does its own job. `close_commit` establishes that the close happened, not that nothing follows it — and not that the close is *this* session's, which is recorded as a known limit in `gotchas.md`.

`duplication_case()` now guards all three files the pair ships in common, not just `validate_packet.py` — `test_validate_packet.py` and `CONFIG.example.json` were byte-identical across `im-down`/`im-up` too, with nothing catching a divergence.
