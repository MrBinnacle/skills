---
"mrbinnacle-skills": patch
---

Two fixes from the 2026-10-31 audit. The `verify-gate` extension no longer treats a failed check command as a verification: a shell command that matches a check pattern clears the pending files only when the tool reports no error, which is the rule the fusion receipt route already applied. Receiver checks and trusted command probes now have a 600-second limit in `mechanisms/session-packet/repo.ts` and in both copies of `validate_packet.py` (`im-up`, `im-down`). Before this change a check that waited on a lock or a prompt froze `/packet-open` and `/packet-close` with no end. A check that outruns the limit fails with exit code 124 and a "timed out" message. `validate_packet.py` also ends the check's child processes. `repo.ts` runs through Pi's exec, which kills only the shell, so a child of that shell can outlive the timeout. Each language has a test for the timeout.
