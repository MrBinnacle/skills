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

**Amended 2026-10-21** against `main` at `62a7e0a`, for
[#576](https://github.com/MrBinnacle/skills/issues/576). The README rewrites in #561, which
applied the #547 ruling, and #565 moved or removed the lines that the C6, C9, C10, C11 and
C12 Evidence cells and the S2 rows cited. Each root `README.md` citation in those cells now
quotes the text it relies on, and its line number is read at `62a7e0a`. The S2 *Current text*
cells describe the README as it is at that revision, re-read whole the same day. Text the
README no longer carries is marked as history in words, with the rewrite that removed it, found
with `git log -S`. Every other citation keeps the revision it names.

**Amended 2026-10-23** against `main` at `b9e0bea`. S3 adds the row for `site/index.html:147`.
That line called Pi the runtime this work targets first, which C2 has forbidden on a public
surface since the #547 ruling. #561 fixed the README for that ruling. The site was in no copy
check and in no row of this sweep, so the line stayed. The same change removes the sentence and
adds `public_claims` to `assets/tokens.json`: `scripts/validate_brand_kit.py` now refuses the
C2 wording on the site, the README, the SVG assets and the repository description. The pattern
names the receipt that would lift it, a Pi install receipt under `docs/product/receipts/`, so the
refusal ends when the missing fact exists. C4 gains a public form: the owner ruled on 2026-10-23
that a public surface may say how far Pi works with the cards today, and how and why, within the
evidence C4 and C5 cite. The ruling was given in a working session and is recorded here.

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

Citations take the form `file:line` at the revision named above. A citation to the root
`README.md` also quotes the text it relies on, because the README is rewritten often. When the
line number and the quote disagree, the quote names the text, and the line number is stale. A
citation to a command names the command and its output.

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
| Allowed wording | On a public surface: the install is for Claude Code, and an install for Pi is planned and untested. Internal records may say that Pi is the runtime this work targets first. |
| Forbidden wording | Any wording that makes the direction read as delivery: Pi support, works on Pi, runs on Pi, built for Pi and Claude Code alike. On a public surface, any wording that calls Pi the primary, first or main runtime while no tested Pi install exists. |
| Evidence | `PRODUCT.md:17-19`; `PRODUCT.md:123-124`: a public surface must not imply that every intended capability already exists. The maintainer's ruling on [#547](https://github.com/MrBinnacle/skills/issues/547#issuecomment-6305476405), 2026-10-20: "Either ship a tested Pi path or stop calling it primary on the public surface." C3 records that no tested path exists. |
| Status | **INTENT** internally. On a public surface, the primary-runtime wording is **FORBIDDEN** until C3 has a receipt. |

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
| Allowed wording | On 2026-10-17, a configured Pi 1.3.0 setup on the owner's machine loaded cards from explicit paths. Provider delivery and body invocation were not measured. On a public surface, from the owner's ruling of 2026-10-23, the same facts with how and why: the cards use the open Agent Skills `SKILL.md` format, which Pi also reads; Pi 1.3.0 loaded them from a local checkout when given their paths by hand; there is no Pi install package; whether the cards change how Pi behaves has not been measured. The reason may be stated as direction: one shared format lets a card be written once rather than once per runtime. |
| Forbidden wording | Any wording that turns this loader observation into an install route, a package, or runtime parity. |
| Evidence | `docs/product/runtime-delivery-matrix.md:88-89`. |
| Status | **SCOPED** to that configuration and date. It is not install guidance. Public use is **ALLOWED** in the public form above, with the date, the version and the two limits beside it. |

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
| Evidence | `README.md:93-105`, in *Install*, the commands and the reload (*The cards appear after `/reload-plugins`.*); `README.md:121`, the Windows limits (*On Windows, keep the path of your Claude configuration directory (`CLAUDE_CONFIG_DIR`) at 108 characters or fewer.*); `README.md:125-131`, the verified forms (*Verified forms, Claude Code 2.1.287, from a clean `CLAUDE_CONFIG_DIR` with no SSH key*); `docs/product/runtime-delivery-matrix.md:92`: historical install success does not attest current bytes. `docs/product/runtime-delivery-matrix.md:111-116`: a 2.1.296 temporary install found cards in all three plugins, and the suite failed one version assertion. [#452](https://github.com/MrBinnacle/skills/pull/452) (`31fe859`), section *Reproduction, measured on 2026-10-17*: Windows 11, Claude Code 2.1.302, git 2.56.0.windows.1, `core.longpaths` unset at every scope. The HTTPS form, bisected on the config root, succeeds at 108 characters and fails at 109 (108 + 59 + 80 = 247, the directory limit). A cold install from a 37-character root succeeded. `scripts/validate_install_paths.py` fails CI on any tracked path over that budget. #452 closed #356. [`receipts/2026-10-17-windows-long-config-root.md`](receipts/2026-10-17-windows-long-config-root.md): a control run at a 109-character root with `core.longpaths` unset failed as #452 recorded. With the setting at global scope, `marketplace add` and all three installs succeeded at roots of 109, 140 and 157 characters, at commit `eecd5a5`. `claude plugin list`, `plugin details` and `plugin validate` then read all three plugins back without a model call. A bisection found that 157 passes and 158 fails with `fatal: '$GIT_DIR' too big`. The host had `LongPathsEnabled` = 1, and skill loading at session start was not tested. Microsoft Learn, *Maximum Path Length Limitation* (updated 2025-04-15): from Windows 10 version 1607, long paths need an opt-in, and the `LongPathsEnabled` registry value "must exist and be set to `1`". |
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
| Evidence | `README.md:10`, *No skill here has been shown to make an agent less likely to repeat its failure*; `README.md:45`, *No skill claims a measured benefit yet*, beside the `CANT_TELL_YET` verdict for `pull-rebase`; `CATALOG.md:19-20`; `skills/engineering/pull-rebase/EVIDENCE.md:12-13`; `PRODUCT.md:141`; `BRAND.md:50`. |
| Status | **FORBIDDEN** as a benefit claim. The absence statement is **ALLOWED**. |

### C10. Admission

| Field | Value |
| --- | --- |
| Claim | Published cards passed the admission policy. |
| Allowed wording | Most published cards do not yet meet all four admission questions on recorded evidence. |
| Forbidden wording | Every skill passed admission. |
| Evidence | `README.md:83`, in *How cards get in and out*, *Not every published card meets the rule* and *Most did not pass all four questions on recorded evidence*; `CATALOG.md:67-72`; `dispositions/2026-08-15-S295-admission-triage.md`. |
| Status | **ALLOWED** in the stated form. |

### C11. Where the cards came from

| Field | Value |
| --- | --- |
| Claim | The cards started with problems the owner met. |
| Allowed wording | Most come from a failure seen in real work. Two, `im-down` and `im-up`, were designed. The owner's line: *Skills that started with problems I encountered.* |
| Forbidden wording | Every skill came from an incident. |
| Evidence | `README.md:12`, *Most records started from one failure in the work of the maintainer* and *Two skills, `im-down` and `im-up`, were designed on purpose rather than written after a recorded incident*; `VERBATIM.md:72-76`; each card's `EVIDENCE.md` Origin row. |
| Status | **ALLOWED** |

### C12. Standing cost

| Field | Value |
| --- | --- |
| Claim | Each model-invocable card adds a cost to every session. |
| Allowed wording | Each card not marked "by hand" adds one line to every session: about 70 to 80 tokens, as `/context` counts it (Claude Code 2.1.305, measured 2026-10-20). That holds when the host lists the card with its description. A host that lists it by name only charges under 20. |
| Forbidden wording | A cost figure with no instrument or date. A claim that a model-invocable card costs nothing until it fires. The `skill-harness skill audit` figures stated as what a session pays: [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476) found none of them within 10% of `/context`. |
| Evidence | `README.md:14`, in the opening section, *about 70 to 80 tokens per skill as `/context`, Claude Code's own context counter, counts them*, and `README.md:21`, *A group costs 70 to 80 tokens per session*. The figure sat in `## Install` after the front-page rewrite of 2026-10-20 and moved out of it in #561. `README.md:77` names the other counter: *a different counter, `skill-harness skill audit`*. [#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476), the pre-registered `/context` measurement, and [#532](https://github.com/MrBinnacle/skills/pull/532), which put it on the README; `CATALOG.md:12-14`. Each card's `Standing cost` row keeps the harness figure from the audit date that row states, where it states one. The rows for `im-up`, `im-down` and `closure-mode` state a zero cost and no audit date. CI job `validate_standing_costs.py` checks those rows against `scripts/standing-costs.json`, a snapshot measured by `skill-harness skill audit` on 2026-10-22. |
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
| `README.md:10`: *This repository is a set of written records of failures, mistakes that coding agents made in real engineering work.* The same paragraph says *Each record also comes with a skill*. History: on 2026-10-17 the line read *Claude Code skills for mistakes that report success.* #456 replaced it with *Skills is a knowledge base and a set of skill cards for engineering work with frontier models.*, at `README.md:12`, and #561 removed that sentence. | None now. It defines the product as records and skills, not as cards alone or by one runtime, which agrees with C1. | No change. |
| `README.md:12`: *other developers who work with a coding agent*. History: on 2026-10-17 `README.md:10` read *Any Claude Code user can hit these failures.*, which #456 removed. | None now. It agrees with C2 and C15. | No change. |
| `README.md:91`, the first line of *Install*: *The install below is for Claude Code. An install for Pi, another coding agent, is planned and untested.* It is the only line that names Pi. History: on 2026-10-17, before #456 (`296c0cd`) merged that day and added a line that names Pi, the word Pi did not occur in the README. A line that called Pi the runtime this work targets first then landed before the install commands (`README.md:52` at `3605a52`), and #561, which applied the #547 ruling, replaced it with the line quoted here. | None now. It agrees with C2 as amended on 2026-10-20 for the #547 ruling, and with C3. The line it replaced conflicted with C2. | No change. History: the earlier candidate, withdrawn from public use, was *agent-drafted* and placed before the install section: *Pi is the runtime this work targets first. There is no tested Pi install yet. The install below is for Claude Code, the install route that has a receipt today.* It was the C2 allowed wording with the C3 gap beside it. The first draft of this row was in the first person. `scripts/validate_voice_provenance.py` refuses a first-person public line that `VERBATIM.md` does not record, so the row was changed on 2026-10-17. |
| `README.md:14`: *Treat the records as documentation. They are the main thing this repository offers, and reading them costs nothing.* The README does not use the words *knowledge base*. History: #456 stated it in those words, and #561 removed them. | None now. It states C14 in other words. | No change. |
| The README does not mention `npx skills add`. History: on 2026-10-17 `README.md:24` read *Or install everything with `npx skills add MrBinnacle/skills`.*, which #456 removed. | None now. | No change. |
| `README.md:93-105`, in *Install*: the two commands and the reload, from *Run these two commands one at a time* to *The cards appear after `/reload-plugins`.* `README.md:121`: *On Windows, keep the path of your Claude configuration directory (`CLAUDE_CONFIG_DIR`) at 108 characters or fewer.* `README.md:125`: *Verified forms, Claude Code 2.1.287, from a clean `CLAUDE_CONFIG_DIR` with no SSH key*. | None. It agrees with C6. | No change. The Windows sentence at `README.md:121` is the *agent-drafted* CANDIDATE this row drafted for the #443 *Accurate install wording* box, and it landed as written in #456. C6 covers each number and each condition in it. The sentence says the install works, not that the skills work, and front-door copy must keep that scope. |
| `README.md:14`: the standing cost, *about 70 to 80 tokens per skill as `/context`, Claude Code's own context counter, counts them*. `README.md:21` repeats the figure per group: *A group costs 70 to 80 tokens per session*. | None. It agrees with C12. | No change. |
| `README.md:18`: *a card is one skill together with its two records*, the failure log and `EVIDENCE.md`. `README.md:4`, the banner alt text, names the retirement condition. History: the section that listed what comes with each card was removed by #561. The README does not mention a card's test cases. | None. It states less than C8 allows, and nothing C8 forbids. | No change. |
| `README.md:10`: *No skill here has been shown to make an agent less likely to repeat its failure.* `README.md:45`: *No skill claims a measured benefit yet.* | None. It agrees with C9. | No change. |
| `README.md:85`, in *How cards get in and out*: *A card leaves on a measured result, on the platform change its record named in advance, or when its own record fails the admission rule outright.* History: on 2026-10-17 `README.md:93` read *or when a model or Claude Code change makes it unnecessary.*; #456 changed *Claude Code* to *runtime*, the #540 rewrite replaced the clause with *the platform change its retirement condition names*, and #561 replaced that. | None now. It names no runtime. | No change. |
| `README.md:4`: banner alt text, *skills. Each card states the condition that would retire it.* | None. It agrees with C8. | No change. |

### S3. Site title, description and Open Graph tags

| Current text | Conflicts with | CANDIDATE |
| --- | --- | --- |
| `site/index.html:6`, `:10-11`: title and `og:title`, *MRBINNACLE / skills* | None. | No change. |
| `site/index.html:7-9`, `:135`: *Skill cards that each state the condition that would retire them.* | None on substance: C8 supports it. C1 on register only, because it describes the product as cards alone. | CANDIDATE, *agent-drafted*: keep the line. Whether the description should name the knowledge base is a register decision, and it is the owner's. |
| `site/index.html:19-20`: image alt *MRBINNACLE / skills* | None. | No change. |
| `site/index.html:137`: *Skills that started with problems I encountered.* | None. Quoted from `VERBATIM.md:76`. | No change. |
| `site/index.html:140`: *Install in Claude Code* | None. It is scoped to one runtime, which agrees with C2 and C6. | No change. |
| `site/index.html:147`: *There is no tested Pi install yet.* History: from #456 (`296c0cd`, 2026-10-17) to 2026-10-23 the line began *Pi is the runtime this work targets first.* That sentence conflicted with C2 after the #547 ruling of 2026-10-20, and the change that added this row removed it. | None now. It is the C3 gap statement. | No change. `scripts/validate_brand_kit.py`, which runs on every pull request, refuses the removed wording on this page through the `public_claims` block in `assets/tokens.json`. |

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
