---
"mrbinnacle-skills": patch
---

`_quarantine/self-documenting-code`: the thirteen files that never landed are here, and the copy this repository called the frozen 0.1.0 baseline turns out to be a different document.

`#216` landed this card from the public `theswerd/aicode` repository because the build ran in a container that could not reach the maintainer's machine. `PROVENANCE.md` said so and left the comparison open. `#233` ran the digest half of it and found the two `SKILL.md` files differ. This change runs the rest on the host.

**Thirteen files landed, not eleven.** `#233` says eleven and lists thirteen in the same body. Its arithmetic subtracted three repository files from fourteen local ones, which assumed the repository files also sat in the local install. Only `SKILL.md` did. The corrected count is posted as a comment on `#233` rather than edited into the body, so the record stays auditable.

**The two copies are not two versions of one document, and that is the finding.** The public file is an essay: 6,018 bytes, five headed sections, no version in its frontmatter, no links to anything. The local file is a procedure: 6,191 bytes, seven numbered steps, a disclosure map, `metadata.version: "0.1.0"` declared in its own frontmatter, and nine links that all resolve to files beside it. Every file in the local package carries one install timestamp, 2026-08-11 23:25; only the field report is later, because the maintainer wrote it. Nothing was edited after install. So the local install is the canonical 0.1.0 package and the public file is an earlier draft. The ticket's `Revisit if:` asked whether the local copy was modified. It is not. The repository held a fragment of something else.

This change does not repair that. `SKILL.md` here now holds the 0.2.0 candidate from `6e81b5d`, so the frozen baseline `#216` criterion 5 asked for is absent in both forms: the essay was replaced and the canonical file never arrived. Choosing among the three documents belongs to whoever owns the 0.2.0 candidate.

**`validate_package.py` exists.** `PROVENANCE.md` recorded that no such script existed in any tree. It sat on the maintainer's host at 3,464 bytes. `#216` task 4 is now done: `gotchas.md` is in its `ALLOWED_TOP_LEVEL` and nothing else in the script changed. It still exits non-zero here, because it validates the upstream nested layout and this repository's card layout is flat. Those errors describe the layout, not the card.

**The evals, read first-hand.** `evals.json` holds five cases and every one carries `"files": []`, so the registry's no-fixtures claim is correct about code. `trigger-evals.json` holds twenty labelled queries, ten positive and ten negative, naming near neighbours the card should decline. That is a contrasting fixture set that needs no code. `#216`'s evidence ceiling is right about efficacy and wrong about triggering; they are two claims.

**Nine files were flattened and one was renamed.** `AGENTS.md:44` sets a flat layout and house practice is unanimous: no `_quarantine/` card has a subdirectory, and `evals/` is the only one in use across published cards. The five reference documents, two templates and two scripts moved up a level keeping their names; `evals/` stayed. Twelve of the thirteen files are byte-identical to the source, verified with `cmp`. The field report is the exception: it named the maintainer's private repository on line 3, so that line got the same generic phrase `500ac26` used across five files, and the file was renamed from `FIELD-REPORT-2026-08-17-workspace-lint.md` because the old name carried the same repository in the path where a content-only residue grep cannot see it.

`EVIDENCE.md` is unchanged. All eight of its rows were checked against the field report now that the report is in the tree, and all eight hold, including its catch that the report's own finding totals disagree with each other.

**The card is not promoted and this change does not argue for it.** It stays in `_quarantine/`. Whether the field report satisfies `ADMISSION.md` criterion 1 belongs to the admission gate; criterion 1 asks for an observed unaided failure, and the report mainly records the card working.
