# gotchas — click-clirunner-env-none-deletes (append-only)

- [OBSERVED 2026-06-09] Origin incident, recorded in `SKILL.md` → Example. A filtered-dict
  `env=` in a CLI test left `OPENROUTER_API_KEY` present in `os.environ` during the
  invocation. A model-aware resolver in the system under test rewrote the model id and made a
  live 12-minute API call. The test passed, because the expected assertion string was still
  present in the output from a different code path.

- [OBSERVED 2026-08-23] **The card's own references rotted, and CI is what found it.** A
  link-check job on an unrelated pull request went red on
  `github.com/pallets/click/blob/8.1.x/src/click/testing.py` with HTTP 429. The 429 was
  incidental. Querying the repository directly returned `No commit found for the ref 8.1.x`:
  the branch no longer exists. Click has moved to 8.5, and all three of this card's `8.1.x`
  URLs were dead, along with the `click/testing.py:534` line pin.

  **The behaviour claim survived the re-check; only the pins were stale.** Current stable
  types the parameter as `Mapping[str, str | None]` on both `invoke` and `isolation`, which is
  the published evidence that `None` is a delete rather than an omission. Links repointed to
  `stable`, verified 200. The line-number pin was removed rather than re-derived — a file
  offset is a pin that rots on every release, and the signature is the durable citation.

  **The general rule, and the reason this card is a good example of it:** a card asserting
  library behaviour carries two independent claims — what the library does, and where you can
  see it. The second rots on the library's schedule, not yours, and it rots silently until
  something external checks. Cite a signature or a documented parameter, not a line number,
  and pin to a ref the project keeps alive.

  Not an instance of `github-linkcheck-404-throttle-false-negative`: that card is about
  GitHub answering a throttled request with 404 rather than 429, where the link is alive. Here
  the checker's complaint was a 429 and the underlying link was genuinely dead. The two look
  alike at the CI log and diverge on the one check that matters — asking the API whether the
  target exists.
