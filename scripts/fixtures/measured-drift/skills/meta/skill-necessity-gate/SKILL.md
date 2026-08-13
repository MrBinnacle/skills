---
name: skill-necessity-gate
description: fixture
disable-model-invocation: true
---

> **Normative status.** The admission policy is `ADMISSION.md`
> (`admission-policy v1`). This skill is the reference method for answering it —
> not the binding rule.

# skill-necessity-gate

fixture: the card pins v1 and ADMISSION.md declares v1, deliberately. They MUST
agree in this tree. This fixture isolates the measured assertion, so it has to
be unable to fail on version drift — the drifted-version case is its own fixture,
`admission-version-drift`. Do not "restore" the mismatch here.
