---
"mrbinnacle-skills": patch
---

Every published card is named after the word a reader reaches for.

Eleven cards carried a name that stated the card's finding as a whole sentence:
`pretooluse-bash-guard-prose-false-positive`, `success-test-accepts-any-output`,
`click-clirunner-env-none-deletes`. The longest ran to forty-two characters. A proposition has to
be read to be understood, cannot be recalled unprompted, and cannot be said out loud. The name is
the string a person types to invoke a card, so a name nobody can recall is a card nobody reaches.

The rule these names were chosen under: name the card after the thing the reader is holding when
they reach for it. For a card someone sets out to run, that thing is the activity. For a card
nobody sets out to meet, it is the symptom. `writing-for-agents` states the mechanism, that the
name is a trigger word someone actually types, and the symptom is what they hold at that moment.
This is why `github-pages-deploy-verification` becomes `stale-deploy`, the deploy you cannot tell
is live, rather than a name for the fix, which helps only a reader who has already opened the card.

| Was | Is |
|---|---|
| `click-clirunner-env-none-deletes` | `clirunner-env` |
| `closure-mode-at-boundaries` | `closure-mode` |
| `git-pull-rebase-trap` | `pull-rebase` |
| `github-pages-deploy-verification` | `stale-deploy` |
| `mock-masked-stub-trap` | `mocked-stub` |
| `pretooluse-bash-guard-prose-false-positive` | `pretooluse-prose` |
| `success-test-accepts-any-output` | `vacuous-check` |
| `router-skill-predicate-gap` | `dead-predicate` |
| `downstream-instruction-framing` | `decision-rights` |
| `parallel-review-disposition-schema` | `disposition-schema` |
| `subagent-research-reliability` | `subagent-handback` |

`halt-as-deliverable`, `im-down` and `im-up` are unchanged, argued rather than inherited.
`halt-as-deliverable` carries its whole idea in its name, and renaming it would spend the idea to
save four characters. `im-down` and `im-up` are the owner's own spoken words for ending and
starting a session, and they hold forty-nine and fifty references each. Paying the highest
migration cost in the set for no gain in recall is the worst trade available.

The `-trap` suffix is retired. Most of these cards are traps, so the suffix distinguishes nothing.

This is the migration the quarantine rename declined to attempt. That changeset said a rename here
breaks installed junctions, `skills-lock.json` entries, inbound links and the paths cited in dated
records, and that it wanted its own review. This is that review, executed.

Each moved card's `name:` frontmatter matches its new directory. Only `skills-ref@0.1.5` checks
that equality, in CI, so a mismatch passes every local script. Every live reference is repointed:
`.claude-plugin/marketplace.json`, `.gitattributes`, `.github/workflows/tests.yml`, `README.md`,
`AGENTS.md`, `templates/BASE-OPERATING-RULES.md`, the three group READMEs, the allowlist and
docstrings in `scripts/validate_card_files.py`, the poison control in
`scripts/test_validate_scoreboard.py` that removes a card name from the README to prove the check
refuses a drop, and the cross-references nine quarantine candidates carry. 198 occurrences across
68 files.

Dated records keep the old names, because a record states what was true when it was written.
`CHANGELOG.md`, `dispositions/`, the already-written changesets and `docs/rule-screens.md` are the
set the collection already recognises. Three more are argued rather than assumed: `docs/adr/0001`,
which sits behind the canonical-document guard and cites a measurement taken on a date;
`docs/design/variants/`, whose own provenance block dates the drafts to 2026-08-30 and calls them
unselected raw material; and the worked example in `_quarantine/skill-family-curation`, which
quotes a 2026-06-09 adjudication and records its disposition under the names in force that day.

Two occurrences survive inside files that were otherwise repointed. The
`reclass-git-pull-rebase-trap.json` receipts cited in that card's `EVIDENCE.md` are real files at
pinned commits in `skill-harness`, and a rename here does not rename them there.
`_quarantine/subagent-research-reliability/` keeps its own name inside its `PROVENANCE.md`, because
only the published card moved.

The rename script did not repeat the failure the last one produced. Every edit is a byte-level
replacement, so no line ending is rewritten anywhere in the path. The quarantine pass normalised
four uniformly-CRLF files to LF before encoding and produced 1,520 insertions against a 53-line
change. This diff is 162 insertions against 162 deletions across 76 entries, and
`.claude-plugin/marketplace.json`, which is CRLF, reads 11 and 11 rather than 53 and 53.

After the change, each exiting zero: `validate_card_files.py`, `validate_scoreboard.py`,
`validate_brand_kit.py`, `check_prose_claims.py`, `validate_eval_corpora.py`,
`validate_spec_conformance.py` at 0 breaches across 39 cards, `validate_path_residue.py`,
`validate_voice_provenance.py`, `validate_disposition_counts.py`, `validate_conformance.py`,
`validate_skill_formats.py`, `validate_vale_style.py`, `release_gate.py`, and every matching test
suite including the poison controls. Vale reports zero errors. 171 relative links resolve.

Two things this does not settle. `#284` changes shape without resolving: the published card has
moved out from under the name, and the orphan quarantine directory now holds it alone. And the
junctions in a local `~/.claude/skills/` point at directories that no longer exist, which no
repository file can repair.
