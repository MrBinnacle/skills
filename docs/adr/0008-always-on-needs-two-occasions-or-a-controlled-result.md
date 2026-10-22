# Always-on needs two occasions or a controlled result

Status: accepted, 2026-10-20. Applies the maintainer's ruling on
[#547](https://github.com/MrBinnacle/skills/issues/547#issuecomment-6305476405). Prices one new
kind of change under the rule [ADR 0005](0005-the-install-route-is-what-a-consumer-resolves.md)
states, and leaves ADR 0002, ADR 0003, ADR 0005 and ADR 0007 untouched.
[`ADMISSION.md`](../../ADMISSION.md) is untouched too, and its version does not bump: this ADR
governs how an admitted card loads, not which cards are admitted.

## What happened

Every installed card that does not set `disable-model-invocation: true` puts its description
into every session. Claude Code's documentation states it: by default the "Description [is]
always in context", and with `disable-model-invocation: true` the "Description [is] not in
context, full skill loads when invoked" (`https://code.claude.com/docs/en/slash-commands`,
"Control who invokes a skill", read 2026-10-20). The `/context` measurement in
[#361](https://github.com/MrBinnacle/skills/issues/361#issuecomment-6304133476) put that at about
70 to 80 tokens per card per session on Claude Code 2.1.305.

Before this ADR, the only rule for that choice was the topology rule in
[`AGENTS.md`](../../AGENTS.md) → "Authoring conventions". It asks who does the strategic
thinking, and it says nothing about evidence. Eleven of the fourteen published cards loaded in
every session. Five of those eleven had one counted occasion.

The maintainer's second critique on #547 (2026-10-20) named the cost: "Paying 70–80 tokens per
session for origin-trace items is the part that makes careful outsiders walk away." The ruling:
"If a card has one counted occasion and no controlled result, it does not belong in the
always-loaded set. Either raise the bar for always-on or move the thin cards to by-hand /
quarantine until they clear it."

## Decision

**A published card is always-on only when it clears the always-on bar. A card clears the bar
when its `EVIDENCE.md` counts two or more occasions, or when it carries a controlled result.
Below the bar, the card ships by hand.**

The two terms are read from fields every published card already carries. This ADR adds no
evidence type.

- **Counted occasion.** The integer that opens the card's `Occasions counted` row. That row is
  `ADMISSION.md` criterion 2 in the card's own file: independent occurrences, counted after the
  fact, with fan-out from one run counted once ([`AGENTS.md`](../../AGENTS.md) → "Recording a new
  occurrence", step 3). `scripts/validate_card_files.py` already requires the integer to equal
  the dated references in the row and each date to be recorded elsewhere in the card. The bar
  is two, the same `INDEPENDENT_OCCASIONS` threshold below which the card must carry the
  `RECURRENCE-THIN` label. "More than one counted occasion" is two or more.
- **Controlled result.** A `Screen result` or `Paired verdict` row that opens with a verdict
  other than `UNMEASURED`: one of `KEEP`, `CUT` or `CANT_TELL_YET`
  (`scripts/validate_scoreboard.py`, `CONTROLLED_FIELDS` and `MEASURED_VERDICTS`). This is the
  definition [`CATALOG.md`](../../CATALOG.md) already uses. Its "Evidence records" table defines
  `CONTROLLED` as "A defined with-and-without evaluation produced a result", and its card
  evidence table marks such a card `measured`. One predicate,
  `validate_scoreboard.carries_controlled_result`, decides both the `measured` posture and this
  bar, so they cannot disagree.

**Currency is not part of the bar.** Whether a receipt still disposes anything, for example after
a card's bytes change and its receipt's `skill_id` stops matching, is conformance obligation O5's
judgment. O5 needs a skill-harness checkout to make it, and CI's card check does not have one.
That judgment governs re-screening and retirement, not how a card loads.

**By hand** means the card's `SKILL.md` frontmatter sets `disable-model-invocation: true`. On
Claude Code the model cannot invoke the card on its own, and its description is not loaded. The
user runs it by name: `/<plugin>:<card>` for a plugin install, such as
`/mrbinnacle-engineering:clirunner-env` (the namespaced form is in
`https://code.claude.com/docs/en/plugins/create`, read 2026-10-20). The key is a Claude Code
key, as `AGENTS.md` → "Where this repository diverges from the Agent Skills specification"
records. Its effect on another host is unmeasured here.

**A card moves back when it clears the bar.** A card that records its second counted occasion,
or gains a controlled result, may drop the key and become always-on again. Clearing the bar
makes always-on allowed, not required. The topology rule still decides: `im-down` counts two
occasions and stays by hand, because it is a procedure with side effects.

**Moving a card from always-on to by hand is a major change.** ADR 0005's decision sentence
says that a change is major "only when an installed user who takes no action loses something
they had, or must act to keep it". A user who takes no action loses a card that fired on its
own, and must now invoke it to keep its effect. The card's name and files do not change, so
nothing else tells that user what happened. The major number is the warning.

**Moving a card from by hand to always-on is a minor change.** The user loses nothing they
had. They begin to pay the card's description cost, as they do when a card is admitted, and
admitting a card is minor under ADR 0002 and ADR 0003.

## The split this ADR applies, read 2026-10-20

| Card | Occasions counted | Controlled result | Before | After |
|---|---:|---|---|---|
| `clirunner-env` | 1 | none | always-on | by hand |
| `mocked-stub` | 1 | none | always-on | by hand |
| `stale-deploy` | 1 | none | always-on | by hand |
| `decision-rights` | 1 | none | always-on | by hand |
| `pull-rebase` | 1 | `CANT_TELL_YET` | always-on | always-on |
| `halt-as-deliverable` | 3 | none | always-on | always-on |
| `pretooluse-prose` | 12 | none | always-on | always-on |
| `vacuous-check` | 8 | none | always-on | always-on |
| `dead-predicate` | 5 | none | always-on | always-on |
| `disposition-schema` | 3 | none | always-on | always-on |
| `subagent-handback` | 7 | none | always-on | always-on |
| `closure-mode` | 1 | none | by hand | by hand |
| `im-down` | 2 | none | by hand | by hand |
| `im-up` | 1 | none | by hand | by hand |

"None" means both controlled fields read `UNMEASURED (mechanical_vacuous)`. The table is a
snapshot of the records on that date and is not maintained. The cards' own `EVIDENCE.md` rows and
frontmatter are the live state, and `validate_card_files.py` checks them.

**Why `pull-rebase` stays always-on.** It counts one occasion, so it clears the bar only on a
controlled result, and it has one. Its `Screen result` and `Paired verdict` rows both open with
`CANT_TELL_YET`, from paired with-and-without runs
([`skills/engineering/pull-rebase/EVIDENCE.md`](../../skills/engineering/pull-rebase/EVIDENCE.md),
lines 12 and 13). Its `Paired verdict` receipt is stale (`card_hash_mismatch`), which is the
currency judgment this ADR leaves to O5.

The same record carries the collection's only measured effect of a card's always-loaded
description. Its `Description channel` row (line 17 of that file) records a paired micro-run on
2026-09-01: k = 8, subject `claude-sonnet-4.5` through OpenRouter, one harness pin for both arms,
on a task with `pull.rebase=true` and diverged local and remote branches. The bare arm, with no
card present, rebased in all 8 epochs and rewrote the planted commits. With the card mounted,
the agent changed its `git` command in 6 of the 8 paired epochs. The 6 of 8 counts discordant
pairs, where the treated epoch avoided the rebase and its bare partner did not; the other 2
treated epochs still rebased. Across the 8 treated epochs the description was present 8 times,
the Skill tool was called 0 times and the body was read 0 times, so the one-line description
carried the change. The Jeffreys 95% interval on discordance is [0.408, 0.944]. That run's own
verdict is `CANT_TELL_YET` (underpowered), and its subject is not the registered direct-Anthropic
subject. It was not replicated: the sized n = 32 run on `claude-sonnet-5` on 2026-09-03 met no
`git pull` in either arm. It is not evidence that the card works, and this ADR does not claim
that. It is the one record that loading a description changed what an agent did.

## Why by hand and not quarantine

The ruling allowed either. By hand is the better fit for a card that is admitted but thin.

- **Installed users keep the card.** A by-hand card stays in its plugin. The user still has its
  name, its body, its recipes and its evidence, and can run it in one command. Moving a card to
  `_quarantine/` takes it out of the plugin, so on the next update every installed user loses
  it. That is a retirement in all but name, and it would need to run through ADR 0007's staged
  exits.
- **Quarantine is the admission axis.** `_quarantine/` holds candidates that have not been
  admitted. These cards were admitted under `admission-policy v1`. The bar concerns what they
  cost in each session, not whether they belong in the collection, and a load-mode question
  should not reopen admission.
- **The move is reversible in one line.** Taking the key out of the frontmatter puts a card back
  in the always-on set. A return from quarantine is a promotion, with the whole promotion pass.

The evidence does not argue for quarantine. None of the four cards has a record that it failed
or did harm. Each has a record that says little.

## Considered and rejected

**Quarantine the four cards.** Rejected for the reasons above.

**Read "controlled result" as an effect shown, that is, a `KEEP` receipt.** Under that reading
no published card has a controlled result, so `pull-rebase` moves to by hand as well. Rejected
for three reasons. The ruling's words are "no controlled result", and `CANT_TELL_YET` from a
paired run is a controlled result under the collection's own definition. The reading would make
the bar judge the verdict, which the bar does not need to do. And it would take the
always-loaded description off the one card whose description has a measured effect.

**Read "controlled result" as a current receipt only.** Rejected because currency is O5's
judgment and needs a skill-harness checkout, which the card check does not have. A bar CI
cannot evaluate is a bar nobody enforces.

**Price the move to by hand as minor, as retirement is priced.** ADR 0002 keeps retirement minor
so that the major number does not grow every time the collection removes a card on evidence.
Rejected for this move, for two reasons. A retired card disappears from the user's plugin, and
the user can see that. A by-hand card stays in place and stops firing, and the user cannot see
that without the version number. And the inflation risk is small: occasions only grow, so a card
falls below the bar only when it is admitted thin, and this ADR applies the bar to the whole set
once.

## Consequences

- Four cards ship by hand: `clirunner-env`, `mocked-stub`, `stale-deploy` and `decision-rights`.
  Each card's `Standing cost` row now states the zero form and the reason, and
  `scripts/standing-costs.json` is refreshed.
- `scripts/validate_card_files.py` refuses a model-invocable card below the bar, with rule kind
  `always_on_bar`. The rule reads one way only: it does not refuse a by-hand card that clears the
  bar.
- The release that carries this change is major. With no other pending major changeset, the
  next release becomes 4.0.0, not the 3.1.1 that
  [#462](https://github.com/MrBinnacle/skills/issues/462) planned "if the name stays".
- An adopter whose own environment tells the model to call one of these cards through the Skill
  tool, for example a prompt hook that says to call `decision-rights` before a handoff, now gets
  a refused call on Claude Code. The documentation states it: "If Claude tries anyway, Claude
  Code blocks the call". A guard on the tool call is unaffected. The changeset tells installed
  users what to do.
- Release gate G10 does not yet see a change of load mode. It prices a diff that touches a card
  as at least a patch, so it accepts the major declared here but would not refuse a minor one.
  A gate case that reads the price sentence above belongs in its own change.

## Decision status

- **Non-negotiable:** that a card with one counted occasion and no controlled result is not
  always-on. The ruling is the maintainer's, taken 2026-10-20 on #547.
- **Revisable with new evidence:** reading "controlled result" as any result other than
  `UNMEASURED`. *Revisit if:* the maintainer rules that it means an effect shown, a `KEEP`
  receipt. Then `pull-rebase` moves to by hand, and `always_on_bar_breaches` reads the
  `Evidence scope` row's `KEEP` forms instead of the controlled fields.
- **Revisable with new evidence:** leaving currency out of the bar. *Revisit if:* a card clears
  the bar only on a receipt that O5 reports stale for two consecutive rotation passes. That would
  show a stale result keeping a card always-on with nothing current behind it.
- **Revisable with new evidence:** by hand rather than quarantine. *Revisit if:* a by-hand card
  records no dispatch and no new occasion across two rotation passes. That would show the card
  is not invoked by name either, and the withdrawn-on-the-policy route in ADR 0007 would then
  fit better.
- **Revisable with new evidence:** the major price for the move to by hand. *Revisit if:* a
  later application of the bar would make two major releases in one quarter. The inflation
  argument against this price would then hold in fact.

## Amendment, 2026-10-21: the `pull-rebase` citation and the currency Revisit-if

This append comes from [#562](https://github.com/MrBinnacle/skills/issues/562). It rewrites no
text above. It records the maintainer's ruling of 2026-10-21, "no, keep pull-rebase always-on"
([ruling](https://github.com/MrBinnacle/skills/issues/562#issuecomment-6321625802)), and the
amending note that ruling asks for, as the
[adjudication](https://github.com/MrBinnacle/skills/issues/562#issuecomment-6321225641) described
it. `pull-rebase` stays always-on.

**The citation was wrong for one row.** "Why `pull-rebase` stays always-on" above says that the
card's `Screen result` and `Paired verdict` rows both open with `CANT_TELL_YET` "from paired
with-and-without runs". That is wrong for the `Screen result` row. The card's
[`EVIDENCE.md`](../../skills/engineering/pull-rebase/EVIDENCE.md) records that screen as
superseded on 2026-09-01, because only its Null arm ran. The `Paired verdict` row alone supplies
the controlled result the bar needs, so the card still clears the bar.

**No current receipt matches the bytes that ship.** The bar does not require one. By the
maintainer's ruling, a controlled result does not have to have been measured on the `SKILL.md`
that ships now to count toward the always-on bar. This is the Decision's "Currency is not part of
the bar", applied to this card.

**The currency Revisit-if is reworded so that it can fire.** Under Decision status above, it
reads: "*Revisit if:* a card clears the bar only on a receipt that O5 reports stale for two
consecutive rotation passes." As written it cannot fire for this card. O5 reports PASS for
`pull-rebase`, because the card's row already marks its receipts as not current, so O5 never
reports that receipt stale again. The reworded clause below replaces it.

- **Revisable with new evidence:** leaving currency out of the bar. *Revisit if:* a card clears
  the bar only on a controlled result, and a rotation pass finds no receipt whose `skill_id`
  equals the sha256 of the card's shipping `SKILL.md`, for the second consecutive pass. For
  `pull-rebase`, the rotation pass of 2026-09-30 was the first, so the next rotation pass is the
  second. Or the maintainer rules currency into the bar. Firing reopens the currency question; it
  does not by itself move a card to by hand.
