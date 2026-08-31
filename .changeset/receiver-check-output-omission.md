---
"mrbinnacle-skills": patch
---

`im-up` and `im-down`: a passing receiver check no longer buries the verdict under its own stdout.

`rerun_checks` captured 2000 characters of stdout and 2000 of stderr for every receiver check, whether it passed or failed. A caller running twenty checks received a receipt carrying up to eighty kilobytes of `ok ...` lines, and had to filter the receipt to find out whether the receipt was accepted. A receiver check signals through its exit code: on a pass its stdout is decoration, and on a fail it is the whole diagnostic.

A passing check now records `"output": "omitted: check passed, exit code is the verdict"`. A failing check keeps both streams, truncated as before.

The omission is recorded rather than silent. An absent `stdout` field would read as "this check printed nothing", which is a different claim from "this check passed and its output was dropped", and only the second is true.

Both published copies of `validate_packet.py` remain byte-identical to each other. The change was exercised end to end on 2026-08-31 across twenty configured checks, with the failing check's diagnostic preserved in full.
