---
"mrbinnacle-skills": patch
---

The session-boundary producer now refuses a packet made before this session's close commit (#122).

`validate_close_commit` established that `HEAD` is *a* close commit, not *this* session's — a session that committed nothing still sat on the previous close and passed, which is exactly the shape that produces a packet the receiver rejects as stale at the next open. The docstring named its own revisit condition: consult the packet directory for an already-claimed `HEAD`. That condition is now satisfied. A new `validate_unclaimed_head` check walks the configured `packet_dir` newest-first to the first prior packet that parses and records a head, and refuses production when the current `HEAD` equals that recorded `repository.head`, naming both in the message. Walking past unreadable files matters: a stray `README.md` sorts after digit-led timestamp names, so taking the raw filename maximum would let one stray file disable the guard silently and permanently. The existing marker check stays; each refuses a case the other cannot see.

The check degrades to the previous behaviour when there is nothing to compare against — an empty packet directory, a malformed newest packet, or a manifest without a recorded head — so a fresh clone can still produce its first packet. This limit is real and smaller than the hole it closes, and is stated in the docstring. Both cards move together: `validate_packet.py` and `test_validate_packet.py` are byte-identical across `im-down/` and `im-up/`, enforced by the suites' parity assertion.
