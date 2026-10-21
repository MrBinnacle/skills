# gotchas — walk-the-recipe (append-only)

- [OBSERVED 2026-06-09] Origin incident, recorded in `SKILL.md` → Example. A planning doc listed
  six "first-touch hardening" items for a reproduction recipe, written from the author's view.
  Walking the recipe as a subscription-auth user with no `ANTHROPIC_API_KEY` surfaced four
  failures the list did not name, including that the case study's own author could not
  reproduce it with current code. The literal-spec response would have shipped a recipe that
  still failed for that author's profile.

- [OBSERVED 2026-09-30] A stranger cold install of this collection at v3.0.1 failed with
  `git@github.com: Permission denied (publickey)`. The README's marketplace shorthand resolved
  to SSH, and the author's machine had a GitHub SSH key, so the author never saw it. Issue #333
  recorded it; pull request #340 fixed the README. Independent of the origin: a different
  project, a different recipe, a different working session.

- [RECORDED 2026-10-20] Repair before screen. The card's Step 4 had no class for a limit the
  recipe itself declares. A walk that cannot say "declared out of scope" files every declared
  limit as friction, which is the noise the #215 negative case exists to catch. The class was
  added BEFORE either replay ran, and both receipts hash the repaired `SKILL.md`. The
  `metadata:` frontmatter block was stripped in the same change. A first pair of replays ran
  on a 10.7 KB card; `scripts/validate_card_files.py --root` on a staged copy then refused it
  as over the 7,168-byte maximum (a size check does exist, against what the 2026-09-04 issue
  body said). The card was compressed to 5.9 KB, Step 3 gained the untrusted-input and
  irreversible-step rules, and both replays were re-run on the compressed card.

- [OBSERVED 2026-10-20] A replay pair on the compressed card ran zero steps. The agent called
  `claude plugin ...` directly instead of through `run_step.py`, `dontAsk` denied it, and the
  agent gave up and wrote a desk-only catalog that still looked like a result. The driver now
  tells the agent to re-issue a denied step through the runner, records a stream-json trace,
  and marks any run with no `STEP:` line invalid. The committed receipts are the pair after
  that fix; each ran five steps.

- [OBSERVED 2026-10-20] The #333 assumption no longer reproduces on Claude Code 2.1.305. In a
  scrubbed environment the shorthand `MrBinnacle/skills` now tries HTTPS first and falls back to
  SSH only when HTTPS fails (`Fetching the marketplace from GitHub failed on both attempts`).
  #333's own Revisit-if ("the CLI changes its shorthand resolution to HTTPS by default") has
  fired. A replay that targets #333 must therefore name a CLI version, or it tests nothing.
  The positive replay targets the Windows path-length assumption instead, which the same v3.0.1
  recipe also did not state and which v3.1.0's README later declared (line 53).

- [OBSERVED 2026-10-20] The first replay attempt used a harness-scoped API key and returned
  `Credit balance is too low` before any step ran. An agent run that fails on its own auth
  produces a transcript that looks like a finding about the recipe. Check the agent's exit code
  and that at least one `STEP:` ran before reading a catalog.

- [OBSERVED 2026-10-20] The step runner's allowlist refused `git config --global core.longpaths
  true` in the negative case and `npx skills add` in the positive case, and the agent reported
  both as untested rather than as failures. That is the correct reading, and it is also a limit:
  the receipts do not test the 108-157 character band or the npx route. Widen the allowlist in
  `replay/run_step.py` only by a step that writes inside the scratch home.
