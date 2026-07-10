# Security policy

## What a skill from this repo can and cannot do

A skill is a plain-text markdown file. Installing one:

- executes **nothing** on your machine — no install scripts, no binaries, no network calls;
- adds instructions your AI assistant will read and may act on. Your assistant can run
  commands, so a malicious skill *could* instruct it to do harmful things. That is the real
  threat model for every skill collection, including this one.

## Our commitments

1. **Human-readable by design.** Every skill here is short plain English. If you cannot read a
   skill end to end in a few minutes, we consider that a defect — report it.
2. **No fetch-and-execute.** No skill in this collection instructs the agent to download and
   run remote code, pipe URLs to a shell, or fetch instructions from an external source at
   run time.
3. **No secrets handling.** No skill asks the agent to read, move, or transmit credentials,
   tokens, or keys.
4. **Explicit updates only.** Installation copies files locally. Nothing self-updates; you
   diff and adopt changes deliberately.
5. **Provenance.** Skills with a real-incident origin carry a dated `EVIDENCE.md`. History is
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
