# BRAND.md — voice and positioning for `MrBinnacle/skills`

**Word lists live in [`assets/tokens.json`](assets/tokens.json)** (`copy.words_to_prefer`,
`copy.words_to_avoid`, its scope rule, and the rejection checklist). Read them there. This file
carries the voice itself, which no JSON can hold.

The shipped surfaces outrank this description of them — `README.md`, `ADMISSION.md`,
`RETIRED.md`, each skill's `EVIDENCE.md`. What follows was read off those files. Where it and
they disagree, they win, and this file wants fixing.

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

Read from the shipped surfaces, with the line that establishes each.

**First person, singular, owning the problem.** *"I kept adding skills to my assistant and I
never removed any."* There is an author with a problem, and he says so.

**The uncomfortable thing goes first.** *"The uncomfortable part first, because this is the part
a README usually buries."* Structure follows honesty rather than persuasion.

**Concrete, with the number attached.** The actual run counts, the actual model name, the link to
the pre-registration. Where a number cannot be attached, rewrite the claim or drop it.

**Plain analogy for the reader who does not know yet.** *"A skill is a small instruction file —
think of it as a recipe card pinned above the stove."* Explain without softening what follows.

**The reader's real question, in their words, answered straight.** *"Is it safe to install
these?"* then *"Plainly:"* — including the part that is not reassuring.

**Short declaratives. Sentence case.** Long sentences appear when the thought is genuinely long.

Hedges earn their place only where the uncertainty is real, and then name the uncertainty rather
than gesturing at it.

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
