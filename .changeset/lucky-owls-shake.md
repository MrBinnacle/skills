---
"mrbinnacle-skills": patch
---

Close four verification holes found while adopting the session-boundary pair in a real
repository. Each was reproduced against the shipped code before it was changed.

- A `command` probe was never executed, yet its claim kept `verified` and the packet was
  ACCEPTED on an advisory note. Refusing to run packet-supplied commands was the right call;
  leaving the status untouched let any unverifiable claim be laundered by choosing that probe
  kind. A command probe now runs only when the repository config authorises the exact command
  (`receiver_checks` or the new `trusted_probe_commands`), and an unlisted probe rejects the
  packet.
- Receive mode without `--config` skipped every configured check and still returned ACCEPTED.
  It now rejects: a verification an omitted argument switches off is not a verification.
- The example `receiver_checks` entry was `git status --porcelain`, which exits zero on a
  clean tree, a dirty tree, and a deleted tracked file alike, so the only shipped example
  could not fail. The example is now `git diff --quiet && git diff --cached --quiet`, and the
  validator reports a known always-zero check as a note.
- A narrative sentence quoting a ticket title containing the word TODO rejected an otherwise
  valid packet. `__REQUIRED__` remains a hard rejection; `TODO` and `TBD` now reject only as a
  whole-line placeholder or a manifest value that is nothing but the token.

Also documents the produce-after-final-commit ordering (committing the packet moves HEAD and
makes the packet reject itself) and adds a drift assertion so the validator copy shipped in
both skill directories cannot diverge silently. The fixture suite grows from four cases to
nine.
