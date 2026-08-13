# Security policy

## What a skill from this repo can and cannot do

Skills are inspectable source packages. Most contain instructions only. Some include scripts for
deterministic checks. Installation does not execute those scripts. An agent may execute them
during use, subject to the host's permissions. Review all instructions and executable files
before installation.

Everything in a skill folder is source you can read — never a binary, never minified or
obfuscated. Installing one:

- runs **nothing at install time** — no install hooks, no build step, no code executed to put
  the files in place;
- copies the whole folder onto your machine, scripts included, so what you read in this
  repository is what you have locally;
- adds instructions your AI assistant will read and may act on. Your assistant can run
  commands, so a malicious skill *could* instruct it to do harmful things. That is the real
  threat model for every skill collection, including this one.

## Our commitments

1. **Human-readable by design.** Every skill here is short plain English. If you cannot read a
   skill end to end in a few minutes, we consider that a defect — report it.
2. **No fetch-and-execute.** No skill in this collection instructs the agent to download and
   run remote code, pipe URLs to a shell, or fetch instructions from an external source at
   run time.
3. **Any code a skill ships is readable source, and it runs only when the skill runs.** Some
   skills bundle a script. It is committed as source here; it is invoked only by that skill's
   own written instructions, which you can read before you run them; and CI detects any file
   inside a skill folder that is not one of: `.md`, `.txt`, `.py`, `.json`. Adding a format to
   that list is a reviewed change to this policy, not a silent commit.

   ⚠ That check **detects** violations; it does not prevent them. `main` has no required status
   checks, so a nonzero exit is a signal, not a gate. Which is the point of the next paragraph.

   Do not take our word for it — check the copy you actually have:

   ```bash
   # 1. Nothing but the declared formats. Compiled Python is step 2.
   find -L ~/.claude/skills/<name> -type f \
     ! -name '*.md' ! -name '*.txt' ! -name '*.py' ! -name '*.json' \
     ! -path '*/__pycache__/*.pyc'

   # 2. Every compiled file has its readable source beside it.
   find -L ~/.claude/skills/<name> -path '*/__pycache__/*.pyc' -exec sh -c \
     'for f; do d=${f%/__pycache__/*}; b=${f##*/}; [ -f "$d/${b%%.*}.py" ] || echo "$f"; done' _ {} +
   ```

   Both print nothing when this commitment holds on your machine. (`-L` matters: installs are
   symlinked, and `find` without it silently skips them. Step 2 exists because a skill that ships
   a script leaves `__pycache__` behind the first time it runs — your interpreter wrote those,
   nobody shipped them, and they are fine exactly when the source sits beside them.)
4. **No secrets handling.** No skill asks the agent to read, move, or transmit credentials,
   tokens, or keys.
5. **Explicit updates only.** Installation copies files locally. Nothing self-updates; you
   diff and adopt changes deliberately.
6. **Provenance.** Skills with a real-incident origin carry a dated `EVIDENCE.md`. History is
   append-only in git.

Review the diff of any update as you would a pull request — that is the intended trust
mechanism, not a substitute for it.

## Reporting a vulnerability or a violating skill

If any skill in this repo violates the commitments above, or you find a way a skill's
instructions could be abused (prompt-injection amplification, instruction smuggling,
destructive-command patterns), please open a GitHub issue — or, for anything sensitive, use
GitHub's private vulnerability reporting on this repository.

Reports are acknowledged as fast as a one-maintainer project honestly can — typically within a
few days. Confirmed violations get the skill pulled first and discussed second.
