# Background watch, per harness

Pattern B in [SKILL.md](SKILL.md) runs `poll_deploy` in the background and waits for one notice. This file gives the call for each harness that was checked. A harness with no section here was not checked: use its own background command or watch tool, and give it a deadline longer than the poll.

## Claude Code

Checked 2026-11-12, Claude Code 2.1.323, against the [tools reference](https://code.claude.com/docs/en/tools-reference).

- **The block.** The Bash tool refuses a command that starts with `sleep 35 &&`. The refusal read on 2026-11-12: "To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block."
- **Monitor tool.** It runs the command in the background and feeds each output line back. `poll_deploy` prints one line, its outcome. Every watch has a deadline: 5 minutes by default, at most 30 minutes, and at most 10 minutes in a non-interactive `-p` run. Set the watch's `timeout_ms` above attempts times 5 seconds plus curl time. A 60-attempt poll needs about 5 minutes, so the default deadline can end it first.
- **`run_in_background: true`** on a Bash or PowerShell call. You get a notification when the command exits; do not poll it yourself. In an unattended session a background command gets 30 minutes, or the `timeout` passed with it, up to 2 hours. A local interactive session has no limit.
