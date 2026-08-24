---
"mrbinnacle-skills": patch
---

Every published card now carries a `Dispatches recorded` row — measured demand beside the recurrence evidence, in a row of its own (#106).

The original proposal wrote dispatch counts into the `Occasions counted` row; that is settled against in the repository's first architecture decision record (a dispatch count is fan-out, the specific inflation the admission policy's recurrence criterion refuses). The new row states the lifetime platform-counter figure with its measurement date and its semantics beside the number: demand evidence only — slash and model Skill invocations, summed lifetime, not deduplicated by working occasion, blind to hook-injected and always-loaded firings — never recurrence, lift, or worth. The two trap cards read "No recorded dispatch", never "unused": they enforce through hook mechanisms the counter cannot see. Figures were re-derived from the live counter at build time, not copied from the ticket, whose figures were eight days stale. Summed-lifetime was chosen over per-session dedup because the counter predates the per-session delta log, so a lifetime dedup figure is not derivable; the reason is recorded beside each row.

The card-contract checker now requires the row on every published card and checks its form — an integer or the exact phrase "No recorded dispatch" at the opening, and a measurement date present — each with its own failing control. Every card's `Occasions counted` row is byte-identical before and after, verified by an additive-only diff.
