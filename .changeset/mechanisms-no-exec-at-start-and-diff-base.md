---
"mrbinnacle-skills": patch
---

Two fixes in `mechanisms/`, from the 2026-10-31 audit. The session-packet extension no longer runs on `session_start`: that handler ran the project's `sessionPacket.receiverChecks` shell commands on every open of a repository that declared them, with no prompt, while `DESIGN.md` said those commands run only on an explicit command. `/packet-open` is unchanged. The reviewer's `review_diff` tool now passes the model-supplied `base` to `git diff` after `--end-of-options`, so a base of `--output=<path>` fails instead of writing that file. A test runs real git against that base and checks that the file does not appear.
