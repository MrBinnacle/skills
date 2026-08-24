---
"mrbinnacle-skills": patch
---

Repair `click-clirunner-env-none-deletes`: its references rotted, its behaviour claim did not.

A link-check job went red on `github.com/pallets/click/blob/8.1.x/src/click/testing.py` with HTTP 429. The 429 was incidental. Querying the repository directly returned `No commit found for the ref 8.1.x` — the branch no longer exists. Click has moved to 8.5, and all three of this card's `8.1.x` URLs were dead, along with its `click/testing.py:534` line pin.

The behaviour claim survived re-verification. Current stable types the parameter as `Mapping[str, str | None]` on both `CliRunner.invoke` and `CliRunner.isolation`. A value type of `str | None` is the API stating that `None` is a meaningful value rather than an omission, which is the delete; the docs describing `env` as "overrides" is the absent-keys-untouched half. So the card is right and its citations were dead.

Links repointed to `stable` and verified 200. The line-number pin is removed rather than re-derived: a file offset rots on every release, and the signature is the durable citation. A `gotchas.md` records the occurrence and the general rule — a card asserting library behaviour carries two independent claims, what the library does and where you can see it, and the second rots on the library's schedule rather than yours.

Recorded explicitly as **not** an instance of `github-linkcheck-404-throttle-false-negative`: that card covers GitHub answering a throttled request with 404 while the link is alive. Here the complaint was a 429 and the link was genuinely dead. The two look identical in a CI log and separate on one check — asking the API whether the target exists.

A sweep of all 55 external links across the collection found no other dead reference. The remaining non-200 results are placeholders, globs, and a POST-only endpoint.

Version 1.1.0. Not promoted.
