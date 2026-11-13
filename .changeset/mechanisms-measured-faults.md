---
"mrbinnacle-skills": patch
---

Seven faults in the Pi mechanisms are fixed, and one false sentence in `mechanisms/DESIGN.md` is corrected. Each behaviour fix landed after a test that failed on the old code. The reviewer's description change has no test.

- The verification gate no longer counts a check whose exit status the command hides. `npm test | tail`, `npm test || true` and `npm test; echo done` exit 0 when the tests fail, because Pi runs `bash -c` without `pipefail`. The gate no longer counts a command that only names a test tool, such as `echo npm test` or `cat jest.config.js`. The gate now tests each pattern against each segment of the command. The default patterns must match at the start of a segment.
- DESIGN.md now says what a malformed `.pi/engineering-env.json` does. The gate stays off for the session, and the error goes to a notification, or to stderr when there is no UI.
- The verification gate and `session-packet` keep each other's messages when both answer one `agent_before_settle`. Before this fix, a REJECTED packet's correction was dropped.
- The eol guard no longer reports a line-ending change that git's own diff does not show. Under `core.autocrlf=true`, writing LF over a CRLF checkout does not change what git stores.
- When more than 200 tracked files differ from HEAD, the eol guard does not check shell commands. It now says so once per run.
- On Windows, `session-packet` runs receiver checks through Git Bash. A Pi started from PowerShell or cmd has no `sh` on PATH, so every check failed before this fix.
- The `review_diff` tool names its fixed reviewer model. It no longer claims that the reviewer is a different model.

Action for installed users: if your `.pi/engineering-env.json` lists `checkCommands`, start each pattern with `^` so that a command that only mentions the tool does not count as a check. A pattern without `^` still matches anywhere in a command segment.
