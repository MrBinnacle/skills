# Changelog

All notable changes to the collection. A release is a delivery event: changed cards reach
installed users when a version is released, not on every merge to `main`. See
[ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) for what a version promises.

## v1.2.0 — 2026-08-10

The session-boundary pair, and the first CI job that runs this collection's own code.

`im-down` and `im-up` carry one session's state into the next as an audited packet rather
than as conversational memory. They arrived, were hardened against four verification holes
found while adopting them in a real repository, and were renamed. Nine skills now.

### Minor Changes

- [#9](https://github.com/MrBinnacle/skills/pull/9) [`20bae6c`](https://github.com/MrBinnacle/skills/commit/20bae6cff067d0a5af4ac4607d73175015f7bc1a) — Add the session-boundary pair under `skills/engineering/`: `im-down` (producer — one
  atomic packet with a hidden JSON manifest, deterministic snapshot script, and validator) and
  `im-up` (receiver — treats the packet as untrusted data, verifies branch
  and HEAD, probes typed claims, runs only repository-configured checks, and emits an explicit
  acceptance receipt). Both are human-invoked (`disable-model-invocation: true`), configured via
  `.claude/session-boundary.json`, and ship with four fixture classes (clean accepted; stale
  HEAD, missing required field, and failed probe all rejected). No Stop hook ships in this
  release.

- [#11](https://github.com/MrBinnacle/skills/pull/11) [`fc5009c`](https://github.com/MrBinnacle/skills/commit/fc5009c1b78ba3f19728448d3229b9f163dda956) — Rename the session-boundary pair to `im-down` (producer, session close) and `im-up` (receiver,
  session start). The old names described the machinery; these describe what the operator is
  actually doing — signing off, and coming back. They also resolve a real collision: the previous
  receiver name was identical to a widely-installed local skill of the same name, so the two
  could not coexist in one library.

  No behavior changes. Directory names, frontmatter `name:` fields, bucket README, top-level
  README, and the pair's own cross-references all move together, and the validator drift
  assertion tracks the new directory names.

### Patch Changes

- [#10](https://github.com/MrBinnacle/skills/pull/10) [`fa81634`](https://github.com/MrBinnacle/skills/commit/fa816344730cbc7ed4dadc0f101873839799bd55) — Close four verification holes found while adopting the session-boundary pair in a real
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

- [#12](https://github.com/MrBinnacle/skills/pull/12) [`9b5d3bb`](https://github.com/MrBinnacle/skills/commit/9b5d3bb4fb60d550fc2ab9a1c2802b9bf7a7b309) — Run the session-boundary validator suites in CI. Two skills in this collection ship
  executable code and the collection had no job that executed it — only the link check and
  the de-personalization gate.

  The job invokes each suite through its real entrypoint rather than through `pytest`, and
  that is the point of it. The cases run from `if __name__ == "__main__"` and the functions
  carry no `test_` prefix, so `pytest` collects nothing from either file and reports
  "no tests ran" — a green line that means the opposite of what it looks like. The job
  asserts each suite's `PASS:` line so a suite that does not execute cannot report success,
  and a poison control asserts the shipped validator still rejects a stale packet, because a
  gate that cannot fail guards nothing. Both skills record the `pytest` false-green in their
  gotchas. Runs on Linux and Windows, the platform the pair is actually used on.

## v1.1.0 — 2026-07-15

First retirement, and a round of repository hardening.

- **Retired `claude-code-stop-hook-envelope`** — the collection's first retirement of a
  *shipped* skill. Claude Code now delivers the assistant's final turn inline via
  `last_assistant_message` on `Stop`/`SubagentStop` and recommends it over reading the
  transcript — the exact platform change the skill's evidence record pre-registered as its
  retirement trigger. Removed from the collection (7 skills remain), recorded in
  [RETIRED.md](RETIRED.md) with the evidence intact at the `v1.0` tag.
- **Corrected `git-pull-rebase-trap`** — the `--ff-only` claim was wrong: under
  `pull.rebase=true`, `--ff-only` refuses a diverged pull outright (a loud abort) rather than
  silently rebasing. `--no-ff` and no-flag pulls still rebase silently. Verified empirically
  (git 2.55.0).
- Repository hygiene: added `.gitignore`, `.editorconfig`, `CODE_OF_CONDUCT.md`, a pull-request
  template, and a link-check CI workflow (lychee, on every PR + weekly). Removed the empty
  `in-progress/` placeholder.

## v1.0 — 2026-07-11

The collection reaches its first complete shape: **8 skills, every one carrying an
evidence record.**

- Evidence coverage completed: `closure-mode-at-boundaries` and `skill-necessity-gate`
  receive their EVIDENCE.md records, closing
  [#1](https://github.com/MrBinnacle/skills/issues/1).

- Added `claude-code-stop-hook-envelope` — eighth skill, with evidence record
  (`f9f7afe`). Its EVIDENCE.md includes an honesty correction to the original private
  write-up's duration claim.
- Promoted three skills with evidence records: `subagent-research-reliability`,
  `downstream-instruction-framing`, `github-pages-deploy-verification` (`73d3796`).
- README restructured around four failure modes, with epigraphs quoting the collection's
  own evidence records (`d8db976`); skill lists ordered by how soon the failure bites
  (`8e18aa9`); banner + social preview added.
- Retirement log now leads with what the screening cost: four of the author's own
  candidates tested at the gate, none admitted (`41386db`).

## 2026-07-10

- First two evidence-backed skills shipped and the `EVIDENCE.md` convention established:
  `git-pull-rebase-trap`, `parallel-review-disposition-schema` (`e71df51`).
- Plain-language rewrite of the README and skill pages; `SECURITY.md` added.
- Retirement log seeded with the first four gate screens — all ceilings, none admitted
  (`e39315e`).
- De-personalization gate: fail-closed pre-commit/pre-push hooks (`3370c58`) plus a CI
  belt (`6ff1bb1`). Published files must carry no private-project residue.

## 2026-07-08

- `skill-necessity-gate` shipped (`dd8b9e8`) — the six-question gate the collection
  itself uses to stay small.
- Shipped-skill rule enforced: unshipped work moved to `skills/in-progress/` (`10824f9`).

## 2026-05-24

- Initial commit: repo scaffolding + `closure-mode-at-boundaries`.
