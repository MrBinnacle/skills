# How a subagent's report reaches its caller, per harness

Check 0 in [SKILL.md](SKILL.md) says the harness delivers a final report, and that the route
differs by harness and mode. This file records each route with the date it was checked. A harness
with no section here was not checked.

## Claude Code

Checked 2026-11-12 against Claude Code 2.1.323 and the docs pages `sub-agents.md`,
`agent-teams.md`, `tools-reference.md` and `hooks.md` at code.claude.com/docs/en.

**Outside auto mode, the final text is the return.** A foreground subagent's final text blocks
are the Agent result's `content`. A background subagent's results arrive as a completion
notification in a later turn. Intermediate output stays in the subagent's own context.

**A teammate reports through team messages.** With agent teams enabled, an Agent call that
carries a `name` can launch a teammate. When it stops, its idle notification "includes its final
answer". The `SendMessage` description says "plain text output is NOT visible to other agents".
No docs page says whether that line covers the final answer. Reading it as mid-turn text only is
an inference, not a checked fact.

**In auto mode, the report travels through a hand-back call (v2.1.271 and later).** Claude Code
gives the `SubagentHandback` tool to each subagent the Agent tool runs locally, except forks. It
adds the tool even when the agent definition leaves it out of `tools` or lists it in
`disallowedTools`. The report is that call's `message` input. The classifier reviews it before
delivery. The Agent result's `content` then carries a short note about the hand-back, not the
report. A stop-time hook's `last_assistant_message` is the closing text, not the report either. To
read the report in a hook, match `SubagentHandback` and read `tool_input.message`.

**A pre-tool-call hook can withhold the report.** A hook that returns `deny` on the
`SubagentHandback` call blocks it. Claude Code tells the subagent up to three times to call the
tool again. If the hook keeps denying, the subagent ends without delivering, and the waiting
conversation gets a note saying so. A hook that returns `ask` raises no prompt for this tool, and
the call runs even if the classifier objects.

**Two things are unverified.** First, whether the classifier alone, with no hook, can withhold a
report. Second, what reaches the caller when an auto-mode subagent ends in plain text without
calling the tool. Either would be a new dead-letter cause. Name a second return route until a
check settles them.

**The tool is not this card.** `SubagentHandback` is a platform tool that shares this card's name.
This card is a dispatch discipline. Loading one does not load the other.
