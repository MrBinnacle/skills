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

## Standing obligations — `conformance v1`

The commitments above are what this collection promises. This section is what a card owes for as
long as it stays published, stated as the list a checker is written against, so that the prose
and the check cannot drift apart quietly. Admission is a separate contract on a separate cadence:
`ADMISSION.md` governs getting in, this section governs staying.

**Version.** This edition is `conformance v1`, declared here and nowhere else. A material change
to the obligations, or to what counts as meeting one, bumps the version. Editorial changes —
wording, ordering, examples — do not.

**Machine-checked.** `scripts/validate_conformance.py` runs these six over the published tree and
reports `PASS`, `FAIL` or `CANNOT-CHECK` per card. `CANNOT-CHECK` is a separate count and is never
reported as a pass.

- **O1 — declared formats only.** Every file inside a skill folder is one of the declared readable
  formats, per commitment 3. Checked by `scripts/validate_skill_formats.py`, whose predicate the
  conformance run calls rather than restates.
- **O2 — no fetch-and-execute.** No card instructs the agent to download and run remote code, per
  commitment 2. Checkable in practice, not in principle: the check matches the known command
  shapes, so a green result means *no known shape is present*. An instruction phrased in English
  rather than in a command line ships no pattern to match.
- **O3 — shipped scripts named in `SKILL.md`.** A card's own `SKILL.md` names every script it asks
  the agent to run, per commitment 3, with commitment 3's own carve-out for the shipped test
  suites. This is the obligation with a demonstrated rejection: pointed at an earlier tree of this
  repository, where the naming sentence did not yet exist and the scripts already did, the checker
  reports the contradiction and exits nonzero.
- **O4 — `EVIDENCE.md` present with all controlled fields.** Every published card carries an
  `EVIDENCE.md` stating each controlled field. An empty field is the same refusal as an absent
  one: the card has not said.
- **O5 — controlled fields do not contradict a published receipt.** A card's controlled fields must
  not contradict a published measurement receipt for the same card. **This is checked on the
  maintainer's clock and is not, and will not be, promised as a CI check from this repository** —
  the measurement store is private, so there is nothing here to compare against. The conformance
  run reports it `CANNOT-CHECK` on every card, by construction rather than by neglect. The durable
  fix is citable, published receipts, and that work does not live in this repository.
- **O6 — scoreboard lockstep.** The front-page counts stay derivable from the cards. Checked by
  `scripts/validate_scoreboard.py`.

**Attested, not checked.** Two commitments are honest obligations that no repository check can
decide, and are listed here rather than left to look machine-checked:

- **Readability (commitment 1).** The few-minutes bar names no number, deliberately. A word count
  would pass a dense wall of jargon and fail a clear longer card. It stands as a reported-defect
  commitment: if a card fails it for you, that is a defect worth an issue.
- **No secrets handling (commitment 4).** The obligation is about what a card *instructs an agent
  to do*, which is a semantic property of English. Word-matching gets it backwards — a card
  telling the agent to *refuse* when a secret may be present scans identically to one that
  mishandles secrets.

**Commitment 5 is a channel claim, not a per-card obligation.** "Nothing self-updates" is a
property of the distribution channel and the installer. No file in this tree can witness it; the
tree is the thing that would be updated. It is stated among the commitments and is deliberately
absent from the list above.

**How the obligations are re-checked, and when that stops.** The cheap change-triggered checks
already run on every pull request. A scheduled workflow re-runs the whole conformance list weekly
over the published tree, because a breach introduced between merges is otherwise caught by nobody,
and a check that never fires is indistinguishable from one that cannot. That schedule ships as a
**pre-registered trial**: if by **2026-11-07** it has caught nothing the pull-request checks
missed, it is retired against that stated criterion rather than kept as ceremony. Per-card
`Conformed-under:` fields are deliberately not used at this edition; they arrive with the first
version bump, when a stale value would mean something.

## Reporting a vulnerability or a violating skill

If any skill in this repo violates the commitments above, or you find a way a skill's
instructions could be abused (prompt-injection amplification, instruction smuggling,
destructive-command patterns), please open a GitHub issue — or, for anything sensitive, use
GitHub's private vulnerability reporting on this repository.

Reports are acknowledged as fast as a one-maintainer project honestly can — typically within a
few days. Confirmed violations get the skill pulled first and discussed second.
