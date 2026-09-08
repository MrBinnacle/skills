---
"mrbinnacle-skills": patch
---

Every quarantine candidate is renamed to a leading word instead of a sentence.

23 of the 25 candidates carried a name that stated the card's finding:
`uniform-eol-rewrite-evades-the-mixed-eol-guard`,
`concurrent-subagents-share-one-checkout-and-contend-on-head`,
`applied-layer-answer-hides-the-governing-result`. Each is a complete proposition. A proposition
must be read to be understood, cannot be recalled unprompted, and cannot be said aloud.

A card's name sits in the pointer position — the directory, the install listing, the first word of
the description, the string someone types to invoke it. `writing-for-agents` names the mechanism: a
leading word is a compact concept the model already holds, and in a pointer it steers invocation.
`wayfinder` and `triage` recruit priors. `applied-layer-answer-hides-the-governing-result` recruits
nothing.

The convention applied, in full: the name is a leading word of one to three tokens, preferring a
word the model already holds; it names the trap rather than the sentence about the trap; it can be
said out loud; and the proposition still gets written, in the description, where it does the
disambiguating work. The card's H1 heading is unchanged and still states the finding, which is
where a reader who has already been routed there needs it.

The renames, by `git mv`:

| Was | Is |
|---|---|
| `uniform-eol-rewrite-evades-the-mixed-eol-guard` | `uniform-eol` |
| `a-blocked-command-form-is-not-a-blocked-action` | `blocked-form` |
| `applied-layer-answer-hides-the-governing-result` | `wrong-altitude` |
| `concurrent-subagents-share-one-checkout-and-contend-on-head` | `shared-checkout` |
| `container-green-host-red-detached-child-holds-tempdir` | `detached-child` |
| `curated-context-becomes-the-reviewers-boundary` | `reviewer-horizon` |
| `summary-narrows-a-disjunction-to-its-nameable-half` | `nameable-half` |
| `bash-cwd-drift-false-clean-grep` | `cwd-drift` |
| `agent-definition-snapshot-at-session-start` | `agent-snapshot` |
| `squash-merge-absorbs-unpushed-base-commits` | `squash-absorbs` |
| `mutation-equivalent-in-architecture` | `equivalent-mutant` |
| `interactive-script-phantom-answers` | `phantom-answers` |
| `github-linkcheck-404-throttle-false-negative` | `linkcheck-throttle` |
| `openrouter-assistant-prefill-host-rejection` | `prefill-rejection` |
| `hidden-and-plugin-skill-reachability` | `skill-reachability` |
| `exit-worktree-cwd-override-merge-from-worktree` | `worktree-cwd` |
| `two-phase-doc-honesty-then-engineering` | `honesty-first` |
| `fix-brief-consolidation-id-hygiene` | `brief-ids` |
| `private-steering-head-over-public-repos` | `steering-head` |
| `anthropic-sdk-via-openrouter` | `sdk-via-openrouter` |
| `anti-slop-frontend-secure` | `frontend-slop` |
| `structure-at-the-write-site` | `write-site` |
| `walk-the-recipe-as-target-user` | `walk-the-recipe` |

`self-documenting-code` and `skill-family-curation` already satisfied the convention and are
unchanged.

Each moved card's `name:` frontmatter key now matches its directory. Every live reference is
repointed: `AGENTS.md`, `.github/workflows/links.yml`, `scripts/test_validate_quarantine_landing.py`,
two published cards' `gotchas.md`, and the cross-references between candidates. `CHANGELOG.md`,
`dispositions/` and the already-written changesets keep the old names, because those record what was
true when they were written and rewriting them would falsify the record rather than update it.

**No published card is renamed.** A rename there breaks installed junctions, `skills-lock.json`
entries in every install target, inbound links, and the `Occasions counted` dates that cite paths.
That is a migration with its own review, and it is not proposed here.

After the change: `validate_card_files.py` PASS, `validate_scoreboard.py` PASS,
`test_validate_quarantine_landing.py` PASS, and the `frontend-slop` candidate's own 25-test oracle
suite PASS.

**The rename script reproduced the failure documented by the card it was renaming.** Its write step
called `.replace("\r\n", "\n")`, a guard written to avoid introducing CRLF on Windows. Four files
that were uniformly CRLF in the index were normalised to LF, and the staged diff read 1,520
insertions against 1,520 deletions for a 53-line change. Caught by reading the numstat, repaired by
restoring CRLF, and counted as occasion 4 on `_quarantine/uniform-eol/EVIDENCE.md`. The rule the
card already states, now with a fourth instance behind it: match the file's existing line endings.
Avoiding the wrong ending is not the same thing.
