---
name: meta-fixture-card
description: fixture
disable-model-invocation: true
---

> **Normative status.** The admission policy is `ADMISSION.md`
> (`admission-policy v1`). This skill is the reference method for answering it —
> not the binding rule.

# meta-fixture-card

fixture: the card pins v1 and ADMISSION.md declares v1, deliberately. They MUST
agree in this tree. This fixture isolates the origin-tier assertion, so it has
to be unable to fail on version drift or on the scoreboard counts — that case
has its own fixture, `measured-drift`. Do not "restore" a mismatch here.

The `admission-version-drift` fixture that used to cover policy-version drift was
removed with the gate card on 2026-08-31 (#178): the drift it planted was between
ADMISSION.md and the gate card's header, and there is no longer a card holding a
second copy of the version to drift from.
