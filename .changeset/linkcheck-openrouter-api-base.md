---
"mrbinnacle-skills": patch
---

`links.yml`: exclude the OpenRouter API base path from the link check, because it is correct rather than broken.

`https://openrouter.ai/api/v1` appears in `_quarantine/anthropic-sdk-via-openrouter/SKILL.md` as the value of a `base_url=` argument inside the frontmatter description. It is an API base that client code concatenates a route onto. A bare GET against it returns 404 by design. Measured 2026-09-06: `curl` returns 404 deterministically, not intermittently.

lychee extracts the URL from inside the quoted argument and cannot distinguish an API base from a dead page, so the job exited 2 on skills#239 — a pull request that changed only `AGENTS.md` and touched nothing under `_quarantine/`.

The alternative was to rewrite the card. That would change a documented constructor argument into something a reader cannot copy, trading a working example for a green light.

The exclusion is anchored with `^...$` to that exact path. A 404 anywhere else on openrouter.ai still fails the job. It follows the pattern already set in this workflow by the `docs/design/variants` exclusion, whose comment makes the same argument: the links there are correct, and rewriting them to satisfy the checker would corrupt the artifact.

This matters beyond one red job. A check that goes red for a reason unrelated to the change trains a reader to merge past it, and the next genuinely broken link arrives in the same colour.

Recorded as skills#240.
