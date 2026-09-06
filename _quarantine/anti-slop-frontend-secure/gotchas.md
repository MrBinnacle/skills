# gotchas — anti-slop-frontend-secure (append-only)

- [OBSERVED 2026-08-09] Origin incident. A single-file HTML dashboard artifact produced by a
  frontier model (Claude) contained three security defects caught by manual code review:
  (1) `innerHTML` used for DOM construction instead of safe `createElement`/`textContent`
  patterns; (2) an unapproved connection to `plausible.io` analytics embedded in a `<script>`
  tag; (3) an API key (`sk-proj-...`) committed in a `<script>` tag that was about to be
  pushed to a public repository. No automated oracle existed at the time — the defects were
  caught by a human reviewer before deployment. The incident was the trigger for building
  this card's deterministic oracle.

- [ANTICIPATED] False positive on minified JavaScript containing sink-like substrings.
  A minifier may produce identifiers containing `innerHTML` as a substring (e.g.,
  `getinnerHTMLById`). The oracle's word-boundary regex (`(?<![a-zA-Z0-9_$])innerHTML(?![a-zA-Z0-9_$])`)
  mitigates this, but a minifier that concatenates without boundaries could still trigger it.
  Mitigation: run the oracle on the unminified source, not the build output.

- [ANTICIPATED] External host allowlist must be declared per-artifact. The oracle's
  `--allowlist` flag is the mechanism. Forgetting the flag means the default empty allowlist
  blocks everything, which is the safe default but may surprise a user who expects `fonts.googleapis.com`
  to be allowed. The error message names the blocked host, which is the shortest path to
  adding the flag.
