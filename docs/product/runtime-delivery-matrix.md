# Runtime delivery matrix

Checked **2026-10-17 UTC** for [#420](https://github.com/MrBinnacle/skills/issues/420).
This records existing delivery routes. It does not change packaging or runtime settings.
Offline loader checks and temporary Claude Code plugin installs ran for this inventory.
No provider request or efficacy experiment ran.

## Terms and evidence limits

- **VERIFIED**: a named source or observation supports the stated fact. The scope of that observation still applies.
- **INFERENCE**: the sources support an explanation, but the relevant runtime observation is missing.
- **UNKNOWN**: the search did not locate the evidence needed to decide.
- **UNMEASURED**: this inventory did not run the relevant test.

These are claim labels, not whole-product grades. A file on disk, a discovered skill,
a description sent to a provider, a body loaded into context, and useful behavior are
five different observations. One does not prove the next.

The [Agent Skills specification](https://agentskills.io/specification) supplies the shared
`SKILL.md` format. It does not make runtimes equivalent. The [Pi skills documentation](https://pi.dev/docs/latest/skills)
and [Claude Code skills documentation](https://code.claude.com/docs/en/skills) describe their
own loading rules. Those vendor pages were fetched on the check date; they are not
version-pinned documentation for every installed binary below.

## Repository and content identities

**VERIFIED:** the local directories named `skills` and `skills-pi` belong to the same
`MrBinnacle/skills` Git repository. `git worktree list` establishes that relationship.
The second directory is a worktree, not evidence of a second repository or product.

| Identity | Revision or version | What it identifies |
| --- | --- | --- |
| Skills main source, called **M** below | `206842d7bfdac3dab323207ee1e01749c036027c` | Published bucket manifests and 14 canonical cards under `skills/` |
| Configured Pi worktree, called **P** below | `42c5346b7dd742b2fc42de88fca72912b7285740` | Four directly loaded canonical cards and eight cards under `pi/skills/` |
| Published Pi source with the same tree as P | `8abc5e2c1565b5c80fc7173c75ff7fd0cdd28607` | `pi-port`; a squash changed commit identity, not file content |
| Root package at M and P | `mrbinnacle-skills` `3.0.1`, `private: true` | Repository metadata; neither root has a `pi` manifest |
| Installed Pi runtime | `@earendil-works/pi-coding-agent` `1.3.0` | Installed package and loader used for the offline observations below |
| Installed Claude Code | `2.1.296` | Output of `claude --version`; not the historical cold-install version |
| Published Harness adapter source, called **H** below | `ee62b2a90d46f8769c499aa292d8c37ba31dc69a`, package `0.3.0` | Separate measurement repository, not a Skills distribution |

Source anchors: [M package](https://github.com/MrBinnacle/skills/blob/206842d7bfdac3dab323207ee1e01749c036027c/package.json),
[P-equivalent package](https://github.com/MrBinnacle/skills/blob/8abc5e2c1565b5c80fc7173c75ff7fd0cdd28607/package.json),
and [H package](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/pyproject.toml).
The repository paths below are relative to these roots. User-specific absolute paths are omitted.

### Card bytes are not interchangeable

These are SHA-256 digests of the full file bytes, not names or package versions.
Working files at M and P were also compared with their Git blobs; their bytes matched.

| Canonical path | M SHA-256 | P SHA-256 |
| --- | --- | --- |
| `skills/engineering/vacuous-check/SKILL.md` | `e49527e3242b9bc30dae38b3d895cb255741acd59911298c8c457b20f7663b99` | same as M |
| `skills/engineering/mocked-stub/SKILL.md` | `02b6bef961c1809fc15da92b4e9eb28b2cb26aa84cba11947edfdd2b865c1dfd` | same as M |
| `skills/engineering/pull-rebase/SKILL.md` | `e62bd4068c6ea6de252212b5f8ccabf44f944c67ba0a2a9e57dd7bd1940d53d4` | `371059e683db526a9e754a4a56674b7bc3bc9de4d8f9c1a921c7900925a2559c` |
| `skills/orchestration/decision-rights/SKILL.md` | `2d7de62b850dfecc7a8ed5452edbb1d5141c1e439a6231bdf0d1d968eb4325af` | `12dcd04c8d7149c8e6aa1d4ab4ea78eb59694874ac93f7216281fd0e34c52cef` |

The complete M card set has 14 entries and digest
`311684686689bc0a939523dcce019071adf013ea4200de1c7520d7c6e3921a5f`.
To reproduce that set identity, sort the repository-relative POSIX paths matching
`skills/*/*/SKILL.md`. Build a list of `[path, sha256(file_bytes)]` pairs in that order.
Encode it with Python `json.dumps(pairs, separators=(",", ":")).encode("utf-8")`, then hash those bytes.
This identifies card files only, not their supporting files or runtime configuration.

The remaining eight configured Pi cards have these identities at P:

| Path | SHA-256 |
| --- | --- |
| `pi/skills/nameable-half/SKILL.md` | `50aebfcfb44bdcfe5d5b2403e2a26b007aaafa276c7f49eb7a18a4ed09ff32ec` |
| `pi/skills/phantom-answers/SKILL.md` | `16fae1c316524b322c58cfabef370768ae6d9d36996691f3db55511bbd4cf65f` |
| `pi/skills/reviewer-horizon/SKILL.md` | `e433b5ceb008f8e3180158ed5825e23a436f5b10a868dbdcae6fe3e3ac3b2057` |
| `pi/skills/squash-absorbs/SKILL.md` | `0b89e7814ac901548488c4efe02c2d5077670538f58f76bd2c084e4bb315e86f` |
| `pi/skills/uniform-eol/SKILL.md` | `5444de7c2319d0cb37b66e69d1c38ef202f31f135210cdbb3da6ade2e9a30c5d` |
| `pi/skills/walk-the-recipe/SKILL.md` | `da36d3e53fcd0f6b836b604e9b85b9ea7125e663e5b57d466066c96806a042c5` |
| `pi/skills/write-site/SKILL.md` | `f9d869b08a52ceaef7cccb5f03af7a783abe4bdf4ace7fdee6b88f3f29edcf0b` |
| `pi/skills/wrong-altitude/SKILL.md` | `b5140f863828a28554bd4642b774354f4783082dc99093d545f123df69956a9f` |

**VERIFIED:** two of the four directly shared paths differ between M and P.
The routes therefore do not currently supply identical bytes at all four paths.
This inventory does not choose which revision should replace another.

## Delivery routes

All current observations in this table use the check date above. Historical receipts retain their own dates.

| Route | Owner-controlled source and runtime/package | Discovery and configuration | Delivery evidence and invocation observer | Limit |
| --- | --- | --- | --- | --- |
| **Pi: direct canonical cards** | P's four `skills/` paths and digests above; Pi `1.3.0` | **VERIFIED:** user `~/.pi/agent/settings.json` lists the four paths directly. It excludes `~/.agents/skills/**`. | **VERIFIED:** the installed `dist/core/skills.js` loader, called with those paths plus the Pi card directory and defaults disabled, returned all 12 names without diagnostics. Its prompt formatter listed every name. The current agent session also advertises them. Pi documents on-demand body reads and `/skill:name`. A read event or expanded slash input can observe body access. | No provider payload or skill-body invocation was captured for this route. Both are **UNMEASURED** here. Loader output does not prove model compliance. |
| **Pi: Pi-specific cards** | P's eight `pi/skills/` paths and digests above; Pi `1.3.0` | **VERIFIED:** the same settings file lists P's `pi/skills` directory. | **VERIFIED:** same 12-card loader observation. The history at `b79c0bb` removed four copies in favor of the direct canonical paths. | These eight files are separate card bytes, not proof that all 14 M cards have equivalent Pi delivery. Body access and efficacy are **UNMEASURED**. |
| **Pi: executable mechanisms** | P's `mechanisms/`; Pi `1.3.0` | **VERIFIED:** user settings name that directory as an extension resource. | Configuration and source are present. This inventory did not record each extension's initialization or tool execution. | Per-mechanism runtime delivery is **UNMEASURED** by this inventory. Extension code is distinct from a skill's instruction body. No independent npm package receipt was located. |
| **Pi: distribution package** | Same owner repository; P contains the Pi implementation, while M lacks `pi/` and `mechanisms/` | **VERIFIED:** inspected settings load paths directly; no `skills-pi` package entry was found in the inspected user package settings. The root package has no `pi` manifest. | **UNKNOWN:** no clean-install receipt for a distributable Pi package was located in this investigation. | This is not proof that Pi packaging is impossible. [Pi packages](https://pi.dev/docs/latest/packages) can use conventional resource directories as well as an explicit manifest. Selecting or implementing a package remains outside #420. |
| **Claude Code: bucket plugins** | M's `.claude-plugin/marketplace.json` points to `skills/engineering`, `skills/orchestration`, and `skills/meta`; each bucket has its own `.claude-plugin/plugin.json`, version `3.0.1` | **VERIFIED:** manifests enumerate 10, 3, and 1 card paths. On Claude Code `2.1.296`, `claude plugin list --json` lists all three installed plugins as enabled at user scope, but reports `projectEnabled: false` for each in the inspected checkout. | **VERIFIED:** the installed index and cache files exist, but use commit `8535dede2d9c42459958898a7300df66f9c0da7b`, not M. [ADR 0004](../adr/0004-a-plugin-is-its-own-root.md) records measured component inventories. [README](../../README.md) records a clean install on `2.1.287`, **2026-10-02**, with all three plugins at `3.0.1`. | An enabled plugin list is not a current provider-delivery capture. Current body invocation and efficacy are **UNMEASURED**. Historical install success does not attest current M bytes. |
| **`npx skills add MrBinnacle/skills`** | M's README advertises the repository as installer input; M card-set digest above identifies the inspected source, not an installed result | **VERIFIED:** the command is published. **UNKNOWN:** resolved installer version, destination, selected cards, and delivered bytes for a current install | No installer or model was launched. A future receipt must record the resolved installer, destination paths, card hashes, and runtime discovery separately. | Shared `SKILL.md` support does not establish Pi package delivery or equivalent runtime behavior. |
| **Harness: Pi subject adapter** | H's `src/skill_harness/subject/pi/`; Harness `0.3.0`; parser `0.1.0` | **VERIFIED:** launcher source disables ambient skills, context files, prompt templates and extensions, then supplies explicit baseline/treatment skills and its capture extension. Runtime version is measured during pre-spend validation; the caller-supplied-result limitation is described below. | The adapter records a provider payload, runtime roster, native session, read events and slash input. Parser identities and observation limits are listed below. Existing mutation receipts attest specific refusal checks, not a clean install of Skills. | This adapter is measurement machinery, not the installed Pi runtime or a Skills distribution. No new epoch or database ingest ran. Compatibility with this host's Pi `1.3.0` is **UNMEASURED**. |

### Installed Claude bytes

The installed index is `~/.claude/plugins/installed_plugins.json`. Its three cache roots are
`~/.claude/plugins/cache/mrbinnacle-skills/<plugin-name>/3.0.1`.
The index records updates on **2026-10-03** and the commit named above.
Read-only inspection found these file digests:

| Installed card | SHA-256 | Comparison with M |
| --- | --- | --- |
| `mrbinnacle-engineering/vacuous-check/SKILL.md` | `99c02e78aba62acb48fe4763136a579fe8b399d53c76545a248b99c15521b5ec` | Different |
| `mrbinnacle-engineering/pull-rebase/SKILL.md` | `a08e4bf26d6761262a871c021ec06822703543fdf5fd09e13728b407bdb28e5a` | Different, even after CRLF normalization |
| `mrbinnacle-orchestration/decision-rights/SKILL.md` | `2d7de62b850dfecc7a8ed5452edbb1d5141c1e439a6231bdf0d1d968eb4325af` | Equal |

Thus `3.0.1` alone cannot identify what this installation supplies.

A subsequent run of [`scripts/test_install_form.py`](../../scripts/test_install_form.py)
used Claude Code `2.1.296` in temporary, isolated configurations. Both the README's HTTPS
install commands and the checked-out tree installed all three plugins with cards present.
The suite failed one assertion: README's historical CLI version is `2.1.287`, not `2.1.296`.
That is not a passing suite. CI pins `2.1.287` for this check. The suite removed its temporary
installs; it did not record installed card hashes, provider payloads or body invocation.

The [plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
describes packaging fields; the local manifests and historical component observations
are the evidence for this collection's bucket layout.

## Harness observation contract

Read at H: [pin.py](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/src/skill_harness/subject/pi/pin.py),
[launcher.py](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/src/skill_harness/subject/pi/launcher.py),
[parser.py](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/src/skill_harness/subject/pi/parser.py),
[capture.ts](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/src/skill_harness/subject/pi/capture.ts),
and [runner.py](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/src/skill_harness/subject/pi/runner.py).
These are **VERIFIED source contracts**, not a report that a new evaluation ran.

- **Subject identity:** the shared pin records measured runtime version, provider, model,
  thinking level, tool allowlist, cwd, image digest, network policy, declared non-secret
  environment, secret names only, baseline `(name, path, skill_md_sha256)` entries,
  and capture-extension hash. The treatment is recorded separately in the runner block's
  environment and attested in each epoch's roster. It is deliberately absent from the shared pin.
- **Discovery:** the parser compares the runtime-reported roster against the expected roster.
  This is stronger than finding a card on disk, but still distinct from provider delivery.
- **Description exposure:** `v2-description-channel:pi-payload-1` observes
  `before_provider_request.payload.system`. `requests/request-001.json` is mandatory.
  The parser normalizes captured payloads for the shared description detector.
- **Body invocation:** `v1-branch-b:pi-read-1` observes a read-tool access to the treatment
  `SKILL.md`, or explicit `/skill:` expansion. Shell-based reads can be missed.
  Invocation is not evidence that the advice was followed.
- **Identity changes:** parser/capture identity, roster mismatch and mid-epoch subject changes
  have refusal checks. At H, the runner calls `validate_pre_spend(spec)` only when the caller
  does not supply `validated`. A supplied result skips those checks; the runner does not
  establish that the result belongs to the spec it executes.

Measured with `parser_identity()` from H, without a provider request:

| Identity | Value |
| --- | --- |
| Parser version | `0.1.0` |
| SHA-256 of `parser.py` bytes + NUL + `capture.ts` bytes | `9aaf5b25b3a6314ce1e7a73350b04b6e8cecc5c7501a3125d2abd8bcd43bc77d` |
| Python semantic digest, `ast-shape-1` | `99692a3315b2d8fa5df674b2e763c34649a02359494c3e4659473e2bec12c6d0` |
| Capture-extension SHA-256 | `e60b835829e70fe8791bc744b32651e0596f861e2ec547b4a13b0b6e0ccd5392` |

The [adapter refusal receipt](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/docs/assurance/pi-adapter-refusal-mutation-receipt.md)
and [driver wiring receipt](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/docs/assurance/pi-driver-wiring-mutation-receipt.md)
name three and four hand-chosen mutations respectively. Their attested parser, launcher,
and runner file hashes match the current H files. That verifies receipt currency by bytes;
this inventory did not rerun their mutations. It does not establish general adapter correctness or efficacy.

The [description-channel finding](https://github.com/MrBinnacle/skill-harness/blob/ee62b2a90d46f8769c499aa292d8c37ba31dc69a/docs/findings/pi-c-detector-blind-to-description-channel.md)
contains a historical refusal and later correction/re-ingest statements. Its retained text
is not one current verdict. Use it to understand why description exposure and body invocation
must remain separate; do not turn it into evidence of present Pi package delivery or efficacy.

## Future clean-install cases

These cases specify observations, not new authorization to install software or spend on a model.
The first two already have offline loader controls on Pi `1.3.0`:
`loadSkills({cwd, skillPaths, includeDefaults: false})` and `formatSkillsForPrompt(skills)`.
The installed module is `dist/core/skills.js` within the Pi package.

| Case | Known input | Required observation | What remains unmeasured |
| --- | --- | --- | --- |
| **Known-present** | Explicit paths to P's four canonical cards and `pi/skills` | **VERIFIED offline:** 12 names, no diagnostics, all 12 in formatted prompt text. A clean-runtime test must also match each resolved path and digest, capture its description in the first provider payload, and separately observe body access if required. | Clean installation, actual provider delivery and body invocation |
| **Known-absent** | No explicit skills and defaults disabled | **VERIFIED offline:** zero names, zero diagnostics, empty formatted skill prompt. A clean-runtime Null case must also exclude packages, ambient settings and extensions that can inject the treatment. | End-to-end isolation in a new runtime process; an empty path list alone is not sufficient |
| **Unknown / missing evidence** | The proposed Pi distribution installed on a clean host | **UNKNOWN:** install command, resolved package identity, resource roots and resulting card bytes. Record these before comparing discovery against the present control. Do not report success from an exit code alone. | The entire package-install route |
| **Historical absent packaging control** | A marketplace-only plugin root with no bucket manifest | ADR 0004 records zero exposed skills on **2026-09-21**, despite successful validation. Repeat component inspection on the chosen current Claude version before relying on that negative control. | Current-version repeat and provider capture |
| **Claude known-present source control** | M's three bucket roots and their explicit manifests | Expect exactly 10/3/1 component paths. Temporary installs on `2.1.296` found cards in all three plugins, with the suite failure described above. Require installed file hashes and exact component inventories before claiming byte-equivalent delivery. | Installed card hashes, provider exposure and body invocation |

## What changes next

1. Keep runtime support, the measurement adapter and package distribution as separate claims.
2. Name a revision and file digest in cross-runtime evidence. Do not use `3.0.1` or a skill name as a content identity.
3. Resolve the two shared-path content differences before claiming a common delivered card set.
4. Choose a Pi distribution route only when that implementation is authorized. The missing evidence is an install receipt, not a missing repository.
5. Test discovery, description delivery, body invocation and useful behavior separately. Nothing in this inventory establishes adoption or demonstrated usefulness.

The [contract proposal in PR #419](https://github.com/MrBinnacle/skills/pull/419) provided
questions for this investigation. It was unmerged when checked and is not treated here as an adopted product contract.
This document closes the inventory requested by #420, not the implementation or evaluation work it identifies.
