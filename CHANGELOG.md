# Changelog

All notable changes to the collection. A release is a delivery event: changed cards reach
installed users when a version is released, not on every merge to `main`. See
[ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) for what a version promises.

## v1.4.0 — 2026-08-31

### Minor Changes

- [#202](https://github.com/MrBinnacle/skills/pull/202) [`ef5adf5`](https://github.com/MrBinnacle/skills/commit/ef5adf524f6fa9f3ead8a2cb4fd00886cbb759f9) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Retire `skill-necessity-gate`. The collection removed its own gate card because the gate card
  could not pass its own gate.

  `ADMISSION.md` criterion 1 requires an unaided failure that was observed, not predicted. The
  card's own `EVIDENCE.md` answered `Occasions counted | 0 — no triggering occurrence`, and no
  occurrence appeared across the card's whole life. The defect is not repairable by rewriting: an
  occurrence can only be found. The S295 admission triage recorded the card `RECURRENCE-THIN` on
  2026-08-15 and deferred the call; this change makes it.

  A third retirement route is added to `AGENTS.md` before it is used. **Withdrawn on the policy**
  covers a published card removed because it cannot satisfy the admission policy it is measured
  against, with the card's own evidence record as the proof and no screen required, because the
  failing criterion counts occurrences rather than measuring lift. The route is written narrowly:
  it fires on a criterion the card's own record demonstrably fails, and the changeset must quote
  the failing row.

  Two rules outlive the card and move into `AGENTS.md` in the same commit that removes the
  directory:

  - **The topology rule** (the card's Gate 3) becomes a rule in its own right — decide
    model-invocable against procedure by asking who does the strategic thinking, treat side
    effects as procedure, and surface the standing-cost maths so the human makes the close calls.
    `AGENTS.md` and `closure-mode-at-boundaries`'s evidence record both cited Gate 3 and now cite
    a rule that exists.
  - **No self-authority** — a card's name, its role in this repository, its prior use, and the
    decisions it produced are not evidence for a verdict it reaches. This was unwritten anywhere
    in the repository while the retirement's own argument depended on it.

  `ADMISSION.md` keeps its four questions unchanged and loses only its reference-method pointer.
  The naming table drops the "gate card" term.

  One reduction in assurance is accepted and named rather than slipped in: the policy-to-card
  version lockstep in `scripts/validate_scoreboard.py` is removed with the card it compared
  against. `ADMISSION.md` must still declare exactly one canonical version, which is the stronger
  half of that check.

  Conformance machinery follows the removal. The `admission-version-drift` poison fixture is
  deleted rather than repaired, because its entire purpose was a disagreement between the policy
  file and the gate card's header and there is no longer a second copy of the version to drift
  from. The other three drift fixtures keep their breach and lose their gate-card scaffolding;
  each was re-run and confirmed to still fail on its own named assertion rather than on an exit
  code. The CI malformed-frontmatter poison control is repointed at `router-skill-predicate-gap`
  and gains an existence assertion, so a future removal cannot make it vacuous in silence.

### Patch Changes

- [#185](https://github.com/MrBinnacle/skills/pull/185) [`b0a77a1`](https://github.com/MrBinnacle/skills/commit/b0a77a19ec3315b27abc26a60fb6fcdd62b33759) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `subagent-research-reliability`: add the batched-nudge variant under the dead-letter rule. On 2026-08-26 the single-message contract-restating nudge failed twice on a large deliverable and recovered a second large one only when the nudge named an explicit batch split; small and medium deliverables returned first try. The card now says: size the output contract at dispatch, license a partial return explicitly, batch large returns, and stop after two failed nudges. One published card changed.

- [#180](https://github.com/MrBinnacle/skills/pull/180) [`ee1afbc`](https://github.com/MrBinnacle/skills/commit/ee1afbc3beb6afd5b9851d786487ac04b127057e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - CI: every `out="$(...)"` capture under `set -e` in `tests.yml` now carries a failure branch (`|| { echo "$out"; exit 1; }`), so a failing check's own diagnostic reaches the job log instead of being discarded at the assignment. Twenty sites fixed ([#172](https://github.com/MrBinnacle/skills/issues/172); [#170](https://github.com/MrBinnacle/skills/issues/170) fixed the twenty-first). A new suite, `scripts/test_captured_exit_handling.py`, parses the workflow and refuses any capture without the branch, and is itself wired into the workflow. No published card changes.

- [#197](https://github.com/MrBinnacle/skills/pull/197) [`d45d59d`](https://github.com/MrBinnacle/skills/commit/d45d59d36e69df7ea58bcc7eb84cc17dc4ee82a9) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The collection consumes the Taste prose style. The six rules are vendored byte-equal from the
  sibling measurement repository and pinned by SHA-256, so a local edit fails rather than forking
  the style silently. A seventh rule renders from the brand kit's banned-marketing word list and
  is bound only to the public surfaces that file declares. Contributors get pre-commit and
  commit-msg hooks; both report at error level, which no row uses yet, so they install the carrier
  without changing what a commit is refused for today.

- [#186](https://github.com/MrBinnacle/skills/pull/186) [`bb94bf5`](https://github.com/MrBinnacle/skills/commit/bb94bf50ed2fc37e195865a5a258fc4708bcf89f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `scripts/validate_conformance.py`: O5 gains an optional `--harness-root <path>`. Without it, O5 stays `CANNOT-CHECK`, so CI never prints a green line for a check that did not run. With it, O5 reads the receipt each card's controlled row links in its `Receipt:` clause (markdown-link or backtick form) and fails on four conditions: the receipt file is absent; its `subject_identity.skill_id` differs from sha256 of the card's `SKILL.md`; its `verdict` differs from the row's opening verdict word; a newer receipt with the same `skill_id` exists that the row does not link. Eight subprocess-driven cases cover the flag-less path, PASS, both clause shapes and one FAIL per condition. No published card changed.

- [#167](https://github.com/MrBinnacle/skills/pull/167) [`756403a`](https://github.com/MrBinnacle/skills/commit/756403a8036843516bc890308c6720e336e7851e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Promote `subagent-research-reliability` patch from `_quarantine/` to published tree.

  Adds the dead-letter failure mode (Check 0 — name the return channel) drawn from two
  independent occurrences (2026-08-18 and 2026-08-24). Widens Check 2 from citations to
  checked negatives. Splits examples and notes into EXAMPLES.md to stay within the 7 KB
  SKILL.md ceiling. Description rewritten to 166 chars naming the return-channel branch.
  Occasions counted rises to 5; RECURRENCE-THIN label removed.

- [#198](https://github.com/MrBinnacle/skills/pull/198) [`875ee6d`](https://github.com/MrBinnacle/skills/commit/875ee6d3d71faed0d838eacc4b229c1b1ba31f1d) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Five of the six vendored Taste rows (Brevity-and-order, Dressing, Evidence, Register, Voice) are
  now ERROR level, enforced by a second, ungated Vale pass in CI. Generic-ness stays warning: one
  hit remains in a canonical ADR this pass could not edit. Thirty-two pre-existing findings across
  the collection were fixed as uncontroversial prose corrections; one README line kept its original
  wording because it is a cited `VERBATIM.md` specimen, carved out with an inline Vale exception
  instead.

- [#173](https://github.com/MrBinnacle/skills/pull/173) [`87eadc0`](https://github.com/MrBinnacle/skills/commit/87eadc0367b922799a88d21ca57bcfe0fc3fe26e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Remove the earn/earned/earning family from prose across the collection, and add `earns` to the banned list so the guard covers the whole family.

- [#199](https://github.com/MrBinnacle/skills/pull/199) [`8b8c6d6`](https://github.com/MrBinnacle/skills/commit/8b8c6d66fe76375ca28fc360dbba463c1d462b8f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - README `What they address` now lists every published card. The section claimed the cards fall
  into four areas and then named nine of the fifteen on `main`; five of the six it omitted belong
  to its own leading category, so the section understated the collection's largest subject. The
  four areas are replaced by three groups derived from the cards' own `EVIDENCE.md` origin rows —
  reports that do not match what happened (nine cards), reports written for the next reader (five),
  and whether a control should exist (one). The section states no numeral, so it cannot fall behind
  a count. `Card map`, the evidence census, and every scoreboard value are untouched. No published
  card changed, so nothing reaches installed users. Closes [#168](https://github.com/MrBinnacle/skills/issues/168).

- [#189](https://github.com/MrBinnacle/skills/pull/189) [`fa786cf`](https://github.com/MrBinnacle/skills/commit/fa786cf0236356a2b6664a64d546647ce5a8dad5) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `AGENTS.md`: the rotation pass gains the receipt path as steps inside the existing ritual. Two triggers (on arrival of a receipt for a published card; at the rotation pass, sweeping `docs/sers/receipts/` at a declared harness commit). One Inputs row declaring the harness release the collection judges against. A currency gate with typed fail-closed reasons (`no_skill_id`, `card_hash_mismatch`, `no_harness_version`, `harness_mismatch`, `oracle_stale`, `model_drift`, `no_trigger_row`, `attestation_missing`, `attestation_expired`, `trigger_fired`, `arm_coverage`); a not-current receipt disposes nothing and the row reads `CANT_TELL_YET (stale receipt: <reason>)`. A record step fixing the controlled-row shape with a commit-pinned `Receipt:` clause. A dispose step routing `CUT` through Retirement's first route, renamed from "Screen null" to "Harness cut". `RETIRED.md` evidence cells link the receipt at the harness commit. The O5 `--harness-root` run is a named step, and the Done-when bar requires every receipt-matched published card to carry its verdict or a typed not-current reason. No published card changed.

- [#190](https://github.com/MrBinnacle/skills/pull/190) [`f42d167`](https://github.com/MrBinnacle/skills/commit/f42d16775cd398c1453023163a07e3ef155633ab) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `git-pull-rebase-trap` Screen result rewritten to the receipt-row shape (commit-pinned Receipt clause, dated 2026-07-20, typed reason `wrong_instrument (trap-discipline); not current: no_skill_id`). `RETIRED.md` screened-out cell for `append-only-evidence-design` amended to cite its receipt as `CANT_TELL_YET` / `wrong_instrument (calibration)` rather than ceiling. Worked examples of the row shape from [#183](https://github.com/MrBinnacle/skills/issues/183); O5 with `--harness-root` reports the expected not-current FAIL.

- [#203](https://github.com/MrBinnacle/skills/pull/203) [`5eaecb6`](https://github.com/MrBinnacle/skills/commit/5eaecb68c8d58bedd7fa1888822036397e51454a) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `im-up` and `im-down`: a passing receiver check no longer buries the verdict under its own stdout.

  `rerun_checks` captured 2000 characters of stdout and 2000 of stderr for every receiver check, whether it passed or failed. A caller running twenty checks received a receipt carrying up to eighty kilobytes of `ok ...` lines, and had to filter the receipt to find out whether the receipt was accepted. A receiver check signals through its exit code: on a pass its stdout is decoration, and on a fail it is the whole diagnostic.

  A passing check now records `"output": "omitted: check passed, exit code is the verdict"`. A failing check keeps both streams, truncated as before.

  The omission is recorded rather than silent. An absent `stdout` field would read as "this check printed nothing", which is a different claim from "this check passed and its output was dropped", and only the second is true.

  Both published copies of `validate_packet.py` remain byte-identical to each other. The change was exercised end to end on 2026-08-31 across twenty configured checks, with the failing check's diagnostic preserved in full.

- [#179](https://github.com/MrBinnacle/skills/pull/179) [`4b6bd99`](https://github.com/MrBinnacle/skills/commit/4b6bd9971a9d11a8ed58716508954364527fcc9b) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record the [#133](https://github.com/MrBinnacle/skills/issues/133) ruling on `downstream-instruction-framing`: the two guard-caught 2026-08-04/05 candidates are known negatives under the operationalization a cross-family panel upheld (the count row records forbidden framing in a persisted artifact a later reader could consume). RECURRENCE-THIN stands; the im-up candidates and the pre-origin-corroboration fork remain open.

- [#165](https://github.com/MrBinnacle/skills/pull/165) [`3c09013`](https://github.com/MrBinnacle/skills/commit/3c090139abaefb6b1b81e04b2d279b5e3de68af7) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - AGENTS.md gains "An issue you did not create": the routing for externally filed issues.
  Triage and reproduce before building; a confirmed report about a published card is counted
  as an occurrence before any fix lands; only a verified leaf ticket gets `ready-for-agent`;
  pipeline tickets are never re-triaged. Written now, before the first outside issue arrives,
  so the first one is routed instead of improvised.

- [#166](https://github.com/MrBinnacle/skills/pull/166) [`4af6db2`](https://github.com/MrBinnacle/skills/commit/4af6db277fa3e15f4ad00aa101f16ab9ce06ff9d) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The skill-invocation phrase in AGENTS.md widens past skill-to-skill. "Call the Skill tool with
  `skill-name`." now covers every place an agent reads an instruction to reach for a skill —
  inside a card, in a slash command, in an AGENTS.md line, in a subagent dispatch — because none
  of the last three sit inside a card and all three had the same inference problem. The same line
  records that composing skills this way is endorsed: a card needing a discipline another card
  already carries delegates to it rather than restating it, which keeps one meaning in one place
  and keeps both cards inside the size bounds stated two lines above.

  `applied-layer-answer-hides-the-governing-result` enters `_quarantine`. It was written to disk
  in a prior session and never committed, so it sat in the working tree while absent from the
  repository — and because the spec gate reads tracked files, the gate had never checked it. The
  gate now covers 32 cards where it covered 31. Admitting it required meeting the size bounds:
  `SKILL.md` was 9,183 B against a ~7 KB ceiling, so the worked example moved to a sibling file
  reached by a pointer, leaving 6,369 B. Reading the conventions at source turned up three further
  fixes — the description was 802 characters against a stated bound of 200 that 14 of 15 published
  cards already meet, a trailing "See also" section violated the inline-at-moment-of-need rule, and
  a References section explained why there were no references, which changes no reader's behaviour.

- [#196](https://github.com/MrBinnacle/skills/pull/196) [`642152e`](https://github.com/MrBinnacle/skills/commit/642152e75d60e18c16f71bf5f2099afee0da3b1d) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Add an SVG source for the social preview card, built to the S371 direction brief: three blocks (lockup, owner-typed statement, install route), declared structural neutrals only, live text nodes so `validate_brand_kit.py` scans it. Correct `tokens.json`'s two stale `#2da44e` assertions to the measured `#3fb950` (3,420 exact fills counted twice, independently). The PNG export and GitHub upload remain the owner's step.

- [`c3c954e`](https://github.com/MrBinnacle/skills/commit/c3c954e5719380f0a63d7a375ea9af9df23dc855) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Track four quarantine candidates that were sitting untracked and blocking the release gate at G9.

  `_quarantine/` is a tracked, unshipped candidate area — sixteen candidates already sit there committed. These four were extracted and left untracked, so `git status --porcelain` reported them as a dirty tree and `release_gate.py --release` returned `BLOCKED` on G9. Tracking them is what that directory is for; it ships nothing and admits nothing.

  - `agent-definition-snapshot-at-session-start`
  - `container-green-host-red-detached-child-holds-tempdir`
  - `private-steering-head-over-public-repos`
  - `squash-merge-absorbs-unpushed-base-commits`

  **None of the four is admitted, and none is promoted by this change.** `ADMISSION.md` criterion 2 requires that the failure recur independently, with occasions counted rather than predicted. Measured against the cards as written: three cite a single dated incident each, and the fourth cites three dated observations of _different_ failure modes rather than a recurrence of one. The default answer in `ADMISSION.md` is "not admitted", and it stands for all four.

  One residue fix rides along, required by the pre-commit gate: `container-green-host-red-detached-child-holds-tempdir` named a private repository and a bare cross-repository `#N` issue reference on its evidence line. Both are replaced with a generic descriptor. The bare cross-repository reference is the exact defect that `private-steering-head-over-public-repos` — one of the other three cards in this changeset — exists to describe.

  Promotion for any of these remains open and needs what promotion has always needed: a counted second occurrence, an `EVIDENCE.md` with its three contractual rows, and the gauntlet run in order.

- [#192](https://github.com/MrBinnacle/skills/pull/192) [`c0b29c1`](https://github.com/MrBinnacle/skills/commit/c0b29c1490133fd0c885ff747d5b0acfdbf8703a) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Repository automation: an issue that opens with no label now receives `needs-triage` from a workflow on `issues: opened`. An unlabeled issue is invisible to every selector that keys on a triage role, and the only guard for that ran on one host. The workflow adds the one label and touches nothing else; no published card changed.

- [#193](https://github.com/MrBinnacle/skills/pull/193) [`59ea32f`](https://github.com/MrBinnacle/skills/commit/59ea32f0e8319042a2da57916c08795ac22a407b) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `validate_voice_provenance`: extend the voice-provenance check to scan surfaces for first-person sentences that must be recorded in VERBATIM.md. The scanned surfaces are a data-driven list, so adding a further surface is a data edit. The GitHub description line is recorded in VERBATIM.md under its own dated section. Five front-page variants under `docs/design/variants/front-page/` pass the extended validator when placed as README.md.

## v1.3.0 — 2026-08-25

### Minor Changes

- [#19](https://github.com/MrBinnacle/skills/pull/19) [`9297702`](https://github.com/MrBinnacle/skills/commit/92977022e42e3e1db1c615e9ee6da4721aca1dec) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Move the published operating-rules template off the repo root, and put a real project delta
  there instead.

  A file named `CLAUDE.md` is loaded automatically as the operating rules of the directory it
  sits in. The file at this repo's root was the template published for adopters to copy — which
  describes no repo and was never meant to govern this one. So every agent that opened this clone
  loaded 384 lines of the wrong thing as its project instructions, with a paragraph of prose as
  the only correction. `AGENTS.md` had already diagnosed this in words ("not a description of how
  this repo operates"), but the placement that framing was built on never followed. This is a
  layer-placement error of exactly the kind the collection exists to catch, shipped at the root of
  the collection.

  - The template moves to `templates/BASE-OPERATING-RULES.md`. It is unchanged as doctrine; its
    header now explains why it is not filed as a `CLAUDE.md`, and it becomes one when you copy it
    to `~/.claude/CLAUDE.md`.
  - The root `CLAUDE.md` is now this repo's genuine project delta — what actually governs work in
    this clone. It is thin on purpose and points at `AGENTS.md` for the working conventions rather
    than restating them.
  - That delta also serves as the worked example the template refers to. The template previously
    offered an empty stub and a parenthetical list of what might go in one; a real delta is a
    better answer than a placeholder, and cannot drift out of date without someone noticing,
    because it is the file the repo runs on.
  - Its **Question routing** section is the part most worth copying: every question has a
    respondent, the human is the last rung rather than the first, and a fork that evidence can
    settle is not a fork.

  An earlier change ([#7](https://github.com/MrBinnacle/skills/issues/7)) moved the template _to_ the root on the grounds that it was "the repo's
  real `CLAUDE.md`", and removed `templates/` because a duplicate copy-target would reintroduce
  drift. The first premise is what `AGENTS.md` later corrected. The second concern does not apply
  here: there is still exactly one copy of the template, and the root file is now different
  content doing a different job.

  `README.md`, `AGENTS.md`, and the `.pre-commit-config.yaml` comment are updated to match, and
  `AGENTS.md` picks up the constraint as a convention so the template cannot quietly drift back
  onto a loaded path.

- [#141](https://github.com/MrBinnacle/skills/pull/141) [`7d1a4aa`](https://github.com/MrBinnacle/skills/commit/7d1a4aacdc7fab947e8b2f56a2df3bf9dfd92381) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The 200-character description bar is now a check, because three cards shipped over it the day it was left to a step.

  `AGENTS.md` step 2a has required a published description of 200 characters or fewer since the collection began, and that step was the only thing enforcing it — the file said so in its own words: _the edit is the enforcement_. On 2026-08-24 six candidates were promoted and **three shipped over the bar, at 210, 226 and 235 characters**, because the promotion pass never ran the authoring skill whose job that is.

  **This is the collection's own layer-placement rule failing on the collection.** A discipline that must fire cannot live only in a step a human or a model has to remember. The fix is not a better-worded step; it is a gate.

  `validate_card_files.py` now refuses a published card whose description is absent or over the bar, and its `PASS` line says so. **Verified against the real tree at the commit where those three shipped: the check names all three cards and states each measured length.** That is a historical defect caught, not a fixture.

  The three descriptions are rewritten to 192, 182 and 195 characters. Each keeps every distinct trigger branch it had; what came out was restatement, not coverage.

  **Why 200 rather than the specification's 1024.** An installed card's `description` is loaded at startup whether or not the card ever fires, so its length is paid for by every session in every project that installs the collection. The specification bounds what a reader can parse. This bounds what a user pays. All three breaches were comfortably inside 1024, which is exactly why the spec gate adopted in the previous change did not catch them — the two checks answer different questions and both are needed.

  **Surrounding quotes do not count against the budget.** Quoting is a YAML requirement — two published cards need it because their descriptions contain a colon — and a syntax obligation must not cost a card two characters of what it can say.

  **The fixtures were not modelling the artifact they grade.** Every fixture card in the suite wrote a `SKILL.md` of `# name` with no frontmatter at all, so none of them resembled a published card and all eleven broke the moment a frontmatter check existed. They now carry real frontmatter. A fixture that cannot represent the failure being introduced is a fixture that was only ever testing the checks it already had.

  Four cases pin the new bar: over is red and the report states the measured length; exactly 200 is green, because a check that cannot go green either way is as useless as one that cannot go red; quotes are not counted; an absent description is refused.

  **What is still not checked, stated plainly so it is not mistaken for solved.** Nothing reads a description as a _router_. A well-formed 200-character description that names none of the words a user actually types passes every gate in this repository cleanly. Length is now deterministic; wording is not, and wording is what decides whether a model-invocable card is ever reached.

  _Revisit if:_ the startup cost of a description changes — the bar is derived from what a user pays per session, not from a style preference.

- [#138](https://github.com/MrBinnacle/skills/pull/138) [`07be44e`](https://github.com/MrBinnacle/skills/commit/07be44eab36c1b5b2386c2737cb86c20b461e731) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The collection ships a distribution artifact, and CI refuses any state where it disagrees with the tree.

  Until now there was no `.claude-plugin/marketplace.json`. The only documented route in was a third-party installer named once in this file's own preamble, so the native plugin mechanism — the one a Claude Code user reaches for — did not know this collection exists. A collection nobody can install is not shipped, whatever its receipts say.

  **What ships.** `.claude-plugin/marketplace.json` declares three plugins, one per bucket: `mrbinnacle-engineering`, `mrbinnacle-orchestration`, `mrbinnacle-meta`. Together their `skills` arrays name every published card exactly once.

  **Grouping is one plugin per bucket, and that is a decision.** Any other grouping requires a hand-maintained card-to-plugin mapping, which is a second census to keep in sync with the tree — and this repository has just finished removing three separate layers that each asserted a census of the same tree. Per-bucket makes the conformance check a pure derivation with no judgement in it.

  **The front page carries an install path.** A one-line install pointer sits in the masthead and a full `## Install` section covers both routes, states where each one writes, and states no count of anything. It also says plainly that an installed card's `description` is loaded at startup whether the card fires or not, so a reader can decide to take one bucket rather than three.

  **The guard is `O7`, inside the existing obligation tuple rather than an eighth validator.** The repository already runs seven validators and seven suites, and the number of gates is itself a documented burden. `O7` asserts that the manifest and the published tree name the same cards, and it checks **both directions**:

  - a path the manifest names with no card at it, and
  - a published card that no plugin names.

  One direction would not be enough, and the receipt for that is in this repository. The sibling occasions check ran forward-only — a count could not rise without a record — and an **undercount stayed green until August 2026**, because nothing asked the reverse question. A manifest check that validates only the paths it names has exactly that hole: drop a card from the manifest and every remaining path still resolves.

  A third breach class was found by attacking the check after it was written, and it is the one that matters most. **A `_quarantine/` candidate has a real `SKILL.md`**, so a manifest naming one is neither dangling nor missing a published card — the two-direction check reported `PASS` while the manifest shipped an unadmitted card to everyone who installs. That was demonstrated green on the live tree before the category existed, and it is now `FAIL`: a named path that resolves but sits outside `skills/` is its own reported breach. The same demonstration is red now, and the failure names the candidate.

  An absent or unparseable manifest is `FAIL`, not `CANNOT-CHECK`. The file is this repository's own artifact, so its absence is a breach rather than an unanswerable question. `CANNOT-CHECK` stays reserved for what this repository genuinely cannot see from inside itself, which is `O5` and nothing else.

  **Both directions are mutation-verified, and the verification read which assertion failed by name.** Disabling the forward direction failed `O7 is FAIL when the manifest names a path with no card at it`; disabling the reverse direction failed `O7 is FAIL when a published card is named by no plugin`. Each mutation was confirmed to parse before it was scored, so neither was a stillborn mutant killed by the compiler rather than by the control. Seven fixture classes cover the space: clean, missing card, unexposed card, absent manifest, malformed JSON, one card named twice, and a quarantine candidate exposed.

  One suite assertion was caught being vacuous during that work and fixed: it searched the whole report for a card name, and the card name appears in the report as its own row heading regardless. Both name-checking assertions now read the `O7` line specifically. That is this collection's own `success-test-accepts-any-output` card, applied to the change that adds a control.

  **The conformance edition is now `conformance v2`.** Adding a standing obligation is a material change to the obligations, and that section's own bump rule says a material change bumps the version. Editorial changes do not.

  **One acceptance criterion is met in substance rather than to the letter, and it is flagged rather than quietly satisfied.** The ticket asked for the install section in the first screen. An existing guard, `test_readme_admission_lead.py`, pins Admission method, Card map and Card evidence as the first three `H2` sections — the front page leads with the rule that governs membership, not with promotion. Rather than weaken an owner-set guard to satisfy a new ticket, the install _pointer_ sits in the masthead above every `H2`, and the full section follows the pinned three. Both constraints hold. If the intent was that the full section must lead, that is a change to the admission-lead guard and belongs in its own decision.

  _Revisit if:_ a bucket is added or renamed, at which point the manifest gains a plugin and `O7` reds until it does.

- [#134](https://github.com/MrBinnacle/skills/pull/134) [`f539b47`](https://github.com/MrBinnacle/skills/commit/f539b4747ccd55eefd6e1b7a7746ca93efe50f1b) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Promote six cards out of `_quarantine/` into the collection, and stop the page counting itself.

  These are the first promotions the collection has made. Twenty-two candidates had accumulated
  in `_quarantine/` since the mechanism was staged on 2026-08-19 and none had ever moved; every
  previously published card entered before quarantine existed. The gap was not a shortage of
  evidence. It was that the maintenance pass which was supposed to move them described itself as
  a hygiene sweep, ended its output contract at "branch to PR", and kept no field capable of
  recording a promotion — so ten logged passes moved zero cards while executing their own
  procedure faithfully.

  Promoted, each by `git mv` so the card keeps its history:

  - `engineering/pretooluse-bash-guard-prose-false-positive` — a `PreToolUse` Bash guard reads
    the whole command string, so it blocks the commit message, heredoc or document that only
    mentions what it forbids. Four counted occasions across three projects and four guards.
  - `engineering/success-test-accepts-any-output` — a check that accepts any non-empty output
    passes when the operation failed, because failure output is non-empty too. Two counted
    occasions, the second in the mirror direction: a probe reporting NOT-FOUND for a whole batch
    because the tool never ran.
  - `engineering/halt-as-deliverable` — when a pre-registration or pre-flight gate refuses to
    produce the thing you came for, the refusal is often worth more than the thing. Three counted
    occasions across two projects.
  - `engineering/mock-masked-stub-trap` — an implementation reports all gates green while a
    load-bearing branch is stubbed in production, because the test patches the helper that is the
    stub. One counted occasion; carries `RECURRENCE-THIN`.
  - `engineering/click-clirunner-env-none-deletes` — Click's `CliRunner.invoke(env=...)`
    overrides only the keys the dict names, so a key omitted is not deleted. One counted
    occasion; carries `RECURRENCE-THIN`.
  - `meta/router-skill-predicate-gap` — a router rule can be live, healthy and match nothing
    anyone types. Two counted occasions.

  Each card gained the published contract it lacked: an `EVIDENCE.md` stating all three enforced
  rows, an `evals/` corpus, normalized frontmatter, and a description rewritten to the
  200-character router bar that every published card already met and no candidate did.

  Three counts are deliberately lower than the dated records would support. Two tracks in one
  session, and a retry loop and a test harness in one session, are each counted as one occasion,
  because ADMISSION.md criterion 2 refuses a count inflated by fan-out from a single run. One
  card's second dated event is link rot in its own citations rather than another instance of its
  trap, and is not counted at all.

  `click-clirunner-env-none-deletes` had its load-bearing library claim re-checked against the
  current published Click source. The signature still types the parameter
  `Mapping[str, str | None] | None`, which is the evidence that `None` is a delete rather than an
  omission. The claim survived; the version pin was dropped, because a version number rots on the
  library's schedule and the signature does not.

  **The page no longer counts itself.** `README.md` stated the collection's size in four places
  and its origin tiering in two, and `scripts/validate_scoreboard.py` _required_ those two tier
  statements to exist — so every admission and every retirement turned the build red until
  someone re-derived the arithmetic by hand, in prose no reader had asked for. The same pin sat
  inside `scripts/test_validate_card_files.py` as the literal `9 published card(s)`, and as a
  hard-coded six-and-three split of which cards carry `RECURRENCE-THIN`. All of it is gone. The
  guarantee that remains is the one worth keeping: any tally the page states must agree with the
  records, and zero tallies is now the expected case. The test suite asserts the label rule as an
  invariant read from each card's own row instead of a roster, and both directions of that
  assertion were verified to fail by name under a deliberate mutation.

  This is the same reasoning that retired the banner's counts on 2026-08-23. A surface that must
  track repository state is a maintenance tax. The receipts live in the cards.

- [#160](https://github.com/MrBinnacle/skills/pull/160) [`d5044da`](https://github.com/MrBinnacle/skills/commit/d5044da24431a45481ef20a4a83b339ec70a0353) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The release gate re-asserts the obligations that already hold on every pull request at the moment a version becomes permanent -- the `--release` run of `scripts/release_gate.py` ([#152](https://github.com/MrBinnacle/skills/issues/152)).

  Three checks join G1-G4 as release-time siblings, each because a one-directional or absent version of it has already failed here:

  - **G5 - the manifest and the published tree name the same cards, both directions.** O7 was forward-only once and an undercount stayed green until August 2026, because nothing asked the reverse question. A manifest check that validates only the paths it names has the same hole: drop a card from the manifest and every named path still resolves. Delegated to `validate_conformance.check_plugin_manifest` rather than restated.
  - **G6 - the external specification validator is clean over the published tree.** `skills-ref` is the only conformance instrument here the maintainer did not author, which is exactly why it caught two PUBLISHED cards carrying invalid YAML frontmatter that every repository-local gate passed. Re-run as a subprocess at release, so a direct push that bypasses the per-PR spec-conformance job still meets the spec before the version becomes permanent.
  - **G7 - every workflow `uses:` action is pinned to a full 40-hex commit SHA.** [#147](https://github.com/MrBinnacle/skills/issues/147) pinned every action; G7 keeps it from rotting back. A floating tag is not a pin (CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside 24 hours), so any `uses:` whose ref is not a 40-hex SHA is a listed failure naming the file, the line, and the mutable ref.

  Each ships its own poison control under the release-gate job in CI, asserting its own distinguishing message and a single-reason refusal. The release-gate job now sets up node (pinned) so the G6 control can run `npx`; that line is itself a `uses:` G7 re-asserts is pinned. G5's only skip is O7's own vacuum ("checked nothing") — the seeded-fixture state — so a missing `skills/` directory whose manifest still names cards is refused rather than skipped. G6 skips a non-git tree and when nothing is published; G7 skips when there is no workflow directory.

- [#158](https://github.com/MrBinnacle/skills/pull/158) [`ae2bfcb`](https://github.com/MrBinnacle/skills/commit/ae2bfcb8bd163d1f7b6bcdd6501a3d6cf9d00ca6) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The release gate answers whether the repository is fit to release, not only whether one surface is fresh.

  Three checks join the manifest-version lockstep check ([#149](https://github.com/MrBinnacle/skills/issues/149)) as siblings in `scripts/release_gate.py`, each behind a refusal this repository or its sibling actually earned:

  - **G2 - the plan assembles.** Every pending `.changeset/*.md` must name a package the workspace contains, and unreadable frontmatter is refused the same way `changeset version` would refuse it. This is the gate's own unscoped `changeset status`: the scoped `--since=origin/main` form examined an empty set whenever it ran on `main`, which is how a misnamed package kept CI green from 2026-08-24 while blocking every release ([#144](https://github.com/MrBinnacle/skills/issues/144) fixed CI; G2 gives the gate its own verdict).
  - **G3 - nothing left unconsumed at release time**, in the new `--release` mode. Between releases, pending changesets are the process working; at the merge of the version bump they are fatal, because a file left behind means some change silently misses the release it was filed against.
  - **G4 - a dated changelog section for the released version.** The version `package.json` declares must appear under a `CHANGELOG.md` heading that carries a date; a sibling repository tagged a release whose section had never been rolled.

  Failures are listed together, not first-fail: one tree failing all three shows all three in one run. Each check ships a poison control in CI that plants exactly its own fault and requires the message naming it. The argument-less command keeps answering "are the surfaces healthy today", so it still passes while changesets legitimately accumulate between releases.

- [#161](https://github.com/MrBinnacle/skills/pull/161) [`b9817fe`](https://github.com/MrBinnacle/skills/commit/b9817fe0206f2f642e86b924498276d786d1f4fc) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The release gate gains mode-awareness and drops `continue-on-error`, which is the in-repo half of making it a required status check. Release-only checks are false on every ordinary pull request that adds a changeset, which is most of them, so a gate required on all pull requests without mode-awareness would block the process it is meant to protect.

  The gate now distinguishes a release ref from an ordinary one by whether the `package.json` version changed relative to its merge-base with the default branch, and runs the release-only subset solely in release mode. The `--release` flag remains the override a fixture or an explicit run uses; auto-detection is what lets one gate serve both an ordinary PR (which adds a changeset) and a release PR (which bumps the version).

  Two checks join the release-time subset, each blocking rather than reporting because release immutability is enabled on this repository and a spent tag name can never be reused:

  - **G8 - the tag this release would cut is Semantic Versioning normal form.** The tag name is `v` + the `package.json` version, so a version that is not `X.Y.Z` produces a malformed tag. A botched release spends a version number permanently, so the gate refuses a non-normal version BEFORE the tag is cut. ADR 0002 takes the normal form from `v1.2.0` onward.
  - **G9 - the working tree is clean.** A release that ships while the worktree carries uncommitted changes delivers something other than what the version bump commit recorded. Skips a tree with no HEAD commit (a fixture with only `git init`), which keeps the seeded-tree cases single-reason.

  The release-gate job drops `continue-on-error` so a refusal fails the check rather than reporting and continuing, fetches full history and the base branch so the detector can compare against `origin/main`, and ships a poison control that proves an ordinary ref and a release ref receive different check sets by asserting the unconsumed-changesets check runs in one and not the other. Adding the job's status context (`Release gate (fit to release)`) to the `protect-main` ruleset is the remaining half of criterion 7 and is an operator ruleset edit, not a workflow-file edit.

- [#157](https://github.com/MrBinnacle/skills/pull/157) [`334d602`](https://github.com/MrBinnacle/skills/commit/334d6027ec1420cfb126f1198a8decf7dd17a0a3) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The repository can refuse a release for one stated reason, end to end.

  ADR 0002 made the merge of a version-bump pull request the delivery event, and obliged `.claude-plugin/marketplace.json` to carry a `version` on each plugin entry — generated from `package.json`, never typed twice. This ships that mechanism as the tracer bullet ([#149](https://github.com/MrBinnacle/skills/issues/149)):

  - **`scripts/release_gate.py`** — check G1 refuses manifest/package version drift in both directions: an entry declaring a different value than `package.json`, and an entry declaring nothing at all (the state every plugin shipped in before this change — no wrong value anywhere, and still no version). Every failure is listed in one run, and an input the gate cannot read, parse, or trust for shape is a listed failure rather than a skip. `--write` stamps every entry from `package.json`; generation and verification share one read path in the same module so they cannot disagree about what the correct value is.
  - **The manifest** — all three plugin entries now declare `"version": "1.2.0"`, written by running the script's `--write` over the tree. The Claude Code platform resolves a plugin's version from the marketplace entry once present, instead of falling through to the commit SHA.
  - **CI** — `tests.yml` gains a non-blocking `release-gate` job on every pull request: the contract suite, then the gate itself with no arguments (the same command a local run runs), then a poison control that plants one drifted entry into a tree built under `$RUNNER_TEMP` and requires the refusal to name `version drift`, the drifted plugin, and a single stale surface.
  - **`scripts/test_release_gate.py`** — nineteen contract cases driving the shipped script as a subprocess against seeded trees, the live tree, and the workflow wiring itself; every refusal case asserts its own message, not merely a non-zero exit.

  The job stays advisory on purpose for now: ADR 0002 owes a blocking pre-publication gate with the release pipeline, and until that pipeline exists a red verdict here has nothing to stop. When it lands, this job's command becomes its first requirement.

- [#140](https://github.com/MrBinnacle/skills/pull/140) [`46a702d`](https://github.com/MrBinnacle/skills/commit/46a702d344367ee35e8b592b5f96ac18039acf94) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - CI adopts the specification's own validator, and it rejected two published cards on its first run.

  Every conformance instrument in this repository was written by its maintainer, which means every one of them can be wrong in the same direction as the cards it grades. `skills-ref` is the Agent Skills specification's reference implementation. Adopting it is the only check here whose author has no stake in this collection passing.

  **It earned its place immediately, and it refuted the premise it was adopted under.** The ticket recorded that all published cards and all quarantine candidates pass it unchanged, so the adoption would "lock conformance in rather than creating work". Re-measured on 2026-08-24: **17 of 31 cards were rejected.** Two of those are real defects that shipped.

  `click-clirunner-env-none-deletes` and `router-skill-predicate-gap` each carried an unquoted YAML description scalar containing a `: ` or a `{`. Claude Code's own parser tolerates both and the cards work in the product; **a specification-conformant reader cannot load either.** No gate in this repository saw it, because no gate here reads frontmatter at all. Both descriptions are now quoted, with the string values unchanged — 187 and 200 characters, still inside the published 200-character bar.

  **The remaining rejections are declared divergences, named and scoped rather than ignored.** A blanket tolerance would make the gate decorative, so each allowance is a pattern, a tree, and a stated reason, and anything not on the list fails:

  - On the published tree, exactly one allowance: `disable-model-invocation` is not in the specification's frontmatter vocabulary and is a real Claude Code key with load-bearing behaviour — it is what stops a procedure card auto-firing. Dropping it would change how four published cards behave in the product to satisfy a document.
  - On the candidate tree, the allowances promotion already closes: bare `author` / `date` / `version` keys, which `AGENTS.md` step 2a strips, and a description over the specification's 1024-character limit, which step 2a rewrites to 200 — a stricter bar than the specification's.

  **The asymmetry is the decision.** `skills/` is what ships and is held to the specification. `_quarantine/` is a queue whose entry conditions `AGENTS.md` already states. Measured the same day, 11 of 16 candidates fail on those three classes alone, so enforcing the published bar over the queue would have reddened the build on the day it was adopted and stopped the harvest rather than improved it. A candidate failing for **any other** reason — malformed YAML, a missing `name` — still fails, which is the property that keeps a non-conforming card out of the promotion queue.

  Tolerated divergences are printed on every run. A silent allowance is a silent gate.

  **Changeset headers are checked, because one got through.** A changeset naming the package `@mrbinnacle/skills` instead of `mrbinnacle-skills` passed all seven validators and all four CI checks and failed only at `changeset version` — after the merge. `changeset status --since=origin/main` now runs in the pull-request job.

  **Both new gates ship with a poison control, and the second control was caught being vacuous before it landed.** The frontmatter control plants the exact class that rejected two live cards, into a clone under `RUNNER_TEMP`, and requires the gate to catch it _and_ to fail naming `Invalid YAML in frontmatter`. The changeset control was first written to assert only a non-zero exit — and it reddened identically with and without the poison file, because an unrelated "no changesets found" error produces the same exit code. It now asserts the message that distinguishes the two, on a tree that otherwise passes. That is this collection's own `success-test-accepts-any-output` card and the `mutation-killed-by-the-wrong-mechanism` trap, both firing on the same six lines.

  `actions/setup-node` is pinned to a full commit SHA with the version in a trailing comment. CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside a 24-hour window; a floating tag is not a pin.

  **The gate count is now eight, and that is a cost this repository counts.** It is an eighth validator rather than an inline shell step for one reason: a gate that does not answer the roster grep is invisible, which is the defect corrected in the pass immediately before this one. `AGENTS.md` records the roster, the four deliberate specification divergences, and the `GITHUB_TOKEN` the release step has always needed and never stated.

  _Revisit if:_ `skills-ref` adds `disable-model-invocation` to its vocabulary, at which point the published allowance is dead and should be deleted rather than left standing.

- [#43](https://github.com/MrBinnacle/skills/pull/43) [`5c412b0`](https://github.com/MrBinnacle/skills/commit/5c412b07d1b4e4c95fe38a6fa421abcfa300760c) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Publish a versioned admission policy at the repo root, and demote the gate card to reference method.

  Outside contributors were told to "pass the gate" and sent to a skill card that both stated and was the rule — with no edition anyone could cite later. This change separates them:

  - `ADMISSION.md` at the root is the binding rule: the four-question admission test, declared as `admission-policy v1`, with a bump-on-material-change rule. The four questions distill the gate card's first three gates only; topology, statefulness, and shape stay authoring guidance on the card.
  - The gate card's `SKILL.md` opens with a normative-status header: the policy lives in `ADMISSION.md`; the card is the reference method for answering it. Existing citations still resolve; the demotion is visible in the file readers open.
  - A naming convention in the policy file settles the overloaded phrase "the gate" — **admission policy** (this file), **gate card** / `skill-necessity-gate` (the procedure), **screen** (the empirical with/without measurement behind the turned-away rows in `RETIRED.md`).

### Patch Changes

- [#130](https://github.com/MrBinnacle/skills/pull/130) [`f01f692`](https://github.com/MrBinnacle/skills/commit/f01f692bf90dba5423e8241215319a964c1dd44e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Make the brand token file enforceable, and close the two colour gaps it recorded against itself.

  `assets/tokens.json` described the brand and nothing read it. It said so in its own `known_gaps` block, and that block stayed an accurate description of the repository for twelve days: the kit declared structural neutrals for dark surfaces only, both banners carried the sibling instrument's confirmed-success green, and no source file or workflow opened the token file at all.

  **The colour gaps are closed first, because the token check could not land green while they were open.** `assets/banner-dark.svg` drew its receipt seal in `#3fb950` and `assets/banner-light.svg` in `#2da44e` — `harness.prompt`, the measurement instrument's colour, which dressed the inventory as a measurement. Both now draw it in a declared structural neutral. No accent was substituted: replacing a borrowed hex with a newly minted one would close the gap by inventing a token. `color.structural_light` declares the light counterpart of the dark primitive set, so the light banner's `#1f2328` and `#57606a` are declared rather than undeclared-but-shipping.

  **`scripts/validate_brand_kit.py` then runs three checks over the token file**, wired into `tests.yml` on both operating-system cells with a poison control per assertion:

  1. **Banned copy.** Any surface named in `copy.words_to_avoid_surfaces` containing a word from `copy.words_to_avoid` is refused, naming the word and the file. Both lists are data: adding a word is a one-line edit to the token file.
  2. **Hash pairs.** Files that must change together record the sha256 of both halves; either drifting from its recorded hash is refused. No pair is recorded yet — the social preview has no checked-in SVG source, and `asset_pairs.pairs_pending` states why. The checker refuses a token file that records neither a pair nor a reason, so the emptiness cannot go quiet.
  3. **Declared hexes.** Every colour in `assets/*.svg` must be declared as a token value under `color`.

  **The scope boundary is narrower than a naive check would draw it, and it is pinned by its own fixture.** README **body** prose, code comments and working documentation are out of scope. Banned words appear in all three deliberately — `AGENTS.md`, `SECURITY.md` and several skill cards use `load-bearing` in exactly the sense the word is good for. A check that caught those would be wrong, and the fixture asserting they pass is the first case in the suite.

  **Two defects the controls found, recorded because a control that finds nothing proves less than one that finds something:**

  - The first hex scan read every string in the token file, so `color.usage_rules` — the sentence stating that `#3FB950` belongs to the sibling instrument and must not be used here — read as a _declaration_ of that colour. Planting the instrument green back into a banner passed: the ban was its own permission. Only a `value` field on a token object declares a colour now.
  - SVG copy is parsed with `ElementTree` rather than pattern-matched, ported from the sibling instrument's scanner. A regex over `<text>` alone is blind to `aria-label`, and both banners carry their entire public statement in one.

  This DETECTS breaches. `main` has no branch protection and no required checks, so a nonzero exit is a signal, not a gate.

- [#46](https://github.com/MrBinnacle/skills/pull/46) [`f530a8f`](https://github.com/MrBinnacle/skills/commit/f530a8fbcecabba71f2d5146236efd8b527aae6d) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Correct the contributor gauntlet: the four admission questions distill the gate card's first three gates, not all six.

  `CONTRIBUTING.md` step 1 told contributors to answer the admission questions "with the six-gate method". `ADMISSION.md` states that the four questions distill the card's first three gates only — layer triage, recurrence and measured worth — and that the remaining gates cover invocation topology, statefulness and shape, which are authoring guidance for a candidate that has already cleared admission and are explicitly not admission criteria. The shipped wording would have had contributors screen candidates on invocation topology, the boundary the admission policy exists to draw.

- [#78](https://github.com/MrBinnacle/skills/pull/78) [`25db36c`](https://github.com/MrBinnacle/skills/commit/25db36ca40c41d58a5d5032cbc968ddd6e923449) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Replace the front-page origin section with the principal's own recorded lines, and add
  `VERBATIM.md` — the public record every quoted first-person line on a public surface now cites,
  with the date it was said. The commit claim is restated on a reproducible basis: fresh clone at
  `HEAD`, both public repositories only, with the exact command and the measurement date on the
  page.

- [#45](https://github.com/MrBinnacle/skills/pull/45) [`683c07a`](https://github.com/MrBinnacle/skills/commit/683c07a41a192fdd5e07aebb3657f7b1bfdad84a) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Repoint merge-blocking admission citations from the gate card to `ADMISSION.md`.

  Contributor and maintainer gauntlets, both intake templates, the front-page exit/entry pair, and the project delta now cite the admission policy directly. Gate 3 (invocation topology) citations stay on the card. The CONTRIBUTING bar sentence distinguishes the four-question policy from the six-gate method.

- [#109](https://github.com/MrBinnacle/skills/pull/109) [`7e9616c`](https://github.com/MrBinnacle/skills/commit/7e9616ceaf7e8a01be0b9807370ebd22ef9c4cdb) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Replace the banner's live scoreboard counts with the ruled orientation line and retire the
  MB compact mark from the repo identity (owner rulings 2026-08-23, skill-harness [#216](https://github.com/MrBinnacle/skill-harness/issues/216)).

  The banner now reads `These aren't the Claude Code skills you're looking for.` at all five
  validator sites. A static graphic that must track repository state is a maintenance tax, and
  the line's job is orientation, not argument: it tells a visitor what kind of repository this
  is; the repository makes any further case itself. `validate_scoreboard.py` now pins that
  sentence byte-identically (a softened restatement fails) and keeps deriving the inventory
  counts from the cards as a record-conformance check — the counts moved from the graphic to
  the PASS line. The two obsolete poison fixtures were repurposed: `banner-line-drift` proves
  a softened line goes red, `verdict-vocabulary-drift` proves the closed verdict vocabulary is
  still refused. `assets/mark-mb.svg` is deleted: it is the owner's personal mark, and the
  repository is not positioned around its owner. The receipt glyph is the repo's semantic
  mark; no replacement is manufactured.

- [#101](https://github.com/MrBinnacle/skills/pull/101) [`3e90702`](https://github.com/MrBinnacle/skills/commit/3e907021dc25c765334b754cdf17a163acd6e3fb) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - CI refuses a published card that is missing one of the three card contract files.

  `AGENTS.md` states the contract — a card ships `SKILL.md`, `gotchas.md` and `EVIDENCE.md` — and until now nothing checked the first two. `scripts/validate_card_files.py` is the check behind that sentence, run in the `linkcheck` lane on every PR. It reports the bucket-qualified card and the missing filename, not a bare directory name, so the line names a file a maintainer can open. Presence only: what an `EVIDENCE.md` must say row by row stays `validate_conformance.py`'s O4.

  A checker that inspects nothing must not print a pass, so a tree with no cards under `skills/` is refused rather than reported green — the path-bug failure that would otherwise read as conformance.

  Cards are discovered by directory rather than by the `SKILL.md` marker, deliberately wider than `validate_conformance.py`'s glob: a checker that finds cards _by_ `SKILL.md` can never report the one card whose missing file is `SKILL.md`. What the wider walk costs is that every directory two levels under `skills/` gets claimed as published, so the unshipped buckets `AGENTS.md` sanctions for parking work in progress, and dot-directories, are excluded using `validate_scoreboard.py`'s own frozenset rather than a second copy of the rule. Without that, parking a half-built card in `in-progress/` — the repo's own instruction — turned the lane red for three files a card that is not published does not owe, and the run claimed three published cards where the front page states one.

  `scripts/test_validate_card_files.py` runs the real entrypoint against real trees: the committed `card-missing-gotchas` poison fixture, which must fail and must name the card and the file; a tree with zero cards; a tree whose only unfinished work sits in `in-progress/` and a dot-bucket, which must pass and must count neither; and the live nine cards, which must pass. It also asserts the workflow lane still invokes both scripts, since a checker no job runs is a checker that never fails.

- [#116](https://github.com/MrBinnacle/skills/pull/116) [`bb2ddde`](https://github.com/MrBinnacle/skills/commit/bb2ddde2a9e2431e21df40a4468b86739c01aa4d) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Repair `click-clirunner-env-none-deletes`: its references rotted, its behaviour claim did not.

  A link-check job went red on `github.com/pallets/click/blob/8.1.x/src/click/testing.py` with HTTP 429. The 429 was incidental. Querying the repository directly returned `No commit found for the ref 8.1.x` — the branch no longer exists. Click has moved to 8.5, and all three of this card's `8.1.x` URLs were dead, along with its `click/testing.py:534` line pin.

  The behaviour claim survived re-verification. Current stable types the parameter as `Mapping[str, str | None]` on both `CliRunner.invoke` and `CliRunner.isolation`. A value type of `str | None` is the API stating that `None` is a meaningful value rather than an omission, which is the delete; the docs describing `env` as "overrides" is the absent-keys-untouched half. So the card is right and its citations were dead.

  Links repointed to `stable` and verified 200. The line-number pin is removed rather than re-derived: a file offset rots on every release, and the signature is the durable citation. A `gotchas.md` records the occurrence and the general rule — a card asserting library behaviour carries two independent claims, what the library does and where you can see it, and the second rots on the library's schedule rather than yours.

  Recorded explicitly as **not** an instance of `github-linkcheck-404-throttle-false-negative`: that card covers GitHub answering a throttled request with 404 while the link is alive. Here the complaint was a 429 and the link was genuinely dead. The two look identical in a CI log and separate on one check — asking the API whether the target exists.

  A sweep of all 55 external links across the collection found no other dead reference. The remaining non-200 results are placeholders, globs, and a POST-only endpoint.

  Version 1.1.0. Not promoted.

- [#128](https://github.com/MrBinnacle/skills/pull/128) [`5b8f54b`](https://github.com/MrBinnacle/skills/commit/5b8f54b2dea56387c3ad027f1d6d0c7951f12d93) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Every published card now ships a structural eval corpus, and CI refuses a card that does not ([#124](https://github.com/MrBinnacle/skills/issues/124)).

  A card states behavioural claims and records evidence for them. Nothing stated what a run against a card should ASSERT, so there was nothing to run a card against later and nothing that went red when a card's frontmatter `name` drifted from what its evidence refers to. Verified 2026-08-24 at `73a779c`: `git ls-files | grep -i evals` returned nothing.

  Each card now carries exactly one `evals/evals.json`: a `skill_name` equal to the card's live frontmatter `name`, at least three cases, unique integer ids, unique realistic prompts, non-empty expected outputs, and at least two falsifiable assertions per case. Thirty cases across nine cards.

  **These files are contracts, not measurements.** A corpus describes what a run should assert. It records no run, no score and no verdict, and its presence is not evidence of anything about a card's worth. Every card's `Screen result` and `Paired verdict` are unchanged and still `UNMEASURED`; the diff touches no `EVIDENCE.md`. `scripts/validate_eval_corpora.py` never reads or writes an evidence record, because a checker that could touch a verdict is a checker that could manufacture one. Executing a corpus, and anything that would move a verdict, belongs to the measurement instrument and is not in this change.

  The corpus semantics live in a new script rather than in `scripts/validate_skill_formats.py`. That gate has one subject — the closed readable-format vocabulary `SECURITY.md` commits to — and `.json` was already in it, so a corpus is admissible there as-is (confirmed by running the gate: 114 guarded files across 41 skill folders, all declared formats). Widening a security check to carry a second, unrelated meaning is how a security check stops being readable in one sitting.

  Discovery is `validate_card_files.find_cards`, imported rather than restated, so the checker's "N published card(s)" and the card-file gate's are one number. That keeps the fixture trees under `scripts/fixtures/` out of scope: they are inputs to other validators, they sit outside `<root>/skills/`, and requiring a corpus of them would turn every one of them red for a file they do not owe. A tree with zero published cards is refused rather than reported green.

  `scripts/test_validate_eval_corpora.py` runs the real entrypoint against fourteen temporary trees plus the live one. Each rejection tree is a single mutation of one conforming baseline, and each rejection asserts both a substring of its own failure message and a breach count of exactly one — a fixture that is red for two reasons would stay red if the check under test were deleted. Covered: missing corpus, invalid JSON, frontmatter-name mismatch, fewer than three cases, duplicate identifier, duplicate prompt, empty prompt, prompt under the length floor, empty expected output, too few assertions, empty assertion, a second file beside the corpus, and a tree with no cards. Going green is proven by the baseline and by the live tree, whose corpus count is asserted equal to its card count rather than to a number written in the suite.

  The suite, the checker and one poison control — a published card that ships no corpus — run in the existing `tests` workflow on both operating-system cells. No second workflow. Output is ASCII-only, and corpus text is quoted through `ascii()` rather than `repr()`, so a non-ASCII byte inside a corpus is reported rather than raised at a cp1252 console.

- [#117](https://github.com/MrBinnacle/skills/pull/117) [`a0fb755`](https://github.com/MrBinnacle/skills/commit/a0fb755d5f6e3db69e77f7039f2bb50937fd407c) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Close the dangling repository-path references three candidate cards carried, and stop the repair rule from widening the frontmatter spread it exists to close.

  An audit of every intra-repository file reference found seven that resolve to nothing. **No gate catches these.** The link job checks HTTP URLs only, so a card can cite a repository path that does not exist and every check stays green — the same enforcement gap as frontmatter, on a different surface.

  **`skill-family-curation` could not be executed from this repository.** Its procedure told the reader to append family-candidate hints to `_quarantine/_family-candidates.md`, and its Verification section asserted that file is append-only. That file is not in the collection and was deliberately never imported, because its contents are specific to one private skill library. A published card whose central step points at a file the reader does not have is not a card the reader can run. Both passages now describe a registry the adopter keeps in their own library, and state plainly that this collection ships none. `success-test-accepts-any-output` carried the same path in a family-candidate footnote, now stated without it.

  **Three citations in two cards pointed at another project's SOP document as though it lived here.** One of the three already named the owning repository; the other two did not, so a reader parsed them as local paths. All three now say the document belongs to a separate project. The path remains in the text because it is evidence of what was cited, and a naive checker will still flag it — an automated version of this audit would need to distinguish a qualified citation from a bare one.

  **Four references inside `dispositions/2026-08-15-S295-admission-triage.md` are left as they are.** They point at research artifacts in a private repository. "Recording a new occurrence" step 5 states that dated disposition records are snapshots and are not rewritten, and that rule outranks tidiness here.

  **The repair rule added in the same pass is corrected.** It required bumping `version` and `date` on every repaired card. Applied to a card carrying neither, that silently adds keys and widens the candidate frontmatter spread that promotion step 2a exists to close. The rule now bumps those fields only when the card already has them, and says the published tree strips them on promotion regardless — they are a candidate-side convenience, never a requirement.

- [#155](https://github.com/MrBinnacle/skills/pull/155) [`56844c8`](https://github.com/MrBinnacle/skills/commit/56844c86e9e96c538b9662e4bff0de316220a104) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Make the public surfaces state what a release delivers, and what a version promises.

  `CHANGELOG.md` still opened by telling readers that tags and the file were informational — a
  reading aid, not a pin. ADR 0002 made that untrue: a release is a delivery event, and changed
  cards reach installed users when a version is released. The preamble says that now. The README's
  Install section gains the disclosure the narrow declared surface obliges: the install path and
  the card format are what the version promises, and the card set is not, so admitting or retiring
  a card is a minor change. Neither disclosed surface states a count of cards; a tally there
  would be the same maintenance tax the page's counts were retired for.

- [#129](https://github.com/MrBinnacle/skills/pull/129) [`0e3df93`](https://github.com/MrBinnacle/skills/commit/0e3df9370b856d9eb54208d001f055d4969350bc) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Every published card now carries a `Dispatches recorded` row — measured demand beside the recurrence evidence, in a row of its own ([#106](https://github.com/MrBinnacle/skills/issues/106)).

  The original proposal wrote dispatch counts into the `Occasions counted` row; that is settled against in the repository's first architecture decision record (a dispatch count is fan-out, the specific inflation the admission policy's recurrence criterion refuses). The new row states the lifetime platform-counter figure with its measurement date and its semantics beside the number: demand evidence only — slash and model Skill invocations, summed lifetime, not deduplicated by working occasion, blind to hook-injected and always-loaded firings — never recurrence, lift, or worth. The two trap cards read "No recorded dispatch", never "unused": they enforce through hook mechanisms the counter cannot see. Figures were re-derived from the live counter at build time, not copied from the ticket, whose figures were eight days stale. Summed-lifetime was chosen over per-session dedup because the counter predates the per-session delta log, so a lifetime dedup figure is not derivable; the reason is recorded beside each row.

  The card-contract checker now requires the row on every published card and checks its form — an integer or the exact phrase "No recorded dispatch" at the opening, and a measurement date present — each with its own failing control. Every card's `Occasions counted` row is byte-identical before and after, verified by an additive-only diff.

- [#15](https://github.com/MrBinnacle/skills/pull/15) [`e429d83`](https://github.com/MrBinnacle/skills/commit/e429d8335303f4f33a4dce65a04a013267ea5352) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Fold the doctrine that has evolved in the maintainer's live operating rules back into the
  published `CLAUDE.md`, and fix a companion list that had gone stale.

  The published file was written self-contained at v1.0 and has not moved since, while the live
  file it came from kept changing. This ports what actually changed, rather than replacing the
  file — the published version holds expanded prose the live one has since compressed behind
  pointers to a private reference, and a straight copy would have lost it.

  What is new:

  - **§0** — a project delta may pin a standing model for its sessions; when it does, the delta
    wins over the frontier-vs-fast heuristic. `im-up` and `im-down` are named as one
    implementation of the state load and the state write.
  - **§0.6** — the per-project fluency profile: a delta can declare which domains the user owns
    and which the agent researches and recommends in, which is what makes the
    is-this-really-a-values-decision test cheap to apply. The values-decision marker is now named
    (`[values decision]`) rather than described.
  - **§0.7** — the full twenty-role roster, inline. It was truncated to ten roles and an "and so
    on", which is not a roster anyone can work from.
  - **§1.5** — three authoring conventions that were missing: a visible description is a standing
    cost paid every session whether the skill fires or not, so budget the collection rather than
    each description alone; frame a skill around what must be true before an action rather than a
    fixed script, with discipline skills as the stated exception; and structure a long directive
    skill as problem / supporting information / steps, tuning loudness before adding rules.
  - **§11** — `im-down` named as the write side of the checkpoint, `im-up` as the read side.
  - **§14 (new)** — keep a quick-reference of the skills you have to remember on purpose,
    organized by the moment you reach for them, listing only what the reader can actually run.
    Skills that fire on an error are excluded: the failure surfaces them.

  What was deliberately not ported:

  - The `/loop` loop-survival detail. `AGENTS.md` already carries it, better adapted to this repo.
  - The maintainer's private skill roster. Naming skills a reader cannot install is the dead-pointer
    failure this collection fixed in its evidence records last release; §14 states the rule instead.
  - The session-close carve-out from the private conventions, which exempts a close ritual from
    `disable-model-invocation`. This collection ships `im-down` with it set, so publishing the
    carve-out as doctrine would contradict what is in the box.

  The companion list named seven skills; nine ship. `im-down` and `im-up` were missing, and
  `closure-mode-at-boundaries` was filed under error-triggered traps when it is a human-invoked
  procedure. The list is now grouped by when you would reach for a skill instead of by bucket.

- [#90](https://github.com/MrBinnacle/skills/pull/90) [`0244231`](https://github.com/MrBinnacle/skills/commit/02442318d469fb962728e25351b27aea203bf91f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The skill-format gate no longer rejects files git ignores.

  `scripts/validate_skill_formats.py` walked the working tree and judged everything in it, so a maintainer who ran `im-up`'s test suite — which its own `SKILL.md` tells them to run — got six rejections on `.pytest_cache/` files that `.gitignore` excludes and that CI has never seen. CI was green and stayed green, because a fresh checkout has no ignored files. The only person the gate ever shouted at was the only person who could act on it, about something that was never a violation, which is how a reader learns to route around a whole family of checks.

  The gate now asks git, via one `git check-ignore` call for the whole file list. That is deliberately not `git ls-files`: an untracked file no rule ignores — a `payload.sh` dropped in five minutes ago — is still judged, and a tracked file is judged even if a pattern matches it. A tree that is not a git work tree (a reader's install directory, a released tarball) is judged in full, and the status line now says which mode the run was in rather than leaving it to be inferred.

  Five suite cases cover it: an ignored undeclared format passes, the same file tracked still fails, an untracked unignored file still fails, a non-git tree is judged in full, and a non-git run says nothing was skipped. The existing poison controls still fail for their own reasons.

- [#104](https://github.com/MrBinnacle/skills/pull/104) [`4b698ef`](https://github.com/MrBinnacle/skills/commit/4b698ef96dd85d916906615215a3aee214137d98) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The front page leads with the admission method, and a check holds its per-card census to the
  cards.

  A visitor now reads three things before anything else: what governs membership (`ADMISSION.md`,
  with its three-instrument table — policy / gate card / screen — cited rather than restated), a
  card map by type, and a per-card table stating each card's evidence posture and its counted
  occasions. The 2026-08-15 S295 disposition record is linked at the top, where a reader can see
  the triage's verdicts: two cards stand, six carry thin recurrence records, one is ceiling-likely.
  `ADMISSION.md` is unchanged.

  `scripts/test_readme_admission_lead.py` is the check behind that table. It runs in the
  `validator` job on every pull request — a table nothing checks is a table that drifts, and this
  one restates nine cards' records on the page furthest from them.

  The census is **derived through the existing validators, not restated**:
  `validate_scoreboard.evidence_fields` parses the rows, its closed verdict vocabulary decides
  `measured`, `validate_card_files.COUNT_RE` reads the occasions integer, and
  `validate_scoreboard.iter_skill_dirs` decides which cards are published. The first draft of this
  suite carried its own parser and its own open "anything that is not UNMEASURED" test, and all
  four rules disagreed with the validators on real trees: an `UNMEASURED` field that merely
  mentions `SKILL.md` read as a measured result, a `KEEP` verdict written without a trailing period
  read as no result, fenced example rows became a card's values, and parking unshipped work in
  `in-progress/` — which `AGENTS.md` sanctions — demanded a front-page row for a card that was
  never admitted. Two of those four errors put a measurement on the page that never happened, which
  is the direction that flatters it.

  Two claims elsewhere were left contradicting the new table and are corrected here rather than
  left standing:

  - `README.md`'s controlled-results bullet still said every controlled field reads `UNMEASURED`.
    That went false on 2026-07-21, when `git-pull-rebase-trap`'s screen returned `CANT_TELL_YET`.
    The bullet now states the one screen that ran and the eight cards that read `UNMEASURED`, which
    is what the banner's `1 measured` has said since the record was corrected. An identical
    universal claim was removed from a neighbouring paragraph in [#42](https://github.com/MrBinnacle/skills/issues/42) and this site was missed.
  - `BRAND.md` quoted "the README's own words" for a sentence this restructure deletes. The quote
    now points at a sentence the page still carries. `BRAND.md` states that the shipped files
    outrank it, so it follows the front page rather than pinning it.

- [#17](https://github.com/MrBinnacle/skills/pull/17) [`2e3575f`](https://github.com/MrBinnacle/skills/commit/2e3575fe0d8527c66a652420e322438fcd203632) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Rewrite the front page from scratch, and drop the slogan from the artwork with it.

  The previous README opened with a tagline ("skills that have to earn their keep — with the
  receipts to prove it") that also sat inside both banner SVGs, so the page was doing its
  positioning with a slogan rather than with what the collection has actually found. The new page
  is written from the sources instead:

  - Opens with the question the collection came from, in the first person, with no tagline.
  - Puts findings before features. The first substantive section says plainly that every one of
    the nine evidence records reads `UNMEASURED` on both controlled fields, that the admission
    screen turned away four of four candidates in July 2026, and that one shipped skill has
    already retired against its own pre-registered trigger.
  - Removes the duplication. Every skill used to be described twice — once under a failure-mode
    heading and again in the reference section. The reference entries stay, keeping the three
    beats each (when it fires, what it does step by step, what you hold when it finishes); the
    failure-mode material is now a short passage on where the nine came from.
  - Corrects the hand-invoked explanation. The page said the four hand-invoked skills are marked
    that way because "each one decides something you should stay in charge of," which states a
    preference as a rule and contradicts `skill-necessity-gate` at Gate 3. It now says what the
    frontmatter flag does, names the shipped default and the trade behind it, and tells the
    reader it is one line to delete.
  - Corrects how `CLAUDE.md` is described. It is a template to copy, not documentation of the
    doctrine this repo runs on.
  - Adds a "what this isn't" section and a reciprocal pointer to the harness repo.

  Both banner SVGs lose the slogan and carry the collection's actual counts instead: 9 kept, 1
  retired, 4 turned away at the gate. `RETIRED.md` and the pull request template still contain the
  phrase and are left for a separate cleanup.

- [#110](https://github.com/MrBinnacle/skills/pull/110) [`8bbe50b`](https://github.com/MrBinnacle/skills/commit/8bbe50b0dd74fbd61a5bcd7133a4aece53afbd79) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The front page is replaced with the owner's greenfield draft, and the checked structure is
  carried across rather than dropped.

  The page now reads: banner, the ruled line, a two-sentence statement of what the collection is,
  then the checked admission lead (admission method, card map, per-card evidence census), then the
  owner's account — where the cards came from, the four problem areas they address, the provenance
  and evidence vocabularies, how a skill leaves, what the collection is not, the evaluation work,
  and why a skill score is not a skill effect. It drops from 28,584 bytes to 11,221.

  Four checks constrain the front page, and all four still hold. `scripts/validate_scoreboard.py`
  requires the ruled banner line inside the `<img alt>` and requires the origin tiering — 6
  `OBSERVED`, 2 `DESIGNED`, 1 `DISTILLED` — stated on a single line in two sections; the draft
  carried the tiering as a three-item bullet list, which matches on neither line, so it is restated
  as one line in "Where these came from" and once more under "Provenance".
  `scripts/test_readme_admission_lead.py` requires admission method, card map, and card evidence to
  be the first three `##` sections and requires the per-card table to project each card's own
  `EVIDENCE.md`; those three sections are copied from the previous page unchanged rather than
  rewritten, so no new prose enters the page in the owner's voice.

  The draft linked `docs/why-skill-scores-mislead.md`, which does not exist in this repository. The
  link now points at
  [`why-naive-skill-benchmarks-mislead.md`](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md)
  in `skill-harness`, which is the target the previous page used for the same claim. `RETIRED.md`
  is named in the draft without a path and is now a link.

  `BRAND.md` quoted the front page's own words for a sentence this rewrite deletes — _"It is not
  proof that these nine work."_ It now quotes _"Publication is not validation."_, which the page
  still carries. `BRAND.md` states that the shipped files outrank it, so it follows the front page
  rather than pinning it.

  **What this rewrite removes, stated plainly because a reader loses it.** The page no longer
  carries the install instructions (`npx skills add MrBinnacle/skills` and the by-hand `git clone`
  recipe), the "Is it safe to install these?" section, the nine per-card descriptions, the
  contributing summary, the author attribution, or the licence line. Issue [#64](https://github.com/MrBinnacle/skills/issues/64) user stories 18 and
  19 protect the install instructions, the safety section, and the per-card descriptions. The draft
  does not contain them and they were not re-added, because adding them back would widen the draft
  the owner wrote. Restoring any of them is a one-commit follow-up.

- [#117](https://github.com/MrBinnacle/skills/pull/117) [`a0fb755`](https://github.com/MrBinnacle/skills/commit/a0fb755d5f6e3db69e77f7039f2bb50937fd407c) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record three guard prose false-positives from a single rotation pass on `pretooluse-bash-guard-prose-false-positive`.

  The card gains a `gotchas.md`. All three reproductions happened on 2026-08-23, across two different guards, and none was a defect in the guarded behaviour.

  A corpus-search guard refuses a bare `find` over a symlinked skills tree, because an unfollowed symlink silently undercounts it. It blocked a `gh pr create` whose heredoc body was English prose containing that verb in an ordinary sentence. No filesystem search was being run. The guard scans the whole command string, the heredoc body is part of that string, and a common English word is its trigger token. A rebase guard fired twice the previous session on the same principle, once on a verification `grep` whose argument named the trap and once on a commit message whose body explained it.

  The pattern is worth naming: writing about a trap is how you trip its guard. The commit message, the pull-request body, and the card documenting a failure mode are the artifacts most likely to name that failure mode, and a substring match cannot distinguish them from an attempt to commit the failure. A collection whose product is trap documentation will hit this more than most projects, and the cost lands on whoever is doing the recording.

  The disposition is to keep the block rather than loosen the predicate. A false positive costs one reword; a false negative costs the incident the guard exists to prevent. What makes the trade tolerable is that the block message names the token that matched, which all three did, so each reword took seconds. The narrower fix — anchoring the predicate to command position so a token inside a quoted heredoc body cannot match — is a change to the hook rather than to the card, and is not made here.

  Version 1.1.0. Not promoted.

- [#162](https://github.com/MrBinnacle/skills/pull/162) [`fae796f`](https://github.com/MrBinnacle/skills/commit/fae796f72e2526eaa15f3f5d33f2fa105fab9b8e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record the fifth counted occasion on `pretooluse-bash-guard-prose-false-positive`: three
  guard blocks in one session (2026-08-24), on three different guards, all fired by prose —
  two commit bodies and a JSON payload. The gotchas entry states its limit plainly: the
  session's close packet preserved the prose classes but not the predicate names, so the
  occasions are counted without rule attribution. EVIDENCE.md's occasion count and
  screen-result row move from four incidents to five.

- [#117](https://github.com/MrBinnacle/skills/pull/117) [`a0fb755`](https://github.com/MrBinnacle/skills/commit/a0fb755d5f6e3db69e77f7039f2bb50937fd407c) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record the first multi-project harvest, its one corroboration, and the void first run that made the second one necessary.

  The rotation pass is a harvest first, and its evidence base is every project the maintainer works rather than this repository. No pass had swept that corpus. This one searched 1358 files across 28 project directories for the origin failure of each `RECURRENCE-THIN` card.

  **The first run of that sweep was void, and the correction is the more useful finding.** It scanned 614 files and reported a confident zero for `github-pages-deploy-verification`. A positive control run afterwards showed that card's signature could not locate its own documented origin incident — 0 of 4 patterns matched the gotchas entry describing it. An empty result from a signature that cannot find the occurrence we know happened is uninterpretable, not a finding. The file glob was also missing `docs/**` recursively, so the corpus was 45 percent short. Every card's signature is now required to match its own origin before its result counts, and all five pass.

  **One corroboration, and it does not move a count.** `downstream-instruction-framing` refuses an ALWAYS-framed decision-rights header in a handoff. The sweep located that framing institutionalized in a second, unrelated project: four phase-handoff documents each carrying a `## DECISIONS ALREADY MADE (do not re-litigate)` section, plus a planning boilerplate that templates it. Dated 2026-04-29 (three of them, one drafting pass), 2026-05-02, and 2026-06-02 for the boilerplate.

  All of them predate the card's 2026-06-07 origin, so none is counted. Recurrence means the failure happened again after the discipline existed, which is what `Occasions counted` answers. The card stays `RECURRENCE-THIN` at one. They are recorded because they establish what the origin entry alone does not: the incident was the moment a standing practice got caught rather than a single lapse, and a boilerplate had been emitting the refused framing for five weeks before anyone named the rule.

  The sweep also found the discipline visibly applied, which is the more useful signal for a retention question. An audit synthesis heads its inherited-decisions section `do not re-litigate; surface a fork if you must` — the card's prescribed form, granting the fork the card exists to protect.

  **An open policy question is surfaced rather than decided.** Neither `ADMISSION.md` nor `AGENTS.md` says whether pre-origin corroboration belongs in `Occasions counted`. Under the reading applied here it does not and the label stands; under the other reading the count moves to two and the label drops. The maintainer owns the choice, and the dated evidence is preserved for either.

  **The negative results are part of the deliverable, now that they are interpretable.** `github-pages-deploy-verification`: zero occurrences outside the collection. `closure-mode-at-boundaries`: one external hit, an archive referencing the card. `git-pull-rebase-trap`: 34 external hits, every one the card, its guard, its fixtures, research about it, a deliberate end-to-end demonstration, or a project convention warning against it — adoption rather than occurrence, consistent with the insurance diagnosis. `im-up`: only the skipped-close already counted on `im-down`, and counting it twice would be the fan-out criterion 2 refuses.

  Before this sweep those diagnoses rested on nothing having changed recently, which is a freshness check rather than a search. They now rest on a search with a passing control.

- [#82](https://github.com/MrBinnacle/skills/pull/82) [`4985c2a`](https://github.com/MrBinnacle/skills/commit/4985c2ad3532bfa806057bef1d7c6bc95706da31) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Swap the front-page inventory line to what the repository can support: `9 admitted / 0 measured /
1 retired / 4 solutions looking for a problem`. `kept` asserted a retention decision that survived
  an evaluation, and no evaluation has happened — so the page that refuses to state numbers its
  evidence will not carry was carrying one.

  `0 measured` is a new derived field. `scripts/validate_scoreboard.py` reads it from each card's
  own `EVIDENCE.md` controlled fields rather than hard-coding a zero, so it goes red the day a card
  is first screened instead of quietly staying wrong. A card with no record, or with a controlled
  field missing, is refused rather than counted as unmeasured. A third poison control proves the
  field can fail.

- [#163](https://github.com/MrBinnacle/skills/pull/163) [`a4dc3ad`](https://github.com/MrBinnacle/skills/commit/a4dc3ad267b11f1649c068e10479355ce2d22333) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Make the maintainer instructions state the delivery-event model rather than the old "tag by hand if wanted".

  AGENTS.md step 4 still described the pre-ADR-0002 model: "tag by hand if wanted", which treats the tag as optional decoration. Under ADR 0002 the merge of the version-bump pull request is the delivery event, not a tag push. The procedure now names the maintainer as who performs the delivering merge, names `python scripts/release_gate.py --write` as the command that stamps plugin versions and reports release fitness (listing every stale surface in one run rather than failing at the first), states that release immutability is enabled and a tag name cannot be reused once spent, and retains the GITHUB_TOKEN prerequisite. `.changeset/README.md` carried the same pre-ADR model ("tag it by hand if you want a tag", "reading aid, not a pin") and now points at the procedure. Pinned by scripts/test_release_model_disclosure.py.

- [#120](https://github.com/MrBinnacle/skills/pull/120) [`94d0890`](https://github.com/MrBinnacle/skills/commit/94d089002ff299a6d0e139d83e2b62f8a366439e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Harvest pass S313: two candidates gain their first independent occurrence; one candidate's dated claims re-verified against current vendor docs.

  A repaired sweep instrument (control floor, fenced-block signature extraction, mechanical
  origin-lineage tagging) re-swept all 22 quarantine candidates and 3 published cards over the
  full 5,048-file corpus: 25 of 25 positive controls PASS with zero dead patterns, and 309
  independent symptom-class hits were read and classified. Two survived as occasions, both
  verified at source: `halt-as-deliverable` gains a 2026-08-16 micro-HALT in a second personal
  project (a stale planning claim empirically re-tested, found false, correction surfaced with
  the record kept), recorded in a new `gotchas.md`; `pretooluse-bash-guard-prose-false-positive`
  gains a third-project, third-guard-family failed-closed block on a legitimate heredoc (recovery
  was this card's own `--body-file` remedy), appended with its hedges stated. The remaining 19
  candidates gained zero occurrences from a sound instrument; their dated deferrals continue with
  a defensible zero behind them. `anthropic-sdk-via-openrouter`'s 2026-06-09 verification note is
  re-dated after corroboration against current OpenRouter docs, and its frozen example model ids
  are marked dated-and-illustrative. No EVIDENCE.md was authored and no verdict vocabulary was
  manufactured; admission standing is unchanged for every candidate.

- [#139](https://github.com/MrBinnacle/skills/pull/139) [`4396e54`](https://github.com/MrBinnacle/skills/commit/4396e54b76321460ec6b2101b8283c28f85ce72e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `O7` no longer crashes on a manifest of the wrong shape, and its absent-manifest case is no longer vacuous.

  An independent cross-family review of the change that shipped `O7` found five defects. All five are fixed here, and the two that mattered were reproduced before being fixed rather than taken on the reviewer's word.

  **A manifest that is valid JSON of the wrong shape aborted the whole report.** `data.get("plugins", [])` assumes the top level is an object. `[]`, `null`, `123` and `{"plugins": ["x"]}` all parse, so the JSON handler never saw them; each raised `AttributeError` out of the check, past both handlers, and took `O1` through `O6` down with it before a single obligation rendered — while the obligation's own text promised `FAIL`. Reproduced on all four shapes, then guarded: shape violations now raise a `ManifestShapeError` that subclasses `ValueError`, so they land in the existing unreadable-manifest handler and report `FAIL` like any other. Six shapes are now fixtures, and each asserts twice: that `O7` is `FAIL`, **and that the other obligations still rendered**.

  **The absent-manifest case could not tell its own branch from a different one.** Deleting the `is not a file` branch entirely left a `FileNotFoundError` that the `OSError` handler converted into the same `FAIL` verdict — so the case passed with the branch it exists to pin removed. Reproduced by mutation: the full suite exited 0 with the branch gone. The case now asserts on the message, and the same mutation fails it by name. The reviewer mutation-tested the other four breach branches and all four were killed by name; only this one survived, which is why it is the one worth recording. **A verdict-only assertion cannot distinguish two code paths that return the same verdict** — that is this collection's own `success-test-accepts-any-output` card, one level up.

  **Three smaller ones.** `CANNOT-CHECK` on an empty published tree contradicted the rule that `CANNOT-CHECK` is reserved for `O5` alone, and it discarded already-computed breaches; an empty tree is now `FAIL`, because a manifest compared against no cards has checked nothing. Path spelling — `././skills/x`, or a backslash separator — resolved on disk but failed a raw `startswith`, so a legitimately published card could be reported under the most alarming label this check emits, "named but not published"; separators and `.` segments are now folded before any prefix test, and `..` is refused. And a `SKILL.md` under `skills/` at any depth other than `skills/<bucket>/<card>` resolved, passed the leading-segment test, contributed a phantom name, and was validated by neither direction — the exact hole the two-direction design exists to refuse. The depth is now checked against the same depth `find_cards()` globs.

  Every one of these is the same shape as the defect `O7` was written to catch: a check that looks complete because it names two directions, while a third state has no name at all.

  _Revisit if:_ the plugin manifest format gains a nested or non-list `skills` form, at which point the shape guard is stating a contract the loader no longer holds.

- [#103](https://github.com/MrBinnacle/skills/pull/103) [`772c350`](https://github.com/MrBinnacle/skills/commit/772c350f6c00b73671e41d08e5aa9616a24e2e18) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The recurrence rows are contract, and CI refuses a card that does not state them.

  Every published card's `EVIDENCE.md` now carries `Occasions counted` — an integer plus the dated references behind it — alongside the `Re-screen trigger` row it already had, and `scripts/validate_card_files.py` refuses a published card missing either. The row answers `ADMISSION.md` criterion 2 in the card's own file: the S295 admission triage found that the systemic gap was never a shortage of incidents but that recurrence is recorded once and never counted.

  The row cannot certify itself. The opening integer must equal the number of dated references in the row, and every one of those dates must appear elsewhere in the card's own files — the row is cut out of the haystack before the search. A count checked only against the dates sitting beside it would pass any number a card cared to write next to any dates it cared to invent.

  Where that stops short, stated rather than implied: the haystack is every `*.md` in the card, `EVIDENCE.md` included, so a sibling row of the same record corroborates the count — and two cards rest on that, `parallel-review-disposition-schema`'s 2026-07-10 and `subagent-research-reliability`'s 2026-07-12, which are recorded in `Validated against` and `Observed in use` rather than in a gotchas entry or a case study. Those are also the two cards whose count carries them past the thin threshold. Narrowing the search to the card's other files is a recount, not a refactor, so it is left to the holder of the records. For the same reason dates are not de-duplicated: two occasions can honestly fall on one day, so collapsing repeats would refuse a true count, but a repeated date does satisfy the arithmetic.

  Seven cards state `RECURRENCE-THIN` in their own record, and the checker requires the label below two counted occasions and refuses it at or above two, in both directions: an absent label overstates what the evidence is worth, and a stale one understates a card that earned its way out. `parallel-review-disposition-schema` (2 counted) and `subagent-research-reliability` (4) carry no label. `git-pull-rebase-trap` carries the label and keeps the triage's own `CEILING-LIKELY` verdict beside it — that verdict is the measurement axis and does not dispute the count.

  `AGENTS.md` states how a new occurrence is recorded — dated entry first, then the count — so recurrence accrues without a special counting session, and states that dated disposition records are snapshots rather than files to be rewritten later.

  The row checks live in `validate_card_files.py`, not in `validate_conformance.py`'s O4, and the earlier note saying otherwise is corrected in place. O4's subject is the CONTROLLED fields the front-page scoreboard is derived from, under `conformance v1`, whose own bump rule makes a material change to what counts as meeting an obligation a version bump — with a pre-registered payload for the first one. These rows are the admission contract, not the scoreboard's. The row table itself is parsed by `validate_scoreboard.evidence_fields`, imported rather than restated, so the fenced-block and first-occurrence-wins rules are not implemented twice with different answers.

  `scripts/test_validate_card_files.py` runs the real entrypoint against real trees: a committed `card-missing-evidence-row` fixture that ships all three files and states one row too few — the case that would silently stop being checked if the checker only looked at file presence — plus an inflated count, a count written as prose, a dated reference nothing corroborates, a missing label and a stale label. Going green is proven as well as going red: by the conforming baseline every one of those trees is a mutation of, and by the stale-label and prose-count cases, which re-run the same tree after correcting it. The committed `card-missing-gotchas` fixture now states both rows, so it stays red for exactly one reason, and both fixtures assert that breach count.

- [#121](https://github.com/MrBinnacle/skills/pull/121) [`bbb5cad`](https://github.com/MrBinnacle/skills/commit/bbb5cad38de8867a0e5bbe1b0b56ec2989e4e451) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `CONTEXT.md` separates two quantities that had been sharing one word, and the first ADR records why.

  An **occasion** is one independent occurrence of the failure a card addresses. A **dispatch** is one invocation of a card. `EVIDENCE.md`'s `Occasions counted` row answers `ADMISSION.md` criterion 2 and means the first; a proposal to write measured platform dispatch counters into that same row meant the second.

  Criterion 2 decides it in its own words: occasions are _"counted, not predicted, and not inflated by fan-out from a single run."_ A dispatch count is fan-out — 88 recorded dispatches of one card are 88 runs over some smaller, unknown number of independent failures. Writing them into the recurrence row is the specific inflation the criterion exists to refuse, not a near-miss against it.

  `scripts/validate_card_files.py` already refuses the change on mechanical grounds, since the row's integer must equal the count of dated references cited in that row and `im-up` cites one. That is the symptom. The reason is the criterion, and the reason is what the ADR records, because the mechanical block could be argued away by widening the checker and the criterion cannot.

  No validator, card or public count changes here. This is vocabulary and a recorded decision: the dispatch measurement is good data and gets a row of its own rather than the recurrence row, and `docs/adr/` exists from now on for decisions that are hard to reverse and would otherwise be re-proposed.

- [#108](https://github.com/MrBinnacle/skills/pull/108) [`2c26820`](https://github.com/MrBinnacle/skills/commit/2c2682074ccb8800f3f368ebc1e172e0dbce142b) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Fold the consolidation-ID-hygiene finding into `parallel-review-disposition-schema` as an OBSERVED gotcha.

  The S305 quarantine Gate-0 run (2026-08-17) routed the private candidate card `fix-brief-consolidation-id-hygiene` here as a layer finding: its content is a consolidation-layer discipline for the output contract this card already owns, not a standalone skill. The appended gotcha records the observed incident — two parallel reviewers' local M1–M5 numbering collided at consolidation, one reviewer's M3 was silently dropped under a kept same-numbered finding, and the dropped bug persisted across 4 commits — plus the three mitigation options (source-prefixed IDs, a rollup table, or per-seat subsections) and the falsifying count check that detects a silent drop. The card's `Occasions counted` row is unchanged: the incident is the folded card's evidence, not a recurrence of this card's own failure mode.

- [#44](https://github.com/MrBinnacle/skills/pull/44) [`4460228`](https://github.com/MrBinnacle/skills/commit/44602281308fd586e0a098b8916eecb03e6b517f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Remove a predictive alternative that had been added to the first admission question.

  `ADMISSION.md` question 1 shipped as "still fails **(or should plausibly still fail)** the job the skill claims to fix". The parenthetical was not part of the settled question and changes what the policy admits: "fails" is an observation, "should plausibly fail" is a prediction, so the disjunct allowed admission with no unaided run ever performed.

  It also contradicted two things already in the repository:

  - the gate card's Gate 1, which says "**Don't predict — measure**" and "Count occasions, not artifacts", and Gate 2, which says "Measure, don't argue" and asks for a with-skill vs without-skill run;
  - question 2 of this same policy file, which requires occasions be "counted, not predicted".

  Question 1 now reads "still fails the job the skill claims to fix. Observed, not predicted: run it unaided first."

  The declared version stays `admission-policy v1`. This is errata, not an amendment: the four questions as specified never contained the disjunct, and no machine-readable consumer of the policy exists yet, so no digest of the defective text is in circulation. Questions 2, 3 and 4 were re-checked against Gates 0-2 and are faithful.

- [#18](https://github.com/MrBinnacle/skills/pull/18) [`1038ea4`](https://github.com/MrBinnacle/skills/commit/1038ea4f5923b51b6fee6365cd9faedfa587785a) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Take the skill names out of the CLAUDE.md template, and finish dropping the slogan.

  The published `CLAUDE.md` is a template adopters copy wholesale into their own
  `~/.claude/CLAUDE.md`. Its §14 tells them: "list only what the reader can actually run —
  naming a skill they don't have costs them context and teaches them to distrust the rest of
  the list." The file then broke that rule five times in its own numbered sections, naming six
  skills from this collection inside rules the adopter is meant to run, each hedged "(in this
  repo)". Copy the file without installing the collection and five of your operating rules
  point at things that don't exist.

  - §0 and §11 named `im-up` / `im-down` while describing the session load and the checkpoint
    write. The rule that actually matters there is that the two are one mechanism in two
    halves, so the sections now say that instead.
  - §1 named `skill-necessity-gate`. It now states the test itself: settle whether something
    should be a skill at all before authoring one, because a skill that fails that question
    still taxes context every session.
  - §4 named `downstream-instruction-framing`, `parallel-review-disposition-schema` and
    `subagent-research-reliability` in three bullets that existed largely to point at them.
    Each bullet now carries its own discipline directly — no blanket "don't re-litigate"
    framing, fix a shared output schema before parallel verifiers run, confirm a research
    subagent's tool grant includes web tools before dispatch because one without them answers
    from memory and reads identically.

  Nothing is lost for a reader who does have the collection: all nine skills are still listed
  under **Companion skills in this repo**, below the horizontal rule, where a heading scopes
  them. The header now says which part of the file is the template and which two sections are
  this repo's worked examples, so the copy boundary is visible rather than inferred.

  `AGENTS.md` picks up the constraint as a repo convention, so a future edit doesn't quietly
  reintroduce it — and notes that `AGENTS.md` itself is under no such restriction, since it is
  never copied anywhere.

  Also corrected: `CLAUDE.md` and `AGENTS.md` each described the template as "the doctrine this
  repo runs on." It is a template the repo publishes; `AGENTS.md` is what governs work inside
  the repo. The README's half of this was fixed when the front page was rewritten.

  Finally, the three remaining sites of the retired "earn its keep" tagline are gone —
  `RETIRED.md` (twice) and the pull request template — which the front-page rewrite had
  deliberately left for a separate pass. The epigraph in `RETIRED.md` keeps its actual claim:
  a list that shrinks when the models improve is the one telling you the truth about which
  skills the model still needs.

- [#89](https://github.com/MrBinnacle/skills/pull/89) [`5d31e9f`](https://github.com/MrBinnacle/skills/commit/5d31e9f8990e623a70fe0b5527c7cdef45e007ba) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - State the true origin tiering on the front page, and derive it from the cards.

  `README.md` said seven of the nine cards exist because something went wrong, twice. Read on 2026-08-13, the nine `EVIDENCE.md` `Origin` fields say six. The ninth card is not in either bucket the page offered: `skill-necessity-gate`'s record calls it a codified research answer, stated plainly, not a scar. `7 + 2 = 9` closed the arithmetic while mis-describing that card — in the sentence explaining why evidence tiers are kept distinct.

  Both passages now state the measured split, 6 `OBSERVED` / 2 `DESIGNED` / 1 `DISTILLED`, and name the third class rather than folding it into one of the other two. The `DESIGNED` vs `OBSERVED` distinction is unchanged; it was the count and the missing tier that were wrong.

  `scripts/validate_scoreboard.py` now derives that tiering from the cards' own `Origin` fields and asserts both README sites, so adding, retiring or re-tiering a card turns the build red instead of leaving the page quietly stale. The vocabulary is closed — an Origin opening with an unrecognised word is refused, not guessed at — and a new poison-control fixture proves the check can fail for its own reason.

- [#126](https://github.com/MrBinnacle/skills/pull/126) [`187c953`](https://github.com/MrBinnacle/skills/commit/187c953a0fa78a0e13a37ffb2997af025652f1e9) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The session-boundary pair's parity contract now covers every shared file, and a missing sibling is reported as not verified instead of passing ([#123](https://github.com/MrBinnacle/skills/issues/123)).

  The suites' `no-drift` assertion guarded three files while eight were byte-identical across `im-down/` and `im-up/` — the packet-format document and all four fixtures sat outside the tuple, so a change to any of them turned no assertion red. The contract now names all eight, the run prints which files it compared (so a future narrowing is visible in output, not only in source), and a contract file absent from either card counts as drift rather than being skipped. On a single-card install the suite reports `parity NOT VERIFIED` and omits `no-drift` from its pass roster, instead of printing a passed check it never ran. Verified by a mutation matrix: one byte appended to each of the eight files in one card only turns both suites red via the parity message naming that file.

- [#156](https://github.com/MrBinnacle/skills/pull/156) [`872cd87`](https://github.com/MrBinnacle/skills/commit/872cd87c5d19205ecc67f159446dc2feb369d568) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Pin every workflow `uses:` to a full 40-hex commit SHA with a trailing version comment.

  Five of six actions rode mutable tags (`actions/checkout@v4`, `actions/setup-python@v5`,
  `actions/github-script@v7`, `lycheeverse/lychee-action@v2`, `pre-commit/action@v3.0.1`). Only
  `actions/setup-node` was already pinned. Each new SHA was verified via `git ls-remote` to be
  the commit its named tag points at, so the workflows run the same action versions they ran
  before. CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside a
  24-hour window; a floating tag is not a pin. The gate that will refuse a future floating tag
  is tracked separately.

- [#115](https://github.com/MrBinnacle/skills/pull/115) [`ea7988b`](https://github.com/MrBinnacle/skills/commit/ea7988b5272aa16b4c84d01c4e57ad24ea4485bb) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Give the rotation and harvest pass a repair gate and a stated screen routing, and record two occurrences the pass surfaced.

  **`AGENTS.md` — the pass gains the step it was missing, and states the one it deliberately does not take.** As written, the pass went harvest → reconcile → adjudicate, so it could reach an admission or retirement call having repaired nothing. Two steps are inserted, and their order is a constraint rather than a preference: harvest before repair, because the occurrence tells you what to repair; repair before any screen, because a screen measures the text in front of it.

  Step 3, the **repair gate**. Four stated criteria put a card into repair: a harvested occurrence falsified its own procedure or remedy; its `description` does not name a branch the new evidence added; it asserts library, API or platform behaviour on an undated or stale claim, checked through Context7 and marked unverified when the docs cannot confirm it; or its frontmatter drifted. Repair is skill authoring, so the step stacks `writing-for-agents` and names the levers it must apply — the `description` is a context pointer carrying one trigger per branch, each meaning keeps a single source of truth, no-ops get pruned.

  Step 4, **routing the worth question**, records that the measurement harness is _not_ in this loop and why. The binding constraint on this collection is admission criterion 2, recurrence, not measurement. The harness measures with-and-without lift, a different question, and its record is zero production KEEPs across 26 screens because production skills ceiling at a Null-arm pass rate of 1.00; a ceiling converts to `CUT` only for a transformative-lift skill and otherwise reads `CANT_TELL_YET`. Running the mill over cards that will all ceiling costs a great deal and returns nothing the pass can act on. So the default is no screen, a card stays `UNMEASURED` and says so, and only a candidate carrying a frozen empirical contract — a fixture and a counterfixture — is screened. Two qualify today. Existing verdicts are read read-only; checked 2026-08-23, that store answered "No admissible screens in the store", so no published card's label can currently be sourced from it.

  **Step 2 gains a pointer scan, because no gate performs one.** The four validators check file presence, `EVIDENCE.md` rows, the banner line, links and residue. None reads frontmatter. A card's `description` is the only thing deciding whether it is ever reached, so the collection validates its receipts and not its retrieval surface: a card can hold a perfect evidence record, derive correctly into every count, pass all four gates, and be permanently unreachable.

  **Promotion gains step 2a, frontmatter normalization.** Published cards carry `name` + `description`, plus `disable-model-invocation` where the topology rule calls for it. Candidates carry four dialects: measured 2026-08-23, 12 of 22 held `author` / `version` / `date`, 6 held a `metadata: type:` block over an undeclared vocabulary, 4 held neither. Nothing catches a leftover key on promotion, so the step is the whole enforcement.

  **Two candidate cards repaired, both through the new gate.**

  `router-skill-predicate-gap` records a second occurrence. A router rule shipped the previous day stayed silent on a plain-language request. Its pattern list covered "could use" and not "needs" — this card's original failure mode. And `patterns[0]`, the broadest of four, held a literal backspace where a regex word boundary was meant: in JSON, `\b` is the backspace escape and a word boundary needs `\\b`. That pattern compiled cleanly and matched nothing from the day it shipped. The rule had a test suite stricter than this card asks for, one that refuses any rule carrying no asserting fixture, and it certified the inert pattern anyway because its coverage check is per-rule: all three fixtures landed on the narrower patterns. Measured that day, 33 of 72 patterns were reachable by no fixture. The card's Notes claimed a test suite is what catches a predicate gap; that is necessary and not sufficient, and the Notes now say so. Version 1.1.0.

  `success-test-accepts-any-output` gains rule 4 and its first negative-direction occurrence. Rules 1 through 3 all defend a claim that something happened. The mirror claim — nothing happened — has the same defect and no external state to re-read. A probe harness built during this pass invoked a hook filename with underscores where the file uses hyphens, printed nothing for six prompts including two known-good fixtures, and was one step from being recorded as total predicate failure. Rule 4 requires a known-good positive control in any run whose finding is an absence, and names the tell: a clean sweep of negatives indicts the harness before the subject. The card's claim that `gh` writes API error bodies to stdout was re-checked against the published `gh api` manual, which documents `--silent` but does not specify the error stream; the claim is now marked reproduced-once rather than specified. Version 1.1.0.

  Neither card is promoted. Admission stays default-refuse and is the maintainer's call.

- [#125](https://github.com/MrBinnacle/skills/pull/125) [`73a779c`](https://github.com/MrBinnacle/skills/commit/73a779c20d8098e8b65dee901d3d967d8b20536f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The session-boundary producer now refuses a packet made before this session's close commit ([#122](https://github.com/MrBinnacle/skills/issues/122)).

  `validate_close_commit` established that `HEAD` is _a_ close commit, not _this_ session's — a session that committed nothing still sat on the previous close and passed, which is exactly the shape that produces a packet the receiver rejects as stale at the next open. The docstring named its own revisit condition: consult the packet directory for an already-claimed `HEAD`. That condition is now satisfied. A new `validate_unclaimed_head` check walks the configured `packet_dir` newest-first to the first prior packet that parses and records a head, and refuses production when the current `HEAD` equals that recorded `repository.head`, naming both in the message. Walking past unreadable files matters: a stray `README.md` sorts after digit-led timestamp names, so taking the raw filename maximum would let one stray file disable the guard silently and permanently. The existing marker check stays; each refuses a case the other cannot see.

  The check degrades to the previous behaviour when there is nothing to compare against — an empty packet directory, a malformed newest packet, or a manifest without a recorded head — so a fresh clone can still produce its first packet. This limit is real and smaller than the hole it closes, and is stated in the docstring. Both cards move together: `validate_packet.py` and `test_validate_packet.py` are byte-identical across `im-down/` and `im-up/`, enforced by the suites' parity assertion.

- [#131](https://github.com/MrBinnacle/skills/pull/131) [`73aabcf`](https://github.com/MrBinnacle/skills/commit/73aabcf1e9622a56b45f7d6fee9e64631d48fccb) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The rotation-and-harvest procedure now describes the gates that actually run.

  `AGENTS.md` § "The rotation and harvest pass" is written so a cold session can execute the whole pass from this repository. Between 2026-08-23 and 2026-08-24 the repository grew three validators, a third contract row on every published `EVIDENCE.md`, a second direction on the occasions check, and an eight-file parity contract on the session-boundary pair. The procedure recorded none of them. It still said "four validators", still named two contract rows, still listed a five-item gate set, and still described the occasions check in one direction. Nothing in CI reads prose, so all four drifts were invisible and none was self-detected.

  The consequence was specific, not cosmetic. A cold session running the pass as written would have shipped a pull request that CI reds on three gates the procedure never told it to run, and a promotion authored against the procedure would have been missing the `Dispatches recorded` row that `validate_card_files.py` requires.

  Four corrections, each verified against the code rather than against the prose it replaces:

  - **Contract rows: two to three.** `Dispatches recorded` is in `REQUIRED_EVIDENCE_ROWS`. Its checked form is stated — a positive integer or the exact phrase `No recorded dispatch`, plus a `measured <date>` clause — together with why a numeral zero is refused: two cards fire through hook mechanisms the platform counter cannot observe, and a figure the counter cannot see must not be published as "unused". The section now also states plainly that a dispatch is not an occasion.
  - **The occasions check runs in both directions.** "Recording a new occurrence" described only the rule that stops a count rising without a record. It now also states the rule that stops a record sitting uncounted, the term-of-art trigger that scopes it, the `co-occurrences` exclusion, and the instruction to reword a non-occurrence line rather than cite its date to silence the check.
  - **The gate set is a table of all seven validators and all seven suites**, each with the change a pass most often breaks in it, and it carries the command that re-derives the list from the workflow files. The instruction is to run all seven rather than the ones the pass believes it touched, on the same reasoning the reconciliation step already gives for walking the consequence chain. The parity contract is stated with its failure mode: the suite reports parity NOT VERIFIED and still exits 0, so CI greps the roster for `, no-drift` and a reader must do the same.
  - **Step 2's validator count is corrected, and its load-bearing claim is sharpened rather than dropped.** One validator now parses frontmatter, but only the `name` key, and only to catch a corpus whose `skill_name` drifted. No validator reads a card's `description`. The count rising from four to seven is exactly the change that invites a reader to assume the gates have grown to cover retrieval; the text now says they have not.

  Step 7 no longer fixes who presses merge, which is the maintainer's to hold or delegate and was stated as neither. It fixes the gates, which hold either way: CI green, and the PR head SHA matching the branch ref — with the incident that makes the second gate load-bearing, where a PR merged mid-push froze its head while `gh pr checks` reported green for the older SHA. Publication is named as a separate authority that does not move: release tags, published assets, the social preview, the About settings.

  A cross-family review of the above found eight further defects, and they are fixed here rather than deferred. Every one is the same class the change set out to close — prose describing a check the code does not perform:

  - **The re-derivation command could not see three of its own gates.** It was scoped to `scripts/`, and both session-boundary parity suites and the stale-packet poison control live under `skills/engineering/im-{down,up}/`. A session that ran the grep to confirm the roster was complete got a clean confirmation with those three unrun. The command is now `grep -rnE 'python3? +[^ ]*(validate_|test_)' .github/workflows/`, which returns all thirty-four invocations, and the three off-`scripts/` gates are named with the exact commands that run them. The instruction "read the roster line, not the exit status" was unexecutable before, because no roster line had been produced.
  - **Two gate-table cells described checks that do not exist.** `validate_skill_formats.py` was credited with "size limits"; it enforces an extension vocabulary (`.md`, `.txt`, `.py`, `.json`) and a bytecode-source rule, and no size check exists anywhere in it. `validate_voice_provenance.py` was credited with "prose register on edited surfaces"; its scope is quotations inside `BRAND.md` section `## Voice`, so no `SKILL.md` or README edit can red it. Both cells now state what the script does.
  - **The occurrence pattern's exclusion was stated backwards.** The lookbehind `(?<![\w-])` excludes a _preceding_ hyphen only. `co-occurrences` and `re-occurrence` are safe; `occurrence-record (2026-08-24)` trips the check. A writer told that hyphenated compounds are excluded would have been reddened having been told the opposite. Both directions of the check are also now stated to scan `card.rglob("*.md")` and nothing else, so a dated occurrence in a `.py`, `.txt` or `.json` file is invisible to the guard in both directions.
  - **"Pass all four gates" still stood seven lines below its own correction to seven.** Pre-existing, inside the paragraph this change rewrites, which is the drift class the change exists to eliminate.
  - **The unobservable-card branch over-claimed and over-reached.** It said a card's absence from the dispatch log is "not evidence about retrieval OR about worth". The counter does observe the model-invocation path, and a zero there is weak but real evidence the description was never picked; it is blind to the enforcing path only. The claim is now "not dispositive about retrieval". Separately, the branch ordering foreclosed too much: branch 1 disqualifies a card from branch 3 (insurance) only. A hook-fired card has its own retrieval defect — the trap occurred and the hook did not fire — detectable from the session records without the counter, and stopping at branch 1 lost it.
  - **The two cards filed as unobservable are not equally evidenced, and the branch now says so.** `git-pull-rebase-trap` has a dedicated PreToolUse guard with a test beside it. `github-pages-deploy-verification` has no dedicated guard, only a prompt-router nudge — and a nudge is not a hook firing, because a model that acts on a nudge calls the Skill tool, which the counter _would_ see. For that card the absence is equally consistent with the nudge never firing and with it firing and being ignored. The rule added: do not file a card in this branch on a router nudge alone.
  - **One scheduled gate was absent from the procedure entirely.** `conformance-schedule.yml` runs an Outgrown-rotation guard that fails the scheduled run if the published card count exceeds 40 or equals zero. It is a rotation tripwire and belongs in the rotation section. Measured 2026-08-24 the count is 15, so it cannot fire today.

  All seven validators, all seven suites, both parity suites and the poison control were run against this change. Both parity suites print `, no-drift`; the poison control exits non-zero and prints `REJECTED`. The parity and poison commands documented here are the ones that were run, not the ones that were expected to work.

  _Revisit if:_ a validator is added or removed, or a gate is added outside `.github/workflows/`. The table dates itself the moment the roster changes, which is why the command that re-derives it sits beside it — and that command is only as good as its scope, which is the defect this review caught.

- [#16](https://github.com/MrBinnacle/skills/pull/16) [`b07d377`](https://github.com/MrBinnacle/skills/commit/b07d3773c2862c4b0fd273b074f550371522ce99) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Rewrite the README's reference section so each skill says what it actually does.

  Every entry described the problem the skill addresses or the principle behind it, and none
  described the behaviour. "Structured wrap-up at phase boundaries" does not tell a reader
  whether the skill runs tests, prints a list, or refuses to continue — so a visitor could not
  tell what they would get by installing it.

  Each of the nine entries now states three things in order: when it fires, what it does step by
  step, and what the reader is holding when it finishes. Concrete detail — the config file a
  skill reads, the script it runs, the check that has to pass before it will sign off, the exact
  condition that makes it reject — is drawn from each `SKILL.md`, not summarised from the
  section it replaces.

  Two smaller fixes ride along. The list voice was clipped noun-stacks with a bolted-on audience
  tag on all nine entries, sitting directly beneath ordinary prose; the entries are now written
  the way the rest of the page is. And the ordering is now broadest-reach first within each
  group, narrowing to the specialist cases, with the sentence that states the ordering rule
  rewritten to match — the page previously described an order it was not using.

- [#14](https://github.com/MrBinnacle/skills/pull/14) [`bd66a9b`](https://github.com/MrBinnacle/skills/commit/bd66a9ba763eefc277077fde803e59864320c778) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Reconcile the README and the evidence records after the `im-down`/`im-up` pair was added.

  The pair was bolted on rather than folded in, which left the collection saying several things
  that were not true:

  - The two new records used a different schema from the other seven (a bullet list against the
    documented table), so the README's "The receipts, explained" section described 7 of 9 receipts.
    Both are now on the schema `AGENTS.md` documents. `Promotion blocker` — a term used nowhere
    else in the repo — folds into `Screen result` as the registered screen task; `Fixture classes`
    folds into `Validated against`.
  - All seven original records opened with a pointer to a README section called "Evidence records",
    which does not exist. The section is "The receipts, explained". Nine pointers repointed.
  - The four failure modes explained 7 of 9 skills. `im-up` now sits under [#1](https://github.com/MrBinnacle/skills/issues/1) (green lights you
    didn't earn) and `im-down` under [#3](https://github.com/MrBinnacle/skills/issues/3) (momentum past the finish line), placed by the failure each
    one actually answers.
  - The README said every skill exists because something went wrong. That was false for two of
    them: the session-boundary pair was built deliberately. Records now carry a `DESIGNED` origin
    with dates instead of an `OBSERVED` one, and the README says so plainly.
  - `im-up`'s record said four fixture classes; nine is the measured figure. Corrected.

  Both records now also carry what they were missing: the adversarial review by reproduction that
  found and closed four verification holes, and the CI coverage on Linux and Windows.

  README moves to the first person throughout.

- [#61](https://github.com/MrBinnacle/skills/pull/61) [`1363b15`](https://github.com/MrBinnacle/skills/commit/1363b15ec0f339f33debaa2fb2f65473150821e9) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `im-down`: enforce the close-before-packet order instead of documenting it.

  A session close is two commands in a fixed order — the durable close commits, moving `HEAD`, and only then may the packet record `HEAD`. Reversed, the close moves `HEAD` out from under a packet that already recorded it, and the receiver rejects that packet as stale in the _next_ session. The skill's `gotchas.md` carried this as `[ANTICIPATED]`; it has now been observed twice in a project that had already written the order into an always-loaded file.

  Prose cannot hold the constraint, because whoever types the second command cannot see the effect of the first. So the requirement is now declarable: a config carrying `"close_commit": { "contains": "RITUAL:" }` makes produce mode refuse a packet whose `HEAD` commit message lacks that marker, and name the repair. Projects that declare no `close_commit` are unaffected.

  The key is `contains`, not `pattern`, because it is a literal substring test — named `pattern`, a project would reasonably write `"^RITUAL:"` and get a check that matches nothing and refuses every packet.

  The stale-HEAD check is untouched and still does its own job. `close_commit` establishes that the close happened, not that nothing follows it — and not that the close is _this_ session's, which is recorded as a known limit in `gotchas.md`.

  `duplication_case()` now guards all three files the pair ships in common, not just `validate_packet.py` — `test_validate_packet.py` and `CONFIG.example.json` were byte-identical across `im-down`/`im-up` too, with nothing catching a divergence.

- [#73](https://github.com/MrBinnacle/skills/pull/73) [`d63f98d`](https://github.com/MrBinnacle/skills/commit/d63f98db64a3101140786f26c440fd89e5fe16da) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Correct downstream instruction framing to test evidence access per decision, keep decision
  authority explicit, and reserve revisit clauses for outcomes that new evidence can change.

- [#159](https://github.com/MrBinnacle/skills/pull/159) [`56ed7e5`](https://github.com/MrBinnacle/skills/commit/56ed7e52daf39628cfbdd0aa6900d417379c3702) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Recompute the front page's stated disposition counts from the record it links.

  The README's "Admission method" paragraph restates what the S295 disposition found: how many cards it triaged, how many it stood, how many it called thin, and how many it called ceiling-likely. Those four counts were hand-maintained prose -- the same shape that left the origin tiering claiming seven when the records read six (2026-08-15), only this count was never re-derived at all.

  `scripts/validate_disposition_counts.py` recomputes each stated count from the one record the page links -- the disposition record's `## Verdicts` table -- and refuses on disagreement, naming the count and both values. The verdict vocabulary is closed (`STANDS`, `RECURRENCE-THIN`, `CEILING-LIKELY`), so an unknown verdict is refused rather than miscounted, the same refusal discipline the measured and origin counts use. Stating a count stays optional (the ruling that retired the banner and origin tallies); a count the page does state must agree with the record.

  The expected value is derived from the tree, never written into the check or its test. A number-word vocabulary (the same pattern `test_release_model_disclosure` uses) parses `nine`, `two`, `six`, `one` off the page; the record's own rows are counted by category. A poison control mutates a copy of the record so a disagreeing page is rejected for that reason, naming the count and both values.

- [#92](https://github.com/MrBinnacle/skills/pull/92) [`9aaf5c9`](https://github.com/MrBinnacle/skills/commit/9aaf5c9b941739677d54428608637de9d52193d6) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record the one controlled screen that has actually run, and stop the front page saying none has.

  `git-pull-rebase-trap`'s `EVIDENCE.md` said `Screen result | UNMEASURED`. The harness screened that card on 2026-07-21 against the screen the card itself registers, kept the trial store, and published a receipt (`docs/sers/receipts/reclass-git-pull-rebase-trap.json`) carrying `CANT_TELL_YET` at p0 = 1.00 on a 3/3 bare arm. `UNMEASURED` asserts "never looked", and that was the wrong thing to assert.

  The record now says what happened and what it is worth. `CANT_TELL_YET` here is a statement about the instrument, not the card: a transformative-lift screen asks whether a stock agent fails unaided, so an above-bar bare arm means the trap did not come up in those three runs — not that the skill has no value. Two limits are stated with the number rather than left for a reader to discover: the screen predates this card's 2026-08-12 edit, and only the Null arm ever ran, so the card's own text was never an input to the result. `Paired verdict` stays `UNMEASURED`, because no Full arm has ever run.

  `README.md` claimed in two registers that the controlled fields are empty — once as the open question and once in "What this isn't" ("the controlled fields are empty and I am not going to dress that up"). Both are now true statements about one measured card and eight unmeasured ones. The page's own neighbouring paragraph had predicted this exact failure: a front-page claim that every record is empty goes false the day any skill ships a controlled result, and silently. It went false, and the roll-up did not notice — the scoreboard `measured` count is derived from the controlled fields, so it moved 0 → 1 across all five sites the moment the record was corrected. That derivation is what caught it here.

- [#145](https://github.com/MrBinnacle/skills/pull/145) [`61fd40b`](https://github.com/MrBinnacle/skills/commit/61fd40baae2147ef032d14ae76d7afbc323198e5) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record what a release of this collection is, and what its version number promises.

  Until now a release delivered nothing. Both documented install routes track `main`, the package
  is private and has never been published to a registry, and `CHANGELOG.md` stated the position
  outright: tags and the changelog are _"informational — a reading aid, not a pin."_ `v1.2.0` sat
  in `package.json` and the changelog while `git tag` stopped at `v1.1`, with 76 commits
  accumulated past it.

  `docs/adr/0002-a-release-is-a-delivery-event.md` records the decision that a release is the act
  of delivering changed cards to installed users, the mechanism that makes it one — a `version`
  on each plugin entry, which the platform documentation says is what stops users receiving every
  commit — the two rejected alternatives, and the consequences that are now owed.

  The same ADR makes the declaration Semantic Versioning requires and this repository had never
  made. **The declared surface is the install path and the card format. The card set is not part
  of it**, so admitting or retiring a card is a minor change. The narrow reading is deliberate:
  under the wide one, every retirement is a breaking change, and a collection whose stated purpose
  is to retire cards on evidence would either inflate its major number until it meant nothing or
  acquire a standing reason not to retire.

  `CONTEXT.md` gains the two terms this fixes in place — **Release** and **Declared surface** —
  each with the words it displaces.

  This changeset is a patch by the rule the ADR itself declares: no card changed, and the install
  path did not move.

  Nothing is implemented here. The manifest `version` fields, the generator that derives them from
  `package.json` rather than duplicating them by hand, and the pre-publication gate are each named
  in the ADR's consequences as owed work.

- [#118](https://github.com/MrBinnacle/skills/pull/118) [`1144b4d`](https://github.com/MrBinnacle/skills/commit/1144b4dd7a5961572d3b87549096a18edcc14e3e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record a second, independent occurrence of the return-channel failure, and answer admission criterion 2 for the `subagent-research-reliability` patch staged in `_quarantine/`.

  The rotation pass exists to collect evidence that accrues faster than anyone records it. This pass produced one countable occasion, and it happened inside the pass itself.

  **What happened.** On 2026-08-24 the pass dispatched four `reader` subagents to extract origin text from 25 skill cards. The dispatch named no return channel; each prompt ended `Your final message IS the data`. A subagent's plain text is a dead letter — the main session never receives it. Four idle notifications arrived carrying no content, and no extract reached the session. The extraction was abandoned and redone by a mechanical script over the same 25 cards.

  **Why it counts.** The staged patch documents its origin as `workspace_lint` S026, 2026-08-18/19: three `Explore` scouts dispatched with no return channel named, four idle notifications carrying no content. The 2026-08-24 occurrence is a different repository, a different agent type, and a different task, six days later. The four agents in one dispatch are one occasion, not four — `ADMISSION.md` criterion 2 refuses fan-out from a single run.

  **The discipline that would have caught it was staged, not live.** `grep -c "dead letter"` returns `0` against the promoted card and `3` against the candidate's `SKILL.md`. `Check 0` is the patch. The promoted skill was installed and active throughout and carries no such check, so the failure recurred in exactly the gap the patch closes.

  **One narrowing the new occurrence adds, which the origin could not.** `Check 0` offers two return routes so that one failing is survivable. Occurrence 1 recovered with `SendMessage` **plus** one authorised absolute path. Occurrence 2 used `SendMessage` alone — all four agents were re-instructed with the output contract restated verbatim, each woke, and each emitted a second idle notification carrying no content. Nothing was recovered. On this evidence the file at a named path is the load-bearing route and `SendMessage` is not a substitute for it. Route 2 was not exercised alone, so its standalone sufficiency remains untested and is not claimed.

  **What this does and does not license.** Criterion 2 is answered for the `Check 0` branch, and criterion 2 was the standing blocker on every candidate in `_quarantine/`. It is the only criterion this pass measured. Criteria 1, 3 and 4 are untouched. The candidate still carries no `EVIDENCE.md` and has not been through the frontmatter normalization in `AGENTS.md` step 2a, so this records evidence rather than proposing a promotion.

  No published card changed. No count on any published card moved. The published tree is unmodified by this pull request.

- [#127](https://github.com/MrBinnacle/skills/pull/127) [`78ecc0f`](https://github.com/MrBinnacle/skills/commit/78ecc0f04a2962ea6689d850a03fc25660c83ec1) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - The card-contract checker now verifies the card against the occasions row, closing the undercount direction ([#105](https://github.com/MrBinnacle/skills/issues/105)).

  The checker enforced four properties of the `Occasions counted` row — integer opening, count-equals-citations, corroboration of every cited date, and the recurrence-thin label in both directions — and every one took the row as subject and the card as reference. A newly recorded occurrence the row failed to cite passed green: the undercount direction had no check. The new reverse direction scans the card's corroborating text (the same haystack the forward check uses, row excised) and refuses any dated occurrence record the row does not cite, naming the uncited date.

  The scope rule was settled by measurement, not argument: a full-haystack demand flags all nine published cards on dates that are demonstrably not occurrences (screen dates, methodology pins, verification dates, validation-genre entries), so the rule is about how an occurrence is recorded — a line carrying both a date and the word "occurrence" is an occurrence record. Measured zero uncited occurrence-marked lines across the live nine, so the check passes the tree today and enforces freshness on the recording convention going forward. The gotchas-only scan the issue body proposed was not built — it would have turned two healthy cards red whose counts rest on sibling-row records, and a regression fixture now protects exactly that shape.

- [#119](https://github.com/MrBinnacle/skills/pull/119) [`02b66ed`](https://github.com/MrBinnacle/skills/commit/02b66ed1ee101132f9a95c11ca57fb53c148bbf7) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Test `Check 0` against its own claim, and confirm the redundancy it prescribes is load-bearing.

  PR [#118](https://github.com/MrBinnacle/skills/issues/118) recorded a second occurrence of the return-channel failure and stated one limit explicitly: route 2's standalone sufficiency was untested and not claimed. It has now been tested against the same four agents in the same session.

  ## The result

  | agent | route 2 (named file)                     | route 1 (message)           | outcome                                     |
  | ----- | ---------------------------------------- | --------------------------- | ------------------------------------------- |
  | A     | 6 of 6 blocks, 10,869 bytes              | —                           | complete via route 2                        |
  | B     | 7 of 7 blocks, 20,500 bytes              | completion summary          | complete via route 2, signalled via route 1 |
  | C     | blocked by the host's own guard, 0 bytes | 6 of 6 blocks, full content | complete via route 1 fallback               |
  | D     | never given a channel                    | —                           | never delivered                             |

  **With no channel named: 0 of 4 agents delivered**, across three rounds and nine idle notifications carrying no content. **With a channel named: 3 of 3 delivered.** Agent D is a natural control — the only one never given a channel and the only one that never delivered.

  The returns were substantive. One block quotes a card's origin paragraph verbatim, names the section heading it sits under, and lists the distinctive literals requested. The agents had done the work throughout; none of it could reach the session until a channel existed to carry it.

  ## Route 2 has two failure modes, and neither is the agent's fault

  **It has no completion marker.** An earlier revision of this record reported one return as incomplete — "five blocks where seven were asked for". That was wrong: the file was read while the agent was still writing it, 5 blocks at sampling and 7 when finished. `Check 0` names a path but never says how the reader knows the write finished. A partially-written file reads as a complete short answer and nothing distinguishes the two.

  **The host's tooling policy can forbid the write.** Agent C's file stayed at 0 bytes because a `PreToolUse` Bash guard on this machine refuses prose authored into a `.md` file through a heredoc — correctly, since that mechanism is known to fail here. The agent fell back to route 1 and returned everything in the message body.

  ## What the evidence actually establishes

  This finding moved three times as evidence arrived, and the movement is recorded rather than smoothed over. First reading: route 2 is sufficient and route 1 is not. Second: the routes are not redundancy, the file carries payload and the message carries completion. **Current reading, on the full evidence: the check's redundancy framing is correct, and the reason is sharper than the check states** — the two routes fail for unrelated causes, so one failing genuinely is survivable. Agent C is the proof.

  **The load-bearing instruction is to name a payload channel at all.** Which one mattered less than that one existed.

  ## Two additions `Check 0` would benefit from

  1. A completion contract — a signal when the write is done, with an unsignalled file treated as still in flight.
  2. Name the writing tool, not just the path, so the agent does not reach for a mechanism the host blocks.

  Neither edit is made here. Changing the check is a change to the card's procedure and belongs in its own reviewable diff.

  No published card changed. No count moved. The published tree is unmodified by this pull request.

- [#47](https://github.com/MrBinnacle/skills/pull/47) [`b24b64c`](https://github.com/MrBinnacle/skills/commit/b24b64c9bbbe2a1f52d96e3ced722bb153b47ada) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Add a scoreboard validator that refuses front-page count drift and admission-policy version drift.

  The kept / retired / turned-away numbers are a conservation claim on the banner and README alt. A partial retirement edit could leave them wrong with nothing red. `scripts/validate_scoreboard.py` derives the three counts from the skill tree and `RETIRED.md`, asserts all five scoreboard sites, and checks the gate card's normative-status version against `ADMISSION.md`. It joins the existing `validator` job with poison-control fixtures, and emits ASCII-only `PASS:` / `REJECTED:` lines so the Windows matrix cell stays honest.

  `ADMISSION.md` now declares its version in exactly one place. The other two occurrences became prose that references the declaration instead of restating the string, and the validator refuses both a missing declaration and a second one. Fewer declaration sites is a stronger guarantee than a smarter checker: with one site a partial bump cannot be expressed, so it cannot be missed.

- [#86](https://github.com/MrBinnacle/skills/pull/86) [`532ede0`](https://github.com/MrBinnacle/skills/commit/532ede07ebd48a56db75160bfd2a47dc9e20f56f) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `SECURITY.md` and `README.md` stop claiming that a skill is a plain-text markdown file, and say
  what this repository actually ships.

  The claim was false as published. `SECURITY.md` opened with _"A skill is a plain-text markdown
  file. Installing one: executes **nothing** on your machine"_ while five tracked `.py` files sit
  inside `skills/engineering/im-{down,up}/`, and both cards' `SKILL.md` instruct the agent to run
  them. The README repeated it.

  The replacement separates installation from execution, which is the distinction the old sentence
  collapsed: nothing runs at install time, and a script runs when the skill runs, subject to the
  host's permissions. It also restores the audit instruction. That last part is the actual repair —
  the old sentence was worse than inaccurate because it told a reader there was nothing to audit,
  so it cost them the review the platform's own guidance asks for.

  A new commitment 3 states that any code a skill ships is readable source, names the four permitted
  formats plus the conditional bytecode rule, and carries the check a reader runs against their own
  installed copy.

  Two claims elsewhere in the same files were contradicted by admitting scripts and are corrected
  here rather than left standing: commitment 1's _few minutes end to end_ bar, which `im-down`'s 627
  lines of Python fail, and the README's definitional _a skill is a small markdown file_. Commitment
  3 also no longer says a shipped script is invoked only by the skill's own instructions — the two
  test suites are run by CI and no skill invokes them, and a reader auditing the folder will find
  them.

  The reader-side command was found to be strictly weaker than the gate it reproduces: a bare
  `-path '*/__pycache__/*.pyc'` matches at any depth, so a payload nested one level inside
  `__pycache__` was skipped by step 1 and waved through by step 2, on a tree CI rejects. Both steps
  in `scripts/validate_skill_formats.py` and `scripts/check-installed-skills.sh` are now anchored to
  one level, with a regression case running both instruments over that tree and requiring the same
  verdict. The command's target is no longer a hardcoded `~/.claude/skills/<name>`, because
  `npx skills add` installs project-locally unless `--global` is passed.

  The commitment says CI **detects** violations, not that it prevents them. `main` has no required
  status checks, so a nonzero exit is a signal rather than a gate. Publishing the stronger verb
  against the weaker mechanism would have reintroduced this effort's own defect inside the sentence
  written to remove it.

- [#77](https://github.com/MrBinnacle/skills/pull/77) [`f27673e`](https://github.com/MrBinnacle/skills/commit/f27673ec86ab9c423036e2d322a3c605ac595915) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Add the skill-folder format gate, plus the command a reader runs on their own copy.

  `SECURITY.md` is about to commit to a closed vocabulary: every file inside a skill folder is `.md`, `.txt`, `.py` or `.json`. `scripts/validate_skill_formats.py` is the check behind that sentence. It walks and evaluates a predicate per file, with no per-file allowlist anywhere in it, so a new violating file turns the run red with nobody remembering to update a list. It discovers skill folders by the presence of `SKILL.md` — the marker the installer keys on — rather than by the literal path `skills/**`, which brings the fixture trees under `scripts/fixtures/` inside the guarded set by construction. All violations are listed, not just the first. The walk follows symlinks, because installs are symlinked and a walk that does not follow them skips the files it exists to guard.

  Compiled Python is admitted only when the source it derives from sits beside it: `__pycache__/mod.*.pyc` passes if and only if `mod.py` is in the parent directory. A skill that ships a script leaves bytecode behind the first time it runs, and blanket-skipping `__pycache__` would answer that while carving out a directory the check never opens. A payload at `__pycache__/evil.pyc` has no `evil.py`, so it fails.

  A co-located gate makes the claim maintainable, not verifiable — one commit can add a violating file and widen the vocabulary in the same diff, and green CI is invisible to a reader anyway. So it ships paired with `scripts/check-installed-skills.sh`, the same check aimed at an installed copy. The two `find` commands in it are generated from the same suffix tuple the walker enforces and are asserted identical by the suite, so the published text cannot drift from the predicate.

  `scripts/test_validate_skill_formats.py` builds every rejection case as a real tree and runs the real entrypoint: a planted `.sh`, bytecode with no source, an extensionless file, a violating file in a `SKILL.md` folder outside `skills/`, and a root with no skill folders at all. Two of those also run as visible poison-control steps in the `validator` job.

  **This detects violations. It does not prevent them.** `main` has no branch protection and no required checks, so a nonzero exit here is a signal, not a gate.

- [#143](https://github.com/MrBinnacle/skills/pull/143) [`16c0d58`](https://github.com/MrBinnacle/skills/commit/16c0d58b873e59eae5a595ce770cbcc9026b331e) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Add the in-skill skill-invocation phrasing convention to the authoring conventions.

  Operator-lodged 2026-08-24, from Matt Pocock's same-day guidance, verbatim: _"the best
  phrase I've found to invoke a skill from within another skill is: 'Call the Skill tool
  with `skill-name`.'"_ The convention: any skill card whose instructions invoke another
  skill writes that exact phrase, naming the tool and its argument, rather than "run X" or
  "use X" — a bare verb leaves the invocation to the reader's inference. No published card
  currently instructs a skill invocation (verified by grep before this change), so this
  lands as a convention for future cards rather than an edit to existing ones.

- [#93](https://github.com/MrBinnacle/skills/pull/93) [`656f4e6`](https://github.com/MrBinnacle/skills/commit/656f4e60ba6934e35a87b0166d5e03797c2f9796) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - State the standing obligations a published card owes, and re-check them on a clock.

  The collection had an entry gate and no stated standing obligations, so every post-admission breach to date was found by someone reading. `SECURITY.md` gains a versioned **Standing obligations** section — `conformance v1`, declared in exactly one place, with the admission policy's bump rule in substance: a material change to the obligations or to what counts as meeting one bumps the version, editorial changes do not. It is a section rather than a new root file because the strongest argument for a root policy file was O5, and O5 is precisely the obligation this repository cannot machine-check.

  Six obligations, each stated as what it is. O1 declared formats only, O2 no fetch-and-execute, O3 shipped scripts named in `SKILL.md`, O4 `EVIDENCE.md` present with all controlled fields, O5 controlled fields not contradicting a published receipt, O6 scoreboard lockstep. Two commitments are listed as attested and not checked rather than left to look machine-checked: the few-minutes readability bar names no number deliberately, and no-secrets-handling is a semantic property of English that word-matching gets backwards — a card telling the agent to _refuse_ when a secret may be present scans identically to one that mishandles secrets. Commitment 5 is re-homed as a claim about the distribution channel, because no file in the tree can witness that nothing self-updates; the tree is the thing that would be updated.

  **O5 is checked on the maintainer's clock and is never promised as a CI check.** The measurement store is private, so there is nothing here to compare a controlled field against. The sweep reports it `CANNOT-CHECK` on every card by construction, and a test asserts it can never go green from inside this repository — a false promise of a check that never ran is worse than the absence.

  `scripts/validate_conformance.py` runs the six over the published tree and reports `PASS` / `FAIL` / `CANNOT-CHECK` per card. `CANNOT-CHECK` is a separate count that is never folded into the pass total, and the green line says how many cells went unverified. The obligations come from a structured list rather than from substring-matching the published sentences: the prototype this is promoted from did the latter and the hard-wrapped prose turned two conforming cards red. Prose and check are instead held together by a test asserting the section and the list state the same identifiers in the same order — removing one bullet from `SECURITY.md` turns the suite red. The format vocabulary is the existing gate's predicate, called rather than restated; the controlled-field names are the scoreboard validator's; an obligation with no registered check is refused at import.

  `.github/workflows/conformance-schedule.yml` re-runs the sweep weekly. The gap the change-triggered validators never covered is between merges, and a check that never fires is indistinguishable from one that cannot: the run therefore watches itself, filing one labelled issue when the RUN fails and closing it on the next success. It is deliberately not a required check — `main` has no branch protection, and a spurious red would train a sole maintainer to bypass rather than to look. **The schedule ships as a pre-registered trial: if by 2026-11-07 it has caught nothing the pull-request checks missed, it is retired against that criterion rather than kept as ceremony.** The remaining failure mode is social and is named rather than solved — the maintainer can learn to close the issue unread, and nothing here prevents that.

  Two poison controls run in both workflows, and both must fail. A card shipping a script its `SKILL.md` never names is the historical breach shape, and it is the one obligation with a demonstrated rejection. A planted undeclared format must turn the sweep red through the delegated format gate, so the delegation cannot be decorative.

  Per-card `Conformed-under:` fields are deliberately not used at this edition. With one maintainer authoring both policy and cards, a stale value today would mean "nothing was edited", which is not the drift signal the field exists to carry; it arrives with the first version bump. `ADMISSION.md` does not bump — entry and staying are different contracts on different cadences, and a v2 whose questions did not change trains readers to ignore bumps.

- [#113](https://github.com/MrBinnacle/skills/pull/113) [`b477d55`](https://github.com/MrBinnacle/skills/commit/b477d558c80c3b30244c979056314a90c3905816) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - State the rotation and harvest pass in AGENTS.md, from the first executed run (2026-08-23).

  The maintainer commissioned a capability that fires on a plain-language request — "the
  skills repo could use some TLC" — and performs a rotation and harvest pass over this
  collection. The ruling on where it lives: the repo carries the weight, so a cold session
  can run the pass from this file alone; the maintainer's private trigger skill only names
  the evidence locations and points here. The new section states the pass — harvest first,
  the authority table, five steps each with a completion criterion, and three hard stops the
  first executed pass hit for real (the closed screen vocabulary, relative links across tree
  moves, the de-personalization gate firing on raw incident notes). Recurrence recording and
  retirement stay in their existing sections; the pass points at them rather than restating
  them.

- [#107](https://github.com/MrBinnacle/skills/pull/107) [`b27bb96`](https://github.com/MrBinnacle/skills/commit/b27bb96bbb779345db89729cda34dcd307bc6c34) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Extend the glossary with the scoreboard-state vocabulary and two cross-repo false friends, and name `CONTEXT.md` the vocabulary of record in `AGENTS.md`.

  `CONTEXT.md` gains: **Scoreboard states** (the four validator-enforced admission-side counts), **Admitted** (in the collection; says nothing about measurement), and **Admissible (card)** (the four admission criteria — distinct from the measurement instrument's _evidence admissibility_). The operative Avoid-note: "kept" is never an admission label, because `KEEP` is the measurement verdict word and rendering admission state in verdict vocabulary implies an admitted card is empirically proven — the confusion the rejection checklist screens for. Found by cross-context domain modeling against the measurement repo's new glossary; the Brand Kit's example social-preview copy carries exactly this collapse, flagged on the brand ticket before any asset was built.

- [#71](https://github.com/MrBinnacle/skills/pull/71) [`cbca4de`](https://github.com/MrBinnacle/skills/commit/cbca4deb881d69382fb17613f587806bb880cb28) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Bound GitHub Pages deploy polling and report distinct timeout, HTTP failure, and stale-content verdicts.

- [#114](https://github.com/MrBinnacle/skills/pull/114) [`2be350b`](https://github.com/MrBinnacle/skills/commit/2be350b8630d6d3cea3f4a8581e47b425fcff517) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Record the retrieval-vs-insurance diagnosis on the two never-invoked cards.

  `git-pull-rebase-trap` and `github-pages-deploy-verification` had never been model-invoked
  across 261 tracked startups. The rotation pass's discriminator ran on 2026-08-23: a corpus
  sweep of the maintainer's three tracked clones found zero trap occurrences outside each
  card's founding incident. Both diagnoses land as dated gotchas entries: insurance, not
  retrieval defect — and for `git-pull-rebase-trap`, partly displaced enforcement, since a
  PreToolUse guard in the maintainer's environment deterministically blocks the founding
  incident's bare `git pull` upstream of any skill retrieval. During verification of that very
  claim, the guard's recorded mention-only false positive reproduced by blocking a `grep`
  whose argument contained the trigger words. Neither card's evidence record changes:
  non-invocation is retrieval evidence, never an occasion count, and both stay consistent
  with their `CANT_TELL_YET` screen shape.

- [#144](https://github.com/MrBinnacle/skills/pull/144) [`cbdd5e1`](https://github.com/MrBinnacle/skills/commit/cbdd5e1fd4c422c48b3d20fcf08d7457cfb23908) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Repair the changeset header that blocked every release, and close the scoping hole that hid it.

  `.changeset/quarantine-starts-shipping.md` declared the package `@mrbinnacle/skills`. The
  workspace package is `mrbinnacle-skills`. The two names do not match, so `changeset version`
  refused to assemble a release plan and exited with `Found changeset quarantine-starts-shipping
for package @mrbinnacle/skills which is not in the workspace`. No release could be cut from
  `main` while that file was present. It arrived on `main` in `f539b47` on 2026-08-24 and was
  still there when this change was written.

  A check for exactly this defect already existed. The comment above it in `tests.yml` names the
  incident that motivated it. That check runs `changeset status --since=origin/main`, and
  `--since` compares the current ref against `origin/main` — so on `main` the compared set is
  empty, the check exits 0, and it reports `NO packages to be bumped`. The gate written to catch
  this class of defect could not see the instance of it sitting in the same directory. CI was
  green on every run.

  The fix is one additional line: an unscoped `changeset status`, which assembles the full
  release plan over every pending changeset and therefore fails on a bad header regardless of
  when it landed. The scoped call stays, because it is the one that catches a bad header on
  arrival in a pull request. The two answer different questions and the repository needs both.

  A poison control ships with it, and it asserts the two calls **disagree**. It commits a
  changeset naming an out-of-workspace package, points a ref at that commit so the poison is
  present in the tree both refs share, then requires the scoped call to exit 0 and the unscoped
  call to exit non-zero with `which is not in the workspace`. If the scoped call ever starts
  failing there, the control no longer reproduces the defect and fails loudly rather than passing
  quietly. The sequence was executed before it shipped: scoped exit 0, unscoped exit 1, message
  matched, working tree restored.

  The control restores with `git reset --soft`, never `--hard`, so a fault in the control cannot
  destroy a working tree.

  Two findings are recorded rather than smoothed over. First, adding a gate after a defect does
  not remove the defect: this check shipped on 2026-08-24 and the changeset it was written for
  survived it by sitting outside the window the gate looks at. Second, a scoped check reports
  success in the vocabulary of a passing run — `NO packages to be bumped` — which reads as
  health rather than as silence about an unexamined set.

- [#85](https://github.com/MrBinnacle/skills/pull/85) [`e7f79a9`](https://github.com/MrBinnacle/skills/commit/e7f79a980f8ec34d680d270705b4f73adb1779e0) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `BRAND.md` stops deriving the owner's voice by reading the shipped front page, and a check fails
  when a voice specimen has no provenance.

  The method was the defect, not the example. The file said its Voice section had been read off the
  shipped surfaces, so it had no way to tell a line the owner wrote from AI copy already sitting on
  the page — and it picked the copy, because generated prose is smoother and reads more like "voice"
  than the real thing. The loop closed inside one session: the README fed `BRAND.md`, `BRAND.md` fed
  the assistant, and the assistant offered the sentence back to its author as the model for how he
  writes.

  The replacement rule: a voice specimen is a line the owner wrote or ratified, cited to
  `VERBATIM.md`. Provenance is a property of the line, and an unmarked shipped surface cannot supply
  it. All five previous specimens cited `README.md`; two of them quoted the block deleted in [#66](https://github.com/MrBinnacle/skills/issues/66) and
  are gone, and the section is now sourced from the record throughout.

  `scripts/validate_voice_provenance.py` checks four mechanical properties: every specimen is
  followed by an explicit `Source:` line; that source names `VERBATIM.md` rather than a shipped
  surface; the quoted text **equals** a recorded line exactly; and the section and date in the
  citation are where that line actually sits.

  Equality rather than containment, because a fragment of a recorded line is not that line —
  selective truncation can invert a sentence while every word is genuine, and a containment check
  would certify it as verbatim. Comparison joins wrapped lines and changes nothing else, so a quote
  may be re-wrapped but not smoothed: deleting a double space or fixing an apostrophe turns the run
  red, because that roughness is the evidence a person typed the line.

  An **inline** quotation in the Voice section is refused rather than checked. That is the shape
  every replaced specimen had — `*"..."*` with the front page named in the surrounding prose — so a
  blockquote-only check would have passed the very file it exists to have caught.

  The check makes no judgement about whether a line sounds like the owner, and does not try. Three
  poison controls run in CI — a specimen sourced from `README.md`, a fabricated quote carrying a
  correct citation, and an inline italic quotation — each asserting the run failed for that reason
  rather than incidentally.

- [#74](https://github.com/MrBinnacle/skills/pull/74) [`9559cc4`](https://github.com/MrBinnacle/skills/commit/9559cc48c59613960268583a166cf9d83ad667c7) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - `git-pull-rebase-trap`: narrow the card's claim to explanation, prevention-by-recipe, and recovery, and publish adopter-owned preventive recipes for Claude Code `PreToolUse` and shell wrappers.

  Both recipes share a required block/pass table, including explicit pull intent, config access, mention-only false positives, and fail-open behavior. The card still ships no executable hook, and its recovery runbook is unchanged.

- [#142](https://github.com/MrBinnacle/skills/pull/142) [`a70fe5c`](https://github.com/MrBinnacle/skills/commit/a70fe5cfc591159b2ece3c1e5a2977bd280626e3) Thanks [@MrBinnacle](https://github.com/MrBinnacle)! - Complete the writing-for-agents body pass on the six cards promoted 2026-08-23.

  The six promotions shipped with rewritten descriptions and normalized frontmatter, and
  their bodies untouched. Measured on 2026-08-24, four of the six exceeded the 5 KB split
  threshold that `AGENTS.md` sets, and three exceeded its ~7 KB ceiling. An earlier partial
  pass on one card had made it larger, not smaller — 8448 to 8736 bytes — which is the
  recorded evidence that commentary without cuts does not pay; that branch was parked rather
  than merged. This change finishes the pass.

  **What changed, per card, with before → after sizes:**

  - `router-skill-predicate-gap` 8736 → 6967 B. The origin incident was told three times
    (trigger bullet, Example, and in full in `gotchas.md`); it is now told once in a
    compressed Example whose full record stays in `gotchas.md`, where the append-only log
    already carried it. The step-1 and step-5 probe loops were the same loop written twice;
    step 5 now runs the step-1 loop with different inputs. The earlier partial pass's three
    genuine fixes (the unrunnable `for p in ...; do ... done` literal made a complete loop,
    the step renumbering, the prohibition rewritten positive) are kept.
  - `success-test-accepts-any-output` 8197 → 7031 B. The 2026-08-17 outage incident appeared
    in a trigger bullet, a rule-1 caveat and the Example; the stringify defect appeared four
    times. Each now has one home: the pattern in its rule, the incident in the Example. The
    dated `gh api` claim-status caveat is compressed but keeps its substance: `--silent` is
    documented, the error stream is not, and the claim rests on a reproduced-once observation.
  - `halt-as-deliverable` 7422 → 5423 B. Steps 2 and 4 ("resist the quiet re-run" / "make it
    loud") stated one instruction from two directions and are merged; the behavioral-economics
    aside folded into that step; one Note that restated a Solution step is cut. The decision
    table and the four-point verification list survive intact.
  - `click-clirunner-env-none-deletes` 6582 → 5866 B. The monkeypatch advice appeared in both
    Fix and Notes; it now lives in Fix. The trailing References section is removed per this
    repository's own cross-reference convention: two of its three links moved inline to their
    moment of need (the testing-module source into Root cause, the monkeypatch reference into
    Fix), and the third — the general CLI-testing guide — is cut as redundant with the more
    specific API-reference link the Notes already carried. The dated signature-verification
    paragraph is compressed without dropping the claim's basis.

  The remaining two promoted cards, `pretooluse-bash-guard-prose-false-positive` (4395 B) and
  `mock-masked-stub-trap` (4156 B), were assessed under the same pass and their bodies left
  unchanged: both are under every threshold and carry no internal duplication worth a diff.

  All six cards' `EVIDENCE.md` standing-cost rows now state exact, dated byte counts — the
  four edited cards because their sizes changed, and the two unchanged cards because their
  rows were stale approximations from before the description rewrites. All seven repository
  validators and the spec validator (`skills-ref` 0.1.5) pass over the edited tree.

  An independent fresh-context review ran twice over the cuts. Round one found four defects,
  all fixed: the compression had deleted a Notes sentence that `gotchas.md` quotes verbatim
  (the "a router rule deserves a test suite" claim — restored); a `§ 1b` pointer in that same
  `gotchas.md` had dangled since this branch's own renumbering (corrected to `§ 2`); the
  link-migration claim in an earlier draft of this changeset overcounted by one (corrected
  above); and the draft described the review in the past tense before it had run — the
  false-confidence tell the review lens exists to catch, recorded here rather than smoothed
  over. Round two returned seven lesser findings: four dropped-content items were restored
  and paid for by cuts elsewhere (the stderr-capture fallback and the GraphQL-routing fact in
  `success-test-accepts-any-output`, the entry-point symptom in
  `click-clirunner-env-none-deletes`); two were declined with reasons recorded on the pull
  request (a repeated leading word that is not a repeated meaning; a removed attribution
  whose idea survives); and the size figures above were re-corrected after the restorations.

  One boundary stated rather than fixed: no gate checks card size — the 5 KB and ~7 KB
  figures live in `AGENTS.md` prose only, the same enforcement shape the description bar had
  before it became a gate. Per the cross-family adjudication of 2026-08-24, a prose bound
  earns a gate on observed recurrence, not on shape; this pass is occurrence one after that
  ruling.

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
  _shipped_ skill. Claude Code now delivers the assistant's final turn inline via
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
