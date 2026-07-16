# Changelog

All notable changes to the collection. The `npx skills add` installer tracks `main`, so
tags and this file are informational — a reading aid, not a pin.

## 2026-07-15

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
