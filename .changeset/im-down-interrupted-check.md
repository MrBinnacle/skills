---
"mrbinnacle-skills": patch
---

`validate_packet.py` in `im-down` and `im-up`: a validator that is interrupted (SIGINT, or SIGTERM on POSIX) now ends the check it was running, session and all. Since the check moved into its own session the signal no longer reached it, so a hung check outlived the validator with no limit (#647, part 1). Measured on Linux: without the fix the check's child survives the interruption; with it, it does not. Part 2 of #647 is Pi's own time limit and stays open there.
