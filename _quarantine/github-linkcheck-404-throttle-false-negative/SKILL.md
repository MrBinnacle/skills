---
name: github-linkcheck-404-throttle-false-negative
description: |
  Diagnose CI link-checker (lychee and similar) failures reporting 404 on
  github.com issue/PR URLs that actually exist. Use when: (1) a link-check job
  goes red on `https://github.com/<owner>/<repo>/issues/<n>` links, (2) `gh api
  repos/<owner>/<repo>/issues/<n>` returns the issue fine, (3) the same check
  passed recently with no doc changes, (4) other unrelated CI jobs fail at the
  same time. GitHub throttles anonymous HTML page requests with 404 (not 429),
  which a checker cannot distinguish from a dead link; platform outages produce
  the same signature repo-wide.
author: Claude Code
version: 1.0.0
date: 2026-08-17
---

# GitHub Link-Check 404-Throttle False Negative

## Problem

Link checkers hit github.com issue/PR pages anonymously. GitHub's anti-scraping
throttle answers some of those requests with **404, not 429** — so a checker
configured to tolerate rate limits (`--accept 200,206,429`, the common lychee
setup) still reports a hard "dead link" on a URL that resolves fine in a browser
or via the API. During a GitHub platform incident the same false-404s appear
repo-wide at once.

## Context / Trigger Conditions

- CI job red with lines like:
  `[404] https://github.com/<owner>/<repo>/issues/47 | Rejected status code: 404 Not Found`
- The links are same-forge issue/PR URLs, often many at once.
- The failing files were not touched by the change under test.
- Bonus tell for the outage variant: a second unrelated job (CodeQL, actions
  analysis) fails in the same run, or the Actions API itself returns 503.

## Solution

1. **Verify the links via the API, not the page**:
   `gh api repos/<owner>/<repo>/issues/<n> --jq '.number,.state'` — if this
   returns, the link is alive and the 404 is throttle/outage noise.
2. **Check platform status before diagnosing the repo**:
   `curl -s https://www.githubstatus.com/api/v2/status.json` — an `indicator`
   of `major`/`critical` explains everything at once; stop repo-side diagnosis.
3. **Re-run the failed job after the throttle window / incident passes**:
   `gh run rerun <run-id> --failed`. Note: a rerun is refused while the workflow
   is still `in_progress`, and returns 503 during an outage — wait for terminal.
4. **Durable hardening (apply on clean evidence only)**: give the checker an
   authenticated path for github.com links — lychee reads `GITHUB_TOKEN` and
   uses the API instead of anonymous HTML requests. Do not ship this change
   during/just after an outage window: the evidence that motivated it is
   contaminated, and you cannot tell hardening from coincidence when it "works".

## Verification

The re-run goes green with zero content changes, and `gh api` confirmed each
flagged issue exists. If the check stays red on a quiet platform with the token
wired, THEN treat the links as genuinely suspect.

## Notes

- Never mass-edit or remove issue links on the strength of a checker 404 alone —
  that converts a false negative into real information loss.
- The two-unrelated-jobs-failing-at-once pattern generalizes: check
  githubstatus.com before any surprising CI diagnosis.

## References

- lychee GitHub token support: https://github.com/lycheeverse/lychee (README,
  `--github-token` / `GITHUB_TOKEN`)
- GitHub status API: https://www.githubstatus.com/api
