# A plugin is its own root

Status: accepted, 2026-09-21. Resolves [#314](https://github.com/MrBinnacle/skills/issues/314).
Amends [ADR 0002](0002-a-release-is-a-delivery-event.md) on one clause: where each plugin's
version lives. ADR 0002 put it on the marketplace entry; it now lives in the plugin's own
`plugin.json`, which is the first place Claude Code resolves it from. ADR 0002's principal
decision, that a release is the act of delivering changed cards, is untouched.

Each of the collection's three plugins is packaged at its own bucket, `skills/<bucket>/`, with a
`.claude-plugin/plugin.json` that states its name, version and exact skill list, and the
marketplace entry says only where each plugin lives. Until this change every entry pointed at the
repository root and declared its skills in the marketplace file, so `claude plugin eval` loaded an
install as a plugin with no name, no version and no skills. An eval of this collection could
therefore measure nothing and still report a score.

## The evidence, measured

`claude --plugin-dir <root> plugin details <name>` reports the component inventory a plugin
exposes, and costs nothing. Measured on 2026-09-21:

| Root | Manifest | Skills exposed |
| --- | --- | --- |
| a copy of the 2.0.0 install | marketplace only | 0, version `unknown` |
| `skills/engineering/` | `plugin.json`, no `skills` field | 0 |
| `skills/engineering/` | `plugin.json`, three named paths | exactly those three |
| `skills/engineering/` | `plugin.json`, `"skills": "./"` | all ten |

`claude plugin validate` passed every row, so it cannot tell a packaging that loads from one that
does not.

## Considered options

**One shared root whose manifest declares every plugin's paths.** Refused. A root holds one
`.claude-plugin/plugin.json`, so a shared root can describe one plugin, not three.

**Move every card to `plugins/<bucket>/skills/<card>/`, the documented default layout.** Refused.
It would move every card and break every inbound link, `find_cards`, `link-skills.ps1` and the
bucket READMEs, and the measurement shows a declared list loads cards at their current depth.

**`"skills": "./"` instead of an explicit list.** Refused. It would ship any directory dropped
into a bucket with no gate. The explicit list keeps the promotion ritual as it was: a promotion
edits the manifest in the same commit as the `git mv`, and O7 checks both directions.
*Revisit if:* the explicit lists drift from the tree in practice often enough that O7 becomes
routine friction rather than a caught mistake.

## Consequences

The install path changes from a copy of the whole repository to a copy of one bucket. Under
[ADR 0002](0002-a-release-is-a-delivery-event.md) that is a major change. A card's relative link
into another bucket no longer resolves inside an install, so such links now point at the
published repository.

O7 now reads each entry's `plugin.json`, and fails an entry whose `plugin.json` is absent or
unreadable, names a different plugin, or has a source that escapes the repository. A tree that
met O7 before this change fails it now, so the standing obligations move to `conformance v3`
under `SECURITY.md`'s own bump rule. G1 now asserts and stamps the version in each
`plugin.json`.

A bucket's `.claude-plugin/` directory sits at the same depth as its cards, so the card finders
skip dot-named directories at that depth.

Measured on 2026-09-21 by installing the branch's marketplace into a scratch configuration:
each plugin installs as a copy of its bucket alone and exposes exactly its declared skills,
engineering ten, orchestration three and meta one.

*Revisit if:* the tool's discovery rule changes so that nested skill directories load without
declaration, or a marketplace entry's own `skills` list comes to govern what a direct eval run
loads. Either would reopen the one-shared-root option.
