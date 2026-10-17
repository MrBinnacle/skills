# Claims ledger and consistency sweep

Checked **2026-10-17** against `main` at `5da3536ced12c2cf6dce813c3c3450adcba4d258` for the
Build GO boxes "Claims ledger" and "Consistency sweep" in
[#443](https://github.com/MrBinnacle/skills/issues/443).

**Amended 2026-10-17** against `main` at `bc28253`. Three entries changed. C6 now cites the
#452 receipt for the Windows path limit. The S2 Pi candidate uses the C2 third-person wording.
S9 adds the two remaining `npx skills add` sentences. Every other citation keeps the revision
above.

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
| Allowed wording | The HTTPS marketplace commands installed all three plugins at 3.0.1 on Claude Code 2.1.287, 2026-10-02, from a clean `CLAUDE_CONFIG_DIR` with no SSH key. On Windows without `core.longpaths`, the HTTPS form installs with a `CLAUDE_CONFIG_DIR` of 108 characters or fewer, measured with Claude Code 2.1.302 on 2026-10-17. For a longer config root, the install text may tell the reader to run `git config --global core.longpaths true` first. |
| Forbidden wording | An undated or unversioned install claim. A claim that an install supplies the current `main` bytes. A claim that the install works on Windows without the `core.longpaths` setting at a config root over 108 characters. A claim that `core.longpaths` was measured to make a longer root install: no install with that setting has been run. |
| Evidence | `README.md:39-45`; `docs/product/runtime-delivery-matrix.md:92`: historical install success does not attest current bytes. `docs/product/runtime-delivery-matrix.md:111-116`: a 2.1.296 temporary install found cards in all three plugins, and the suite failed one version assertion. [#452](https://github.com/MrBinnacle/skills/pull/452) (`31fe859`), section *Reproduction, measured on 2026-10-17*: Windows 11, Claude Code 2.1.302, git 2.56.0.windows.1, `core.longpaths` unset at every scope. The HTTPS form, bisected on the config root, succeeds at 108 characters and fails at 109 (108 + 59 + 80 = 247, the directory limit). A cold install from a 37-character root succeeded. `scripts/validate_install_paths.py` fails CI on any tracked path over that budget. #452 closed #356. `core.longpaths` is git for Windows' own setting for paths over `MAX_PATH`. The remedy rests on that setting, not on a receipt from this repository. |
| Status | **SCOPED** to the version and date of each receipt. |

### C7. The `npx skills add` route

| Field | Value |
| --- | --- |
| Claim | `npx skills add MrBinnacle/skills` installs the collection. |
| Allowed wording | The command is published. What it installs from the current tree has no receipt. |
| Forbidden wording | An unqualified install instruction, including a one-line install on a rendered asset. |
| Evidence | `docs/product/runtime-delivery-matrix.md:93`: **UNKNOWN** installer version, destination, selected cards and delivered bytes. `CHANGELOG.md:509` records a clean-directory run under v1.6.0, before the v3.0.0 change of install path (`CHANGELOG.md:34`). That receipt is stale. |
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
| Evidence | `README.md:89`; `CATALOG.md:19-20`; `skills/engineering/pull-rebase/EVIDENCE.md:12-13`; `PRODUCT.md:141`; `BRAND.md:50`. |
| Status | **FORBIDDEN** as a benefit claim. The absence statement is **ALLOWED**. |

### C10. Admission

| Field | Value |
| --- | --- |
| Claim | Published cards passed the admission policy. |
| Allowed wording | Most published cards do not yet meet all four admission questions on recorded evidence. |
| Forbidden wording | Every skill passed admission. |
| Evidence | `README.md:10`; `CATALOG.md:67-72`; `dispositions/2026-08-15-S295-admission-triage.md`. |
| Status | **ALLOWED** in the stated form. |

### C11. Where the cards came from

| Field | Value |
| --- | --- |
| Claim | The cards started with problems the owner met. |
| Allowed wording | Most come from a failure seen in real work. Two, `im-down` and `im-up`, were designed. The owner's line: *Skills that started with problems I encountered.* |
| Forbidden wording | Every skill came from an incident. |
| Evidence | `README.md:10`; `VERBATIM.md:72-76`; each card's `EVIDENCE.md` Origin row. |
| Status | **ALLOWED** |

### C12. Standing cost

| Field | Value |
| --- | --- |
| Claim | Each model-invocable card adds a cost to every session. |
| Allowed wording | Each skill adds one line to every session, about 44 to 63 tokens, measured by `skill-harness skill audit` on 2026-09-22. |
| Forbidden wording | A cost figure with no instrument or date. A claim that a card costs nothing until it fires. |
| Evidence | `README.md:47`; `CATALOG.md:12-14`; CI job `validate_standing_costs.py`. |
| Status | **SCOPED** to the audit date. |

### C13. What a version promises

| Field | Value |
| --- | --- |
| Claim | The install path, the card format and a card's name are the declared surface. The card set is not. |
| Allowed wording | The site and `CATALOG.md:261` wording. |
| Forbidden wording | Wording that implies the card set is stable across a minor release. |
| Evidence | ADR 0002, *What the version number promises*; ADR 0003, *Decision*. |
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
| `README.md:10`: *Claude Code skills for mistakes that report success.* | C1, C2. | CANDIDATE, *agent-drafted*: *Skills for mistakes that report success.* |
| `README.md:10`: *Any Claude Code user can hit these failures.* | C2: the failures are not specific to Claude Code. | CANDIDATE, *agent-drafted*: *Anyone working with a coding agent can hit these failures.* |
| No line about Pi. Zero occurrences of the word Pi on 2026-10-17. | C2. | CANDIDATE, *agent-drafted*, placed before the install section: *Pi is the runtime this work targets first. There is no tested Pi install yet. The install below is for Claude Code, the install route that has a receipt today.* This is the C2 allowed wording with the C3 gap beside it. The first draft of this row was in the first person. `scripts/validate_voice_provenance.py` refuses a first-person public line that `VERBATIM.md` does not record, so the row was changed on 2026-10-17. |
| No line about the knowledge base. | C14. | CANDIDATE, *agent-drafted*: *The repository is also a record: the evidence, explanations and failures behind each card.* |
| `README.md:24`: *Or install everything with `npx skills add MrBinnacle/skills`.* | C7. | CANDIDATE, *agent-drafted*: remove the sentence until a current receipt exists, or add *untested since v3.0.0* beside it. |
| `README.md:37-45`: the 2.1.287 receipt. | None. It agrees with C6. | No change to the receipt. CANDIDATE, *agent-drafted*, added to the install section for the #443 *Accurate install wording* box: *On Windows, if you set `CLAUDE_CONFIG_DIR` to a path longer than 108 characters, run `git config --global core.longpaths true` before you add the marketplace. At 108 characters or fewer, the HTTPS form installs without it. Measured with Claude Code 2.1.302 on 2026-10-17 (#452).* C6 covers the measured limit. It covers the remedy only as git's setting. |
| `README.md:47`: the standing cost. | None. | No change. |
| `README.md:83-87`: what comes with each skill. | None. It agrees with C8. | No change. |
| `README.md:89`: *No skill claims a measured benefit yet.* | None. | No change. |
| `README.md:93`: *or when a model or Claude Code change makes it unnecessary.* | C2, minor. | CANDIDATE, *agent-drafted*: *or when a model or runtime change makes it unnecessary.* |
| `README.md:4`: banner alt text. | None. It agrees with C8. | No change. |

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
| `CATALOG.md:235-243`: the *Installer* paragraph and the command `npx skills add MrBinnacle/skills`, with no qualifier. Added to this sweep 2026-10-17 at `bc28253`. | C7. | CANDIDATE, *agent-drafted*: keep the paragraph, and add after the command block: *This route has no install receipt since v3.0.0 changed the install path, so what it installs from the current tree is untested.* |

`AGENTS.md:57` is not a public surface. It is the conventions file for agents working here. It
still says *`npx skills add MrBinnacle/skills` is the other supported route*, and C7 forbids
that as a current claim. CANDIDATE, *agent-drafted*: *`npx skills add MrBinnacle/skills` is
published as a second route, with no install receipt since v3.0.0; it writes a
`skills-lock.json` and tracks `main` rather than a tag.*

## What this record does not settle

- It approves no wording. Gate `public-copy-approval` holds every CANDIDATE.
- It does not choose the About description. Gate `repo-description` holds that choice.
- It does not run an install. C3, C6 and C7 change only when a new receipt exists.
- A wording change that follows from this ledger needs its own pull request and the owner's
  approval before merge.
