# Security policy

## What a skill from this repo can and cannot do

Skills are inspectable source packages. Most contain instructions only. Some include scripts for
deterministic checks. Installation does not execute those scripts. An agent may execute them
during use, subject to the host's permissions. Review all instructions and executable files
before installation.

Everything this repository ships inside a skill folder is source you can read — never a binary,
never minified or obfuscated. (Your own machine may add to that: running a skill that ships a
script leaves compiled `__pycache__/*.pyc` behind. Your interpreter wrote those, nobody shipped
them, and commitment 3 says exactly when they are fine.) Installing one:

- runs **nothing at install time** — no install hooks, no build step, no code executed to put
  the files in place;
- copies the whole folder onto your machine, scripts included, so what you read in this
  repository is what you have locally;
- adds instructions your AI assistant will read and may act on. Your assistant can run
  commands, so a malicious skill *could* instruct it to do harmful things. That is the real
  threat model for every skill collection, including this one.

## Our commitments

1. **Human-readable by design.** Every skill's *instructions* are short plain English — if you
   cannot read a skill's markdown end to end in a few minutes, we consider that a defect, so
   report it. Two skills also ship Python, and that is longer: `im-down` and `im-up` carry a
   validator and its test suite. They are held to being readable and commented rather than to
   the few-minutes bar, and commitment 3 covers them.
2. **No fetch-and-execute.** No skill in this collection instructs the agent to download and
   run remote code, pipe URLs to a shell, or fetch instructions from an external source at
   run time.
3. **Any code a skill ships is readable source, and nothing here fetches or generates it.** Some
   skills bundle a script, committed as source in this repository. A skill's own `SKILL.md` names
   the scripts it asks the agent to run, so you can read them before you run them. **Not every
   shipped `.py` is one of those** — `im-down` and `im-up` also ship their test suites, which our
   CI runs and no skill invokes. Read those too; they are part of what you installed.

   CI detects any file **in this repository** inside a skill folder that is not `.md`, `.txt`,
   `.py` or `.json` — plus compiled Python, which is allowed only as `__pycache__/<name>.pyc`
   sitting directly
   beside the `<name>.py` it came from. Adding a format is a reviewed change to this policy, not
   a silent commit.

   ⚠ That check **detects** violations; it does not prevent them. `main` has no required status
   checks, so a nonzero exit is a signal, not a gate. Which is the point of the next paragraph.

   Do not take our word for it — check the copy you actually have. Point this at the folder you
   installed into: `npx skills add` writes to `.claude/skills/<name>` under the directory you ran
   it in unless you pass `--global`, so confirm where yours landed rather than assuming.

   ```bash
   # 1. Nothing but the declared formats. Compiled Python is step 2.
   find -L <the folder you installed> -type f \
     ! -name '*.md' ! -name '*.txt' ! -name '*.py' ! -name '*.json' \
     ! \( -path '*/__pycache__/*.pyc' ! -path '*/__pycache__/*/*' \)

   # 2. Every compiled file sits directly in __pycache__ with its source beside it.
   find -L <the folder you installed> -path '*/__pycache__/*.pyc' ! -path '*/__pycache__/*/*' -exec sh -c \
     'for f; do d=${f%/__pycache__/*}; b=${f##*/}; [ -f "$d/${b%%.*}.py" ] || echo "$f"; done' _ {} +
   ```

   Both print nothing when this commitment holds on your machine. (`-L` matters: installs are
   symlinked, and `find` without it silently skips them. Step 2 exists because a skill that ships
   a script leaves `__pycache__` behind the first time it runs. The `! -path '*/__pycache__/*/*'`
   on both steps is load-bearing: `*` spans slashes, so without it a file buried a level deeper
   inside `__pycache__` is skipped by step 1 and waved through by step 2.)

   These two commands are generated from the same suffix list the CI walker enforces, and
   `scripts/check-installed-skills.sh` in this repository is the same pair in a runnable file.
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
