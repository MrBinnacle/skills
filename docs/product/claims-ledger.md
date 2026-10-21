# Claims ledger and consistency sweep

Checked **2026-10-17** against `main` at `5da3536ced12c2cf6dce813c3c3450adcba4d258` for the
Build GO boxes "Claims ledger" and "Consistency sweep" in
[#443](https://github.com/MrBinnacle/skills/issues/443).

**Amended 2026-10-17** against `main` at `bc28253`. Three entries changed. C6 now cites the
#452 receipt for the Windows path limit. The S2 Pi candidate uses the C2 third-person wording.
S9 adds the two remaining `npx skills add` sentences. Every other citation keeps the revision
above.

**Amended again 2026-10-17** against `main` at `eecd5a5`. C6 now cites the controlled
`core.longpaths` install receipt in
[`receipts/2026-10-17-windows-long-config-root.md`](receipts/2026-10-17-windows-long-config-root.md).
C7 cites the later v2.0.0 run, and the S9 candidates name v2.0.0 as the last recorded run. The
S2 Windows candidate follows the receipt. A third amendment the same day ties the C6 figures
to the measured tree, records that Windows long-path support is opt-in, and forbids reading the
install receipt as evidence that the skills work.

**Amended 2026-10-20.** C12 now gives the `/context` figure that
[#532](https://github.com/MrBinnacle/skills/pull/532) put on the README, and cites the README as
rewritten for a first-time reader that day. The C6, C9, C10 and C11 `README.md:N` citations and
the S2 rows now point at the page as rewritten (#540), read whole on 2026-10-20 at `main` `3605a52`.
Every other `README.md:N` citation keeps the revision it names.

**Amended again 2026-10-20** for [ADR 0008](../adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md).
C12 carries the refreshed `skill-harness skill audit` date. C13 adds the load-mode price. C16 is
new: which cards load in every session.

This is an internal working record. It is not public copy, and it changes no public surface.
It has two parts:

1. **The ledger.** One table per claim the repository makes or may make. Each table gives the
   allowed wording, the forbidden wording, the evidence and a status.
2. **The sweep.** One table per public surface. Each row quotes the current text, names the
   ledger claim it conflicts with, and gives a replacement marked **CANDIDATE**.

**The owner writes the public lines** ([BRAND.md](../../BRAND.md), lines 21-23). Every
CANDIDATE below is a draft for the owner to pick, edit or reject. No CANDIDATE lands without
the owner's approval (gate `public-copy-approval`). A CANDIDATE quoted from
[VERBATIM.md](../../VERBATIM.md) says so. Every other CANDIDATE is marked *agent-drafted*.

## Sources and status terms

The ledger derives each claim from these sources, which outrank this file:

- [PRODUCT.md](../../PRODUCT.md), the owner's direction of 2026-10-17.
- [BRAND.md](../../BRAND.md): *What the repository claims*, *Register by surface*, *Evidence
  rules* and *Open decisions*.
- The [runtime delivery matrix](runtime-delivery-matrix.md), checked 2026-10-17.
- [ADR 0002](../adr/0002-a-release-is-a-delivery-event.md) and
  [ADR 0003](../adr/0003-a-cards-name-is-part-of-the-declared-surface.md).

Citations take the form `file:line` at the revision named above. A citation to a command names
the command and its output.

| Status | Meaning |
| --- | --- |
| **ALLOWED** | A cited file or receipt supports the allowed wording as written. |
| **SCOPED** | Allowed only with the stated limit beside it: a date, a version or a runtime. |
| **INTENT** | An owner decision recorded in `PRODUCT.md`. It may be stated as direction. It may not be stated as a delivered capability or an observed result. |
| **FORBIDDEN** | No receipt supports the claim, or a cited record contradicts it. |

The word list in `assets/tokens.json` at `copy.words_to_avoid` applies to every claim below. This
ledger cites that list by its path and does not repeat it.

## Ledger

### C1. What the product is

| Field | Value |
| --- | --- |
| Claim | Skills is one product: a knowledge base and practical support for engineering work with frontier AI models. |
| Allowed wording | Skills is a knowledge base and a set of skill cards for engineering work with frontier models. |
| Forbidden wording | A definition of the whole product as Claude Code skills, Claude Skills, or skill cards alone. |
| Evidence | `PRODUCT.md:16-19`, `PRODUCT.md:122-125`: older card-only or Claude-only descriptions need reconciliation. |
| Status | **INTENT** |

### C2. Runtime direction

| Field | Value |
| --- | --- |
| Claim | Pi is the primary runtime direction. Claude Code is a compatibility and distribution target. |
| Allowed wording | Pi is the runtime this work targets first. Claude Code is the install route that has a receipt today. |
| Forbidden wording | Any wording that makes the direction read as delivery: Pi support, works on Pi, runs on Pi, built for Pi and Claude Code alike. |
| Evidence | `PRODUCT.md:17-19`; `PRODUCT.md:123-124`: a public surface must not imply that every intended capability already exists. |
| Status | **INTENT** |

### C3. A Pi install route

| Field | Value |
| --- | --- |
| Claim | A user can install Skills on Pi. |
| Allowed wording | None until a clean-install receipt exists. The honest gap may be stated: there is no tested Pi install yet. |
| Forbidden wording | Any install command, setup step or instruction for Pi. Any wording that lists Pi as a supported install route. |
| Evidence | `docs/product/runtime-delivery-matrix.md:91`: **UNKNOWN**, no clean-install receipt for a distributable Pi package. `PRODUCT.md:141-142`: no clean Pi package install is established. #443 *Cold install on every claimed route*. |
| Status | **FORBIDDEN** |

### C4. Pi delivery that was observed

| Field | Value |
| --- | --- |
| Claim | A configured Pi setup loaded cards from this repository. |
| Allowed wording | On 2026-10-17, a configured Pi 1.3.0 setup on the owner's machine loaded cards from explicit paths. Provider delivery and body invocation were not measured. |
| Forbidden wording | Any wording that turns this loader observation into an install route, a package, or runtime parity. |
| Evidence | `docs/product/runtime-delivery-matrix.md:88-89`. |
| Status | **SCOPED** to that configuration and date. Internal records only; it is not install guidance. |

### C5. Runtime parity and shared content

| Field | Value |
| --- | --- |
| Claim | The Pi and Claude Code routes deliver the same cards. |
| Allowed wording | Shared canonical content is the direction. Current byte parity is not established. |
| Forbidden wording | Same cards on every runtime; one card set for Pi and Claude Code. |
| Evidence | `docs/product/runtime-delivery-matrix.md:78-80`: two of four shared paths differ. `PRODUCT.md:65-66`. |
| Status | **FORBIDDEN** as a parity claim. |

### C6. The Claude Code plugin install

| Field | Value |
| --- | --- |
| Claim | The Claude Code marketplace commands install the three plugins. |
| Allowed wording | The HTTPS marketplace commands installed all three plugins at 3.0.1 on Claude Code 2.1.287, 2026-10-02, from a clean `CLAUDE_CONFIG_DIR` with no SSH key. On Windows without `core.longpaths`, the HTTPS form installs with a `CLAUDE_CONFIG_DIR` of 108 characters or fewer, measured with Claude Code 2.1.302 on 2026-10-17. With `git config --global core.longpaths true`, the HTTPS form installs with a config root of up to 157 characters, and fails above 157 even with the setting. That was measured on the same versions on 2026-10-17, on a host with Windows long-path support (`LongPathsEnabled`) turned on. Windows long-path support is an opt-in setting (Microsoft names a registry value, Group Policy and Intune as ways to turn it on, and states no default), so the install text must say that the setting-off case was not tested. Both figures hold for the tree at `eecd5a5`, the 3.1.0 candidate. They depend on the longest tracked path (80 characters for a directory at that commit), so a longer tracked path lowers both. |
| Forbidden wording | An undated or unversioned install claim. A claim that an install supplies the current `main` bytes. A claim that the install works on Windows without the `core.longpaths` setting at a config root over 108 characters. A claim that `core.longpaths` lifts the limit without bound: a root of 158 characters or more fails with it set. A claim that the long-root install was tested with Windows long-path support turned off, or that a session loaded the skills at start: neither was tested. A claim that the skills work after a long-root install: the receipt shows that the plugins install, list and validate, not that a skill fires in a session. The 108 and 157 figures stated for a tree other than the one measured, without a new measurement. |
| Evidence | `README.md:56-66` (commands and reload), `README.md:84` (Windows limits), `README.md:88-94` (verified forms); `docs/product/runtime-delivery-matrix.md:92`: historical install success does not attest current bytes. `docs/product/runtime-delivery-matrix.md:111-116`: a 2.1.296 temporary install found cards in all three plugins, and the suite failed one version assertion. [#452](https://github.com/MrBinnacle/skills/pull/452) (`31fe859`), section *Reproduction, measured on 2026-10-17*: Windows 11, Claude Code 2.1.302, git 2.56.0.windows.1, `core.longpaths` unset at every scope. The HTTPS form, bisected on the config root, succeeds at 108 characters and fails at 109 (108 + 59 + 80 = 247, the directory limit). A cold install from a 37-character root succeeded. `scripts/validate_install_paths.py` fails CI on any tracked path over that budget. #452 closed #356. [`receipts/2026-10-17-windows-long-config-root.md`](receipts/2026-10-17-windows-long-config-root.md): a control run at a 109-character root with `core.longpaths` unset failed as #452 recorded. With the setting at global scope, `marketplace add` and all three installs succeeded at roots of 109, 140 and 157 characters, at commit `eecd5a5`. `claude plugin list`, `plugin details` and `plugin validate` then read all three plugins back without a model call. A bisection found that 157 passes and 158 fails with `fatal: '$GIT_DIR' too big`. The host had `LongPathsEnabled` = 1, and skill loading at session start was not tested. Microsoft Learn, *Maximum Path Length Limitation* (updated 2025-04-15): from Windows 10 version 1607, long paths need an opt-in, and the `LongPathsEnabled` registry value "must exist and be set to `1`". |
| Status | **SCOPED** to the versions, dates, host conditions and tree of each receipt. *Revisit if:* the longest tracked path grows past 80 characters for a directory or 92 for a file, or Claude Code changes its temporary clone directory. Either moves both figures. |

### C7. The `npx skills add` route

| Field | Value |
| --- | --- |
| Claim | `npx skills add MrBinnacle/skills` installs the collection. |
| Allowed wording | The command is published. What it installs from the current tree has no receipt. |
| Forbidden wording | An unqualified install instruction, including a one-line install on a rendered asset. |
| Evidence | `docs/product/runtime-delivery-matrix.md:93`: **UNKNOWN** installer version, destination, selected cards and delivered bytes. `CHANGELOG.md:509` records a clean-directory run under v1.6.0, and `CHANGELOG.md:416` a later clean-directory reproduction under v2.0.0 (2026-09-13). No run is recorded after v2.0.0. v3.0.0 (2026-09-21) changed the plugin install path (`CHANGELOG.md:34`). The changelog does not say whether that change altered what `npx skills add` writes. Both receipts are stale. |
| Status | **FORBIDDEN** as a current install claim until a new receipt exists. |

### C8. What every card carries

| Field | Value |
| --- | --- |
| Claim | Each published card carries an evidence record, a gotchas record, test cases and the condition that would prompt its re-screen or retirement. |
| Allowed wording | Each card carries an evidence record, test cases, and the condition that would retire it. |
| Forbidden wording | Wording that says the test cases pass or have run. Wording that counts the cards in prose. |
| Evidence | Command run 2026-10-17 on every `skills/*/*/` card directory: each has `EVIDENCE.md`, `gotchas.md` and `evals/evals.json`, and each `EVIDENCE.md` has one `Re-screen trigger` row. `CATALOG.md:15`, `CATALOG.md:23-24`. `CHANGELOG.md:11`: the orchestration eval cases have not been run. The Vale `Claims` style bans a card count in prose. |
| Status | **ALLOWED** |

### C9. Measured benefit

| Field | Value |
| --- | --- |
| Claim | A card improves agent behaviour or engineering outcomes. |
| Allowed wording | No skill claims a measured benefit yet. The one controlled result, on `pull-rebase`, is `CANT_TELL_YET`. Publication is not validation. |
| Forbidden wording | Any wording that a card is proven, validated, effective, or makes agents more reliable. Any adoption or user count. |
| Evidence | `README.md:16`, `README.md:106`; `CATALOG.md:19-20`; `skills/engineering/pull-rebase/EVIDENCE.md:12-13`; `PRODUCT.md:141`; `BRAND.md:50`. |
| Status | **FORBIDDEN** as a benefit claim. The absence statement is **ALLOWED**. |

### C10. Admission

| Field | Value |
| --- | --- |
| Claim | Published cards passed the admission policy. |
| Allowed wording | Most published cards do not yet meet all four admission questions on recorded evidence. |
| Forbidden wording | Every skill passed admission. |
| Evidence | `README.md:16`; `CATALOG.md:67-72`; `dispositions/2026-08-15-S295-admission-triage.md`. |
| Status | **ALLOWED** in the stated form. |

### C11. Where the cards came from

| Field | Value |
| --- | --- |
| Claim | The cards started with problems the owner met. |
| Allowed wording | Most come from a failure seen in real work. Two, `im-down` and `im-up`, were designed. The owner's line: *Skills that started with problems I encountered.* |
| Forbidden wording | Every skill came from an incident. |
| Evidence | `README.md:10`, `README.md:14-16`; `VERBATIM.md:72-76`; each card's `EVIDENCE.md` Origin row. |
| Status | **ALLOWED** |

### C12. Standing cost

| Field | Value |
| --- | --- |
| Claim | Each model-invocable card adds a cost to every session. |
| Allowed wording | Each card not marked "by hand" adds one line to every session: about 70 to 80 tokens, as `/context` counts it (Claude Code 2.1.305, measured 2026-10-20). That holds when the host lists the card with its description. A host that lists it by name only charges under 20. |
| Forbidden wording | A cost figure with no instrument or date. A claim that a model-invocable card costs nothing until it fires. The `skill-harness skill audit` figures stated as what a session pays: [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476) found none of them within 10% of `/context`. |
| Evidence | `README.md:68`, in `## Install`, at the front-page rewrite of 2026-10-20; [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476), the pre-registered `/context` measurement, and [#532](https://github.com/MrBinnacle/skills/pull/532), which put it on the README; `CATALOG.md:12-14`. Each card's `Standing cost` row keeps the harness figure, measured by `skill-harness skill audit` on 2026-10-20, and CI job `validate_standing_costs.py` checks those rows against `scripts/standing-costs.json`. |
| Status | **SCOPED** to the Claude Code version and date of the `/context` measurement. |

### C13. What a version promises

| Field | Value |
| --- | --- |
| Claim | The install path, the card format and a card's name are the declared surface. The card set is not. |
| Allowed wording | The site and `CATALOG.md` *What a version promises* wording. Moving a card from always-on to by hand is a major change; moving it back is minor. |
| Forbidden wording | Wording that implies the card set is stable across a minor release. Wording that implies a card's load mode can change under a minor release in the always-on to by-hand direction. |
| Evidence | ADR 0002, *What the version number promises*; ADR 0003, *Decision*; ADR 0008, *Decision*. |
| Status | **ALLOWED** |

### C14. The repository is a knowledge base

| Field | Value |
| --- | --- |
| Claim | The repository's explanations, evidence and gotchas are useful without becoming a card. |
| Allowed wording | The repository is also a knowledge base: evidence, explanations and failure records. |
| Forbidden wording | Wording that a reader's decision changed, or that the knowledge base is used, as an observed result. |
| Evidence | `PRODUCT.md:21-25`. |
| Status | **INTENT** |

### C15. Audience and adoption

| Field | Value |
| --- | --- |
| Claim | Who the product is for, and who uses it. |
| Allowed wording | Built for the owner's own work first, and for other developers. |
| Forbidden wording | Any user count, community, adoption or demand claim. A comparison that makes the collection sound larger. |
| Evidence | `PRODUCT.md:33-40`; `BRAND.md:53-55`. |
| Status | Audience is **INTENT**. Adoption is **FORBIDDEN**. |

### C16. Which cards load in every session

| Field | Value |
| --- | --- |
| Claim | Only cards that clear a minimum evidence bar load in every session. The rest run by hand. |
| Allowed wording | A card loads in every session only when its record counts two or more occasions, or it carries a controlled result. Every other card runs only when you invoke it by name. |
| Forbidden wording | Wording that the always-on cards are proven, validated or effective: the bar counts occasions and controlled runs, and the one controlled result is `CANT_TELL_YET`. A roster of always-on cards in prose that no check reads. |
| Evidence | [ADR 0008](../adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md), *Decision*; `scripts/validate_card_files.py`, rule `always_on_bar`, which refuses a model-invocable card below the bar; each card's `SKILL.md` frontmatter and `EVIDENCE.md` `Occasions counted`, `Screen result` and `Paired verdict` rows. |
| Status | **ALLOWED** |

## Consistency sweep

Each table quotes the current text. *Conflicts with* names the ledger claim. **None** means the
text agrees with the ledger.

### S1. Repository About description and topics

Read with `gh repo view MrBinnacle/skills --json description,homepageUrl,repositoryTopics` on
2026-10-17.

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| Description: *Claude Skills* | C1, C2: defines the product by one runtime. | CANDIDATE A, quoted from `VERBATIM.md:76`, the owner's typed About text recorded 2026-08-30: *Skills that started with problems I encountered.* The same line is `package.json:5` and the social card's body line. |
| | | CANDIDATE B, the owner's About text recorded on the Notion project page on 2026-08-11. It is not in `VERBATIM.md`. Recording it there is the owner's decision. |
| Topics: `agent-skills`, `ai-agents`, `claude`, `claude-code`, `developer-tools`, `claude-skills`, `evals`, `llm-evaluation` | C2: Claude only. | CANDIDATE, *agent-drafted*: no Pi topic until C3 has a receipt. A topic is read as a supported runtime. Leave the list unchanged. |
| Homepage: `https://mrbinnacle.github.io/skills/` | None. | No change. |

The About text changed at least twice. The Notion project page records one line on 2026-08-11.
`VERBATIM.md:72-76` records a different line, the owner's typed text, on 2026-08-30. The live
value on 2026-10-17 is *Claude Skills*. No record in this repository says when or why the last
change happened. Gate `repo-description` lists three options; CANDIDATE A is a fourth, and it
needs no new owner-authored copy.

### S2. Root README

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `README.md:10`: *Claude Code skills for mistakes that report success.* Replaced by the #540 rewrite. `README.md:12` now reads *Skills is a knowledge base and a set of skill cards for engineering work with frontier models.* | None now. It agrees with C1. | No change. |
| `README.md:10`: *Any Claude Code user can hit these failures.* Removed by the #540 rewrite. `README.md:12` names *other developers who work with a coding agent*. | None now. It agrees with C2 and C15. | No change. |
| No line about Pi. Zero occurrences of the word Pi on 2026-10-17. `README.md:52` now carries the line, before the install commands. | None now. It agrees with C2 and C3. | Landed. The candidate was, *agent-drafted*, placed before the install section: *Pi is the runtime this work targets first. There is no tested Pi install yet. The install below is for Claude Code, the install route that has a receipt today.* This is the C2 allowed wording with the C3 gap beside it. The first draft of this row was in the first person. `scripts/validate_voice_provenance.py` refuses a first-person public line that `VERBATIM.md` does not record, so the row was changed on 2026-10-17. |
| No line about the knowledge base. `README.md:12` and `README.md:118` now state it. | None now. It agrees with C14. | No change. |
| `README.md:24`: *Or install everything with `npx skills add MrBinnacle/skills`.* The README no longer mentions `npx skills add`. | None now. | No change. |
| `README.md:56-66` and `README.md:88-94`: the install commands and the 2.1.287 receipt. The Windows sentence is at `README.md:84`. | None. It agrees with C6. | No change to the receipt. CANDIDATE, *agent-drafted*, added to the install section for the #443 *Accurate install wording* box: *On Windows, keep the path of your Claude configuration directory (`CLAUDE_CONFIG_DIR`) at 108 characters or fewer. If it is longer, run `git config --global core.longpaths true` before you add the marketplace; that raises the limit to 157 characters. Above 157, the install fails even with that setting. Measured for this release with Claude Code 2.1.302 on 2026-10-17, with Windows long-path support turned on. Not tested with that support off. Windows long-path support is an opt-in setting.* C6 covers each number and each condition in it. The sentence says the install works, not that the skills work, and front-door copy must keep that scope. |
| `README.md:68`: the standing cost, now the `/context` figure. | None. It agrees with C12. | No change. |
| `README.md:98-106`: what comes with each card. | None. It agrees with C8. | No change. |
| `README.md:16` and `README.md:106`: *No skill claims a measured benefit yet.* | None. It agrees with C9. | No change. |
| `README.md:93`: *or when a model or Claude Code change makes it unnecessary.* Replaced by the #540 rewrite. `README.md:112` reads *the platform change its retirement condition names*. | None now. | No change. |
| `README.md:4`: banner alt text, *skills. Each card states the condition that would retire it.* | None. It agrees with C8. | No change. |

### S3. Site title, description and Open Graph tags

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `site/index.html:6`, `:10-11`: title and `og:title`, *MRBINNACLE / skills* | None. | No change. |
| `site/index.html:7-9`, `:135`: *Skill cards that each state the condition that would retire them.* | None on substance: C8 supports it. C1 on register only, because it describes the product as cards alone. | CANDIDATE, *agent-drafted*: keep the line. Whether the description should name the knowledge base is a register decision, and it is the owner's. |
| `site/index.html:19-20`: image alt *MRBINNACLE / skills* | None. | No change. |
| `site/index.html:137`: *Skills that started with problems I encountered.* | None. Quoted from `VERBATIM.md:76`. | No change. |
| `site/index.html:140`: *Install in Claude Code* | None. It is scoped to one runtime, which agrees with C2 and C6. | No change. |

The issue text of #443 lists the site description as drift. The evidence does not support that.
Every card has the re-screen trigger the line names (C8). The open question is register, not
truth.

### S4. Marketplace and plugin descriptions

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `.claude-plugin/marketplace.json:8`: *Agent skills that each carry an evidence record, test cases, and the condition that would retire it.* | None. C8 supports it. *Agent skills* names the shared `SKILL.md` format, not a runtime. | No change. |
| `.claude-plugin/marketplace.json:14` and `skills/engineering/.claude-plugin/plugin.json:4`: *Workflow disciplines for shipping software: mistakes that report success, guards and gates that stop your work, and the rituals at phase and session boundaries.* | None. | No change. |
| `.claude-plugin/marketplace.json:19` and `skills/orchestration/.claude-plugin/plugin.json:4`: *Disciplines for multi-agent work - dispatch, joinability, and synthesis across parallel agents.* | None. | No change. |
| `.claude-plugin/marketplace.json:24` and `skills/meta/.claude-plugin/plugin.json:4`: *Skills about the skill system itself: whether a skill can be reached.* | None. | No change. |

These files are Claude Code plugin manifests. A Claude Code scope is correct on them.

### S5. Bucket READMEs

[#390](https://github.com/MrBinnacle/skills/issues/390) owns these files. This sweep records the
conflicts and drafts no replacement.

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `skills/meta/README.md:3-4`: *Disciplines for deciding what belongs in an agent's skill library at all, and for keeping that library honest about its own cost.* | C8, card set. The bucket holds one card, `dead-predicate`, which is about reachability. The card about whether a skill should exist retired in August. `CHANGELOG.md:22` removed the same subject from the plugin description. | Owned by #390. |
| `skills/engineering/README.md:5` and `skills/orchestration/README.md:5`: *Ordered by how soon the failure is likely to bite you.* | C9: no measurement ranks the failures by likelihood. | Owned by #390. |
| `skills/engineering/README.md:10`: *Born from a real incident that rewrote 22 commits* | None. `skills/engineering/pull-rebase/EVIDENCE.md:8` records 22 local commits. | No change. |

### S6. CHANGELOG head and GitHub Release notes

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `CHANGELOG.md:7-28`, the v3.0.1 section. The v3.0.1 Release body is the same text. | None. A changelog entry records the wording in force when it shipped. `assets/tokens.json` excludes this file from the word list for that reason. | No change. The next release's notes belong to the #443 *Release page* box. Check them against this ledger before publication. |

### S7. Social card

Text read from `assets/social-preview.svg`. The PNG upload is gate `social-preview-upload`.

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| Line 22: *skills* | None. | No change. |
| Line 27: *Skills that started with problems I encountered.* | None. Quoted from `VERBATIM.md:76`. | The card's primary line is an open owner decision (`BRAND.md:200-202`). This ledger records no candidate for it. |
| Line 31: *npx skills add MrBinnacle/skills* | C7: no current receipt. | CANDIDATE, *agent-drafted*: replace with the repository address, *github.com/MrBinnacle/skills*. |

### S8. Notion project page

The Notion project page for this repository was read through Notion search on 2026-10-17. Its
last edit is 2026-10-14. Notion is read-only for this work, so this table lists corrections
for the owner and makes none.

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| Title: *MrBinnacle/skills — Claude agent skills library* | C1, C2. | Owner's edit. |
| Snapshot: the latest tag and Release are v1.1. | Stale. The latest Release is v3.0.1, published 2026-09-30 (`gh release list`). | Owner's edit. |
| *Live GitHub About copy*: the 2026-08-11 line, described as the current public description. | Stale. See S1. | Owner's edit. |
| *Owner-directed product scope — 2026-10-14 (PROPOSED)*: the redefinition in PR #419. | Superseded. `PRODUCT.md:114-118` keeps the #419 thesis and contract as historical proposals. | Owner's edit. |

### S9. A surface outside the listed set

`CATALOG.md` is the first page the README links for detail. It is not on the #443 list.

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `CATALOG.md:7`: *A skill card is a Markdown file that Claude Code loads as instructions.* | C1, C2. | CANDIDATE, *agent-drafted*: *A skill card is a Markdown file an agent loads as instructions.* |
| `CATALOG.md:197`: *Models improve, Claude Code changes, and a failure mode can stop occurring.* | C2, minor. | CANDIDATE, *agent-drafted*: *Models improve, runtimes change, and a failure mode can stop occurring.* |
| `CATALOG.md:235-243`: the *Installer* paragraph and the command `npx skills add MrBinnacle/skills`, with no qualifier. Added to this sweep 2026-10-17 at `bc28253`. | C7. | CANDIDATE, *agent-drafted*: keep the paragraph, and add after the command block: *This route has no install receipt since v2.0.0, so what it installs from the current tree is untested.* The first wording, *since v3.0.0 changed the install path*, was withdrawn on 2026-10-17: v3.0.0 changed the plugin install path, and no record says it changed what this route writes. |

`AGENTS.md:57` is not a public surface. It is the conventions file for agents working here. It
still says *`npx skills add MrBinnacle/skills` is the other supported route*, and C7 forbids
that as a current claim. CANDIDATE, *agent-drafted*: *`npx skills add MrBinnacle/skills` is
published as a second route, with no install receipt since v2.0.0; it writes a
`skills-lock.json` and tracks `main` rather than a tag.*

## What this record does not settle

- It approves no wording. Gate `public-copy-approval` holds every CANDIDATE.
- It does not choose the About description. Gate `repo-description` holds that choice.
- It does not run an install. C3, C6 and C7 change only when a new receipt exists. The receipts
  it cites live in `docs/product/receipts/` or in the pull request named beside them.
- A wording change that follows from this ledger needs its own pull request and the owner's
  approval before merge.
