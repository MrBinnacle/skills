# Knowledge context audit

Audited **2026-10-21** for [#421](https://github.com/MrBinnacle/skills/issues/421).
This is a read-only source audit of the owner's Notion workspace against this repository.
It is not a product specification and it proposes no mapping framework.
No Notion page, property or schema was changed during the audit, and no repository file was
changed. The audit was first posted as a comment on #421. This file carries it into the tree.

The Notion conflicts it lists were corrected after the audit, on the same date. See
[Corrections after the audit](#corrections-after-the-audit). Every count and conflict below
still describes the workspace as it was when the audit ran.

## How sources are cited

Each Notion source is named by its page or database title and a generic location. Page links
and page identifiers are left out, because #421 authorizes no disclosure of private page
identifiers. The workspace is private, so a link would not open for a reader in any case.

## Scope of every count

Counts come from SQL over all non-archived rows of each named data source, with no view
filter, on 2026-10-21. Repository checks are against `main` at `62a7e0a`. This file was
written at `main` `5604e79`. The counts were not derived again for it.

Claims ledger entries are cited by id, for example C12, from
[`claims-ledger.md`](claims-ledger.md).

## 1. Live schema, and declared structure against populated relations

The database **Skills Library and Global Context** sits under the owner's tooling section. It
holds two data sources.

- **Skills Library** has 103 rows. Its schema declares identity (`Name`, which its description
  says must match the `SKILL.md` name field), a canonical pointer (`Source URL`), state
  (`Status`, `Lifecycle`, `Evidence`), version and dates (`Version`, `Last Updated`,
  `Last Edited Time`), cost (`Standing Cost (tok)`, `Fired Cost (tok)`, `Aux Cost (tok)`), and
  relations to Global Context, the Capability Menu, projects and source notes.
- **Global Context** has 7 rows. Its schema is three fields: `Name`, `Description` and
  `Source URL`. It has no status, scope, owner or verification-date field.

Declared is not populated. These are the populated counts on the Skills Library.

| Field | Rows populated of 103 |
| --- | --- |
| `Knowledge Relations` (to Global Context) | 3 |
| `Capability Menu` | 8 |
| `Related Projects` | 22 |
| `Source URL` | 54, of which 14 point at this repository |
| `Evidence` | 64 |
| `Lifecycle` | 38 |
| `Last Updated` | 70 |
| `Standing Cost (tok)` | 16 |

For this product the relations are empty. The 14 rows whose `Source URL` points at this
repository have **0** `Knowledge Relations` and **0** Capability Menu links. The 3 populated
`Knowledge Relations` all point at one Global Context row from an unrelated personal domain.
The six other Global Context rows concern skills. No Skills Library row links to any of them.
They have an empty `Description` and an empty `Source URL`; their content is in the page body.

The finding: the skill-to-context relation that the
[product contract proposal](product-contract.md) asks to "preserve" exists as a declared
field. It joins nothing for this product. This is an observation about populated data, not a
request for a schema change.

**Claude Code Capability Menu** is a separate data source with 154 rows. 8 rows link back to
the Skills Library. 26 rows claim this repository through `Canonical Repository` or a
`skills/...` `Skill Path`. Checked against this repository's full history, 25 of those 26 paths
never existed here. 21 are third-party skills recorded as "Inspired / adapted". 4 are
owner-authored candidates that never shipped. The one path with history,
`skills/engineering/azimuth`, appears in two commits and is absent from `main`. None of the 14
cards on `main` has a Capability Menu row that points at its path.

## 2. Sources by kind, with conflicts and verification dates

Each source below carries one label: knowledge, owner decision, hypothesis, implementation,
observed effect, or superseded.

| Source (title, location) | Kind | Edited / stated verified | Note |
| --- | --- | --- | --- |
| **MrBinnacle/skills — Claude agent skills library**, a project page in the owner's projects database | Implementation record, partly superseded | Last edit 2026-10-14. Its snapshot callout says "verified 2026-08-12". The roster line says "verified against GitHub 2026-09-09". | One page carries three dates. The edit date is not the date any claim was checked. Its "Owner-directed product scope — 2026-10-14 (PROPOSED)" section is superseded: [`PRODUCT.md`](../../PRODUCT.md) keeps the #419 thesis and contract as historical proposals. |
| **Skills Library** rows for the 14 cards | Implementation registry | `Last Updated` values run from 2026-08-10 to 2026-09-02. `Last Edited Time` runs to 2026-09-10. | The schema separates the two dates: `Last Updated` is described as "semantic release date". That separation is good design. Neither field records when a row was last checked against the repository. |
| **Skills Library and Global Context**, a row in the owner's workspace database directory | Implementation record | `Last Verified` 2026-09-17, row count 103 | Its "Known Issue" field records a 2026-09-02 census of 99 rows, after a field description recorded 48 rows. Its `Purpose` field says the database is "not the install surface" and that canonical skill ownership is this repository. |
| **Skill standing cost: the measured constant (0.92x)**, a Global Context row | Knowledge (a measured result, scoped) | Created 2026-08-04 | A corpus of 71 skills on the owner's machine, 38 model-invocable. Median standing cost 72 tokens raw, about 81 calibrated. Range 43 to 213 raw. Receipts are in a private research repository. |
| **Cost is a triple, never a scalar (the cost inversion)**, a Global Context row | Knowledge | Created 2026-08-04 | Standing, fired and auxiliary cost rank a corpus differently. Hand-invoked skill bodies were larger (median 2,141 against 1,665 tokens) and cost zero standing. |
| **Language register is Simplified Technical English**, a runbook row in the owner's assistant system | Hypothesis, labelled so by its author | Last edit 2026-09-19 | `Status` is "Hypothesis". `Evidence` is empty. The page body is blank. |
| **literal-humanist-voice**, a Skills Library row | Implementation, identity unknown | `Last Updated` 2026-08-16 | See conflict 3. |

### Conflicts

Each row names the source that owns the fact. The audit changed neither side.

| # | Notion said | Repository says | Owner of the fact |
| --- | --- | --- | --- |
| 1 | `Source URL` for 11 of the 14 published cards is a pre-2.0.0 path, for example `skills/engineering/git-pull-rebase-trap/SKILL.md`. | 11 of those 14 paths are absent from `main` at `62a7e0a`. [`RETIRED.md`](../../RETIRED.md), "Renamed in 2.0.0", maps each old name to its current card. The other 3 (`halt-as-deliverable`, `im-down`, `im-up`) resolve. | The repository. |
| 2 | `Standing Cost (tok)` holds figures from 0 to 100 on the card rows. | Claims ledger C12 gives about 70 to 80 tokens per card, measured with `/context` on Claude Code 2.1.305 on 2026-10-20. C12 forbids citing the `skill-harness skill audit` figures as what a session pays, because [#361](https://github.com/MrBinnacle/skills/issues/361) found none of them within 10% of `/context`. | The repository's `/context` receipt. The Notion column is not a citable source for session cost. |
| 3 | `literal-humanist-voice` has `Lifecycle` = Published and no `Source URL`. | No card of that name exists on `main`. [`AGENTS.md`](../../AGENTS.md) carries a prose-voice convention of that name. | Unknown. The row does not say where it is published. |
| 4 | The project page says the latest tag and Release are v1.1, gives `npx skills add` as the install path, and quotes an About line it calls current. | Claims ledger S8 already lists these as stale and parks each as an owner's edit. | Already recorded in the ledger. This audit adds nothing to S8. |

## 3. Research on standard English, flight manuals and bounded vocabulary

None found in either surface the audit searched. Notion holds the adoption of Simplified
Technical English as a house rule, in the runbook row above and in the assistant's operating
instructions, which date the rule 2026-08-09. Its author labels the rule a hypothesis and
records no evidence. Neither surface holds literature on controlled language, aircraft
maintenance manuals or bounded vocabularies, and nothing in them measures their effect on
agents.

Searches run:

- Notion, keyword search: `Simplified Technical English`,
  `controlled vocabulary flight manual agent`, `ASD-STE100 research controlled language`,
  `aviation maintenance manual plain language instructions`, `STE agent instructions evidence`.
- Repository: `git grep -i` on `main` for `STE100`, `simplified technical english`,
  `controlled language` and `controlled vocabulary`, with no match.

These searches cover the Notion workspace and this repository only. They say nothing about
research held anywhere else.

## 4. What the knowledge changes about a concrete engineering decision

Nothing in the repository's current decisions changes. The two cost pages are real knowledge,
but the repository already carries their content.
[ADR 0008](../adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md) and claims
ledger entries C12 and C13 keep standing cost and on-demand cost apart, and #361 replaced the
harness figures with a `/context` measurement. The 0.92x page's median (72 raw, about 81
calibrated) sits beside C12's 70 to 80 tokens. It corroborates that figure with a different
instrument on a different corpus. It is not the same measurement, and its receipts are not
public.

One negative action follows. Do not cite the Notion `Standing Cost (tok)` column, or the
Notion card rows' `Source URL`, as a source for anything in this repository.

## 5. Additional mapping

No additional mapping is recommended. The relations that exist are empty for this product,
and nothing in the work tracked by [#418](https://github.com/MrBinnacle/skills/issues/418)
retrieved Notion records and failed. The observed identity problem (conflict 1) was a stale
pointer in Notion, and a Notion edit corrected it (see below). The repository needs no mapping
to hold its own facts.

## Knowledge-base entry point for #462

None found in Notion by the searches listed below. **Knowledge Hub** is a whole-workspace
learning hub that covers unrelated domains. The **Skills Library and Global Context** database
describes itself as an inventory and "not the install surface". No Notion page is public, so
none can be linked from a public front door.

The in-repository route stands: [`PRODUCT.md`](../../PRODUCT.md), "Sources and Authority",
which links [Three decisions, and what they share](../explanations/three-decisions.md).
[#462](https://github.com/MrBinnacle/skills/issues/462) can link that page, as the acceptance
item carried over from #445 already says.

Notion searches for the entry point: `Skills Library Global Context`,
`knowledge base entry point skills`, `Knowledge Hub`.

## Corrections after the audit

The audit treated Notion as read-only and left each conflict as an owner's edit. Later on
2026-10-21, under the owner's grant of that day to write the workspace, a correction sheet of
24 rows and 47 edits was applied. The confirming re-fetches ran into 2026-10-22 UTC. The
receipt for those edits is kept outside this repository, because it names private page
identifiers.

| Conflict | State after the corrections |
| --- | --- |
| 1 | The card rows' `Source URL` values point at current card paths. An earlier pass on the same day had made the change, and the correction pass found each value already correct on re-fetch. |
| 2 | `Standing Cost (tok)` is empty on all 14 card rows. Claims ledger C12 stays the source for session cost. |
| 3 | `literal-humanist-voice` has `Lifecycle` = Quarantine, and its free-text field now says no card of that name exists in this repository. Its `Status` still reads Active. The page's own correction record names Draft, so the row is still inconsistent. |
| 4 | The project page now names v3.1.0 (2026-10-17) as the latest Release and the plugin marketplace commands as the install route. It records the #419 product scope as merged on 2026-10-17. Its older dated sections were kept as historical records. |

Four Capability Menu `Skill Path` values were also corrected or cleared, among them the
`azimuth` path. The counts in sections 1 and 2 were not derived again after these edits.
Claims ledger S8 still reads as written on 2026-10-17. This file does not edit the ledger.

## Open items

No new owner decision comes out of this audit. Of the four conflicts, one leaves a residue:
the `Status` value on the `literal-humanist-voice` row (conflict 3). It is a Notion edit and
needs no repository change.
