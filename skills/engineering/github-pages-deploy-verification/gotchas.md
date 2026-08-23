# gotchas — github-pages-deploy-verification

## [ANTICIPATED]

- **Regional CDN edges serve different content.** Your poll loop can see the new content while a
  user behind a different edge still gets the old page. The loop proves origin propagation, not
  global propagation — for launch-critical changes, re-check after a few minutes.
- **HTML minification/rewriting breaks exact-string markers.** Pages pipelines (Jekyll, asset
  bundlers) can reorder attributes or strip whitespace so your diff line never appears verbatim
  in the served HTML. Pick markers from visible copy or CSS values, not from markup structure.
- **`grep -q` on a compressed response.** If you add `-H "Accept-Encoding: gzip"` (or a proxy
  does), the body is binary and the grep silently never matches. Plain `curl -s` without encoding
  headers is what the pattern assumes.
- **A cached 404 also polls forever.** If the site itself failed to build, an unbounded loop spins
  on the missing marker with no error. The published procedure now caps attempts, records HTTP
  errors, and checks build status only at the cap to produce a non-success reason.

## [OBSERVED]

*(Append observed gotchas here as they surface. Do not delete entries — gotchas are
stress-test signal.)*

- **2026-05-27 / azimuth repo (public):** poll predicate `case-footnote` matched pre-deploy
  content — the selector already existed, only its `color` value changed in the commit. Loop
  exited instantly on stale content; verification was a false positive. Re-picked marker to a
  brand-new declaration (`overflow-x: auto`) introduced in the same commit; loop then waited
  ~30s and exited on genuinely new content.
- **2026-05-27 / same session:** `sleep 35 && curl ...` chain blocked by the Claude Code Bash
  harness ("Blocked: sleep N followed by:"), cancelling parallel tool calls. Replaced with the
  until-loop pattern; harness accepts a short `sleep` inside a check loop.

- **2026-08-23 / discriminator run (rotation pass, step 2):** This card had never been
  model-invoked across 261 tracked startups, so the retrieval-vs-insurance discriminator ran: a
  corpus sweep of the maintainer's three tracked clones (all `.md` surfaces, including session
  checkpoint archives; raw transcripts and the private archive not swept) found **zero trap
  occurrences outside the 2026-05-27 founding incident**. Diagnosis: **insurance** — the
  situation has not recurred, no deterministic guard covers it, and non-invocation says nothing
  about the card's worth (consistent with its `CANT_TELL_YET` screen shape).
