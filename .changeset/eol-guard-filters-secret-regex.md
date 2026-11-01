---
"mrbinnacle-skills": patch
---

Two fixes from the 2026-10-31 audit. The `eol-guard` extension now reads a file at HEAD with `git cat-file --filters`, which applies the checkout conversion (`core.autocrlf`, `.gitattributes` `eol`), instead of `git show`, which returns the raw LF blob. Under `core.autocrlf=true` every edited file read as "LF at HEAD, now CRLF", so the guard appended a conversion note to every edit. A test runs real git under both settings. The secret scan in `mechanisms/session-packet/packet.ts` and in the two copies of `validate_packet.py` (`im-up`, `im-down`) no longer matches `sk-` inside an ordinary word such as `task-session-packet-chain`; the pattern now requires that no letter or digit precede `sk-`. A bare key such as `sk-abcdefghijklmnopqrstuv` is still refused, and each copy has a test for both cases.
