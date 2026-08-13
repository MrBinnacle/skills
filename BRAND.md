# BRAND.md — voice and positioning for `MrBinnacle/skills`

**Word lists live in [`assets/tokens.json`](assets/tokens.json)** (`copy.words_to_prefer`,
`copy.words_to_avoid`, its scope rule, and the rejection checklist). Read them there. This file
carries the voice itself, which no JSON can hold.

**Two different things live in this file, and they are sourced differently.**

*Positioning and register* — what the repository claims, which surface takes which tone — is a
description of the shipped files. Those files outrank it: `README.md`, `ADMISSION.md`,
`RETIRED.md`, each skill's `EVIDENCE.md`. Where this file and they disagree, they win, and this
file wants fixing.

⛔ *Voice* is **not** sourced that way, and must never be again. It comes from
[`VERBATIM.md`](VERBATIM.md), the record of lines the owner actually wrote, and a shipped surface
cannot supply it. The reason is in that file: the front page once opened with generated copy in
his voice, and this file read it off the page and promoted it to the establishing example of how
he writes. A page cannot be its own provenance. `scripts/validate_voice_provenance.py` fails the
build if a voice specimen here loses its citation or picks one up from a shipped surface.

⛔ **The owner writes the public lines.** An agent drafts candidates and labels them as
candidates. Approving your own copy onto a public surface is outside your authority, and this
constraint is the reason the file exists.

**A line ships when the checklist reads *no* on every item, every number in it resolves to an
artifact you opened, and the owner has picked it.**

---

## Polish

The failure mode of every rewrite, and the owner's own name for it — checklist item 10: *"Does
the copy sound more polished but less like Matthew?"*

Polish is the default direction of any edit an agent makes. Smoothing is what models do. So the
bar is inverted here: **a draft that reads smoother than the README is off-voice regardless of
how good it is.** Catching yourself smoothing a line is the signal to put the rougher version
back.

Polish is the verbal form of *dressing* (see [`DESIGN.md`](DESIGN.md)): both make a limitation
look like a claim. Hunt for it first.

---

## What the repository claims

That you can see where each card came from, what it does when it runs, and what has and has not
been tested about it. Nothing beyond that.

What it declines to claim, in the README's own words: *"If you came here for a collection that
says its skills are proven, this one will disappoint you on purpose."*

It competes on whether the record holds up when someone opens it. Skill marketplaces and prompt
packs compete on quantity and reach — **a comparison that makes this collection sound larger is
a comparison working against it.** Keep the frame on the record.

---

## Voice

**The rule: a voice specimen is a line the owner wrote or ratified, cited to
[`VERBATIM.md`](VERBATIM.md).** Provenance is a property of the line, not of the surface it
appears on. A specimen that cannot be cited is removed rather than left uncited — an uncited line
is indistinguishable from copy an assistant wrote, which is how this section went wrong the first
time.

⛔ **Read the specimens as typed.** The record keeps double spaces, missing apostrophes and
trailing hedges on purpose, and they are reproduced here unchanged. **The roughness is the
provenance** — it is the first thing an editing pass removes and the last thing a generated
sentence contains. Smoothing a quote to fit your sentence destroys the evidence. Change your
sentence.

**First person, singular, and the problem is his.** The account starts with a question he had,
not with a market.

> I wanted to know if you could tell if a skill was good. Etc and so forth. Expand expand expand.
> And then this happened.

Source: [`VERBATIM.md`](VERBATIM.md), *On how it started*, 2026-08-12.

**The unflattering reading goes first, hedge included.** He reaches for the deflating word about
his own work before anyone else can, and does not resolve the hedge.

> It's just - the most successful mistake of mine so far. I think..maybe

Source: [`VERBATIM.md`](VERBATIM.md), *On what it amounts to*, 2026-08-12.

**Method described as a rate, not a virtue.** The claim is about iteration speed against an error
rate he states plainly. Never the word *rigorous* — wrong a lot, fast enough to recover.

> Im wrong  like 200x a day - but i can iterate in really cool ways fast enough to cancel out the
> wrongness

Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.

**Substance before surface, said as the order the work happened in.**

> All of the cosmetic/aesthetic/frontend stuff - as you've noticed - has waited until after I've
> figured out if there's something to put wrapping paper on

Source: [`VERBATIM.md`](VERBATIM.md), *On the order the work happened in*, 2026-08-12.

**Points at the record rather than asking to be believed.** Short, flat, checkable.

> Follow the time stamps.

Source: [`VERBATIM.md`](VERBATIM.md), *On how it started*, 2026-08-12.

**Names the failure as what it is, including on his own page.** No softening of the word, no
distancing from having shipped it.

> I'm taking that line out first thing. I never "just kept adding skills…" that was ai slop that I
> just allowed while I was focusing on skill harness

Source: [`VERBATIM.md`](VERBATIM.md), *On the line that used to be on the front page*, 2026-08-12.

### What carries across the specimens

**Concrete, with the number attached.** The actual run counts, the actual model name, the link to
the pre-registration. Where a number cannot be attached, rewrite the claim or drop it.

**Short declaratives. Sentence case.** Long sentences appear when the thought is genuinely long.

**Hedges earn their place only where the uncertainty is real**, and then name the uncertainty
rather than gesturing at it. The record hedges — see the trailing hedge on the second specimen
above — and it is kept rather than tidied, because it is doing work.

⚠ **Prose in this section must not use double quotes.** A quoted span here is refused rather than
checked, because inline italics are the exact form the unsourced specimens took. Restructure, or
name the phrase in italics without quoting it.

⚠ **What this section deliberately does not do.** It does not tell you whether a draft *sounds*
like him. No file can, and `validate_voice_provenance.py` does not try — it checks citations, not
resemblance. Judging resemblance is the owner's, or `/t1-review`'s tier.

### Register by surface

| Surface | Register |
|---|---|
| README, repository description, social card | Plain first person. Shortest true version. |
| `ADMISSION.md`, `AGENTS.md`, skill cards | Technical and procedural. Precision over warmth. |
| `EVIDENCE.md` | Flat and factual. Dates, methods, verdicts. Adjectives stay off results. |
| `RETIRED.md` | Matter-of-fact. A retirement is the process working, written without apology or triumph. |

---

## The name

**`MRBINNACLE / skills`** — construction in `tokens.json > wordmark`.

A binnacle is the housing that keeps a ship's compass readable and correct: it holds the
instrument steady and corrects for the iron around it. That is the whole metaphor, and it is why
[`DESIGN.md`](DESIGN.md) bans the nautical iconography — the maritime reading is a surface pun
that trades the idea for a picture.

**Leave the metaphor unexplained in public copy.** A name that needs a gloss on the card has
already failed, and the explanation reads as a pitch against a collection whose whole posture is
the opposite.

---

## Words

Lists and scope: `tokens.json > copy`. Three notes there carry conditions worth knowing before
you draft — `earn`, `robust`, `production-ready`.

The origin is worth carrying here because it is why the list exists: the retired tagline *"skills
that have to earn their keep"* was cleared from three text surfaces and survived on
`assets/social-preview.png` — the one surface a stranger sees before clicking.

**What the list reaches:** recurrence of an exact retired phrase.
**What it does not:** a rephrase in the same spirit. *"Has to prove its keep"* passes clean.
Closing that needs a human or cross-model read against intent, which is `/t1-review`'s tier, not
a string match's. *Revisit if:* a rephrase gets through — that is the signal the list needs the
judgment layer rather than more entries.

---

## Evidence rules

`tokens.json > evidence_rules`, and they are the non-negotiable four. The one an agent breaks
most easily: **counts on a rendered asset are regenerated from live repository state before
export** (`social_preview.counts_rule`). A count baked in months ago goes false the moment the
collection changes, and it goes false silently.

---

## Open decisions

The owner's, carried so they do not lapse.

- **The social card's primary line.** Candidates exist and were independently reviewed. None is
  recorded here — writing one in would make it the default by inertia. *Revisit if:* the owner
  selects one, at which point it lands here as the recorded line.
- **Whether a public project page should exist**, and what it would say. *Revisit if:* the owner
  opens it.

---

*Visual system: [`DESIGN.md`](DESIGN.md). Values: [`assets/tokens.json`](assets/tokens.json), kit 0.1.*
