# Porting brief: Claude Code skill cards to Pi

You are porting skill cards from Claude Code to Pi (a different coding-agent harness). The
copies are already in `C:/Users/mlpgr/2026_Projects/skills-pi/pi/skills/<name>/`. Edit them in
place. Edit **only** the skill directories assigned to you. Do not touch any other file, do not
run `git commit`, `git push`, or `git add`, and do not start long-running processes.

## The rule

Each ported skill must load and work **on its own** in Pi: no links to skills outside the
ported set, no harness config files, no setup step, and no Claude Code tool names, hook names,
or paths. The ported set is: vacuous-check, mocked-stub, pull-rebase, decision-rights,
walk-the-recipe, reviewer-horizon, nameable-half, wrong-altitude, write-site, phantom-answers,
uniform-eol, squash-absorbs. The only allowed link between two ported skills is
`vacuous-check` → `mocked-stub` (a relative link `../mocked-stub/SKILL.md`).

## How to port

- **Keep each skill's substance.** Same discipline, same steps, same evidence claims, same
  voice. This is a translation, not a rewrite. Change only what is Claude Code specific or
  what links outside the set. Keep the frontmatter `name` and keep the `description` trigger-
  precise and under about 200 characters; reword it only if it names Claude Code.
- **Translate harness terms into Pi terms:**
  - Claude Code tools → Pi tools: `Bash` → `bash`, `Read` → `read`, `Edit`/`MultiEdit` →
    `edit`, `Write` → `write`, `Grep`/`Glob` → `bash` with `rg`/`fd` (or Pi's `grep`/`find`
    tools), `Agent`/`Task` (subagents) → Pi's `agent` tool, `AskUserQuestion` → ask the user.
    `Skill` and `SendMessage`: remove or describe generically.
  - "Claude Code" as the harness → "the harness" or "Pi", whichever reads true. Where the text
    records a **historical incident** that happened in Claude Code, describe it neutrally
    ("an agent session", "a pre-tool-call guard") so the fact survives without the name.
  - `PreToolUse` hooks → a Pi extension `tool_call` handler, which can block a tool call by
    returning `{ block: true, reason }`; a handler that throws also blocks. `PostToolUse` →
    `tool_result` handler. `SessionStart` → Pi's `session_start` event. Pi extension docs:
    `C:/Users/mlpgr/AppData/Roaming/npm/node_modules/@earendil-works/pi-coding-agent/docs/extensions.md`
    (read the events section before writing any extension recipe).
  - `.claude/` paths, `CLAUDE.md`, `settings.local.json`, `hooks.json` → Pi equivalents
    (`~/.pi/agent/AGENTS.md`, project `AGENTS.md`, `.pi/settings.json`, `.pi/extensions/`)
    or remove.
  - `$ARGUMENTS` does not exist in Pi: text after `/skill:name` is appended to the skill.
  - Git hooks (`.git/hooks`, pre-commit) are not harness hooks. Keep them.
  - Model names in historical evidence (Sonnet, Opus) are facts; keep them.
- **Links outside the set:** remove the sentence, or inline the one idea the reader needs in a
  sentence or two. Never leave a dangling name. A link to a GitHub issue in the skills repo is
  also flagged; remove it or keep the fact without the link.
- **Auxiliary files** (`EVIDENCE.md`, `gotchas.md`, `case-study.md`, `worked-case.md`, etc.):
  keep one only if `SKILL.md` (or a file it links) **already** tells the reader to open it with
  a relative link. If nothing links to it, **delete the file**. Do not add new links just to
  keep a file. A plain-text mention without a link does not count: either make it a real
  relative link (if the body clearly tells the reader to open it at a step) or delete the file.
- Keep the flat layout. No new files except where the brief for your skill says so.

## Check your work

Run the lint and read every line for your skills:

    cd C:/Users/mlpgr/2026_Projects/skills-pi && python pi/scripts/lint_pi_skills.py | grep -E "^(skill-a|skill-b)/"

Iterate until your skills have zero findings. If you believe a finding is a false positive,
do not game the pattern with odd spelling. Reword naturally, or report it in your final
message with the line and your reasoning.

Then reread each `SKILL.md` top to bottom as a Pi user would and confirm it still makes sense
on its own.

## Final message

For each skill: files kept or deleted, each substantive change (one line each), anything
inlined from an outside skill, and any lint finding you could not resolve. Keep it short.
