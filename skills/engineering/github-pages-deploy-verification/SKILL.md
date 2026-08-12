---
name: github-pages-deploy-verification
description: Verify a GitHub Pages (or any CDN-fronted) deploy actually serves new content. Poll on a marker that did not exist pre-deploy; avoid sleep-and-curl chains the agent harness blocks.
---

# GitHub Pages deploy verification

## Problem

Three failure modes when verifying that a deploy is live via `curl`:

1. **False-positive poll predicate.** Polling `until curl ... | grep -q "<selector>"; do sleep; done`
   succeeds instantly if the selector existed before the deploy too. The loop exits on the OLD
   content; you think you've verified the new state and you haven't.

2. **Blocked timing chain.** `sleep 35 && curl ...` looks reasonable but the Claude Code harness
   blocks long leading sleeps inside Bash to prevent dead polling. Worse, even short
   `sleep N && curl` followed by additional pipes can hit "Blocked: sleep N followed by:" errors
    that cancel parallel tool calls.

3. **Unbounded failure.** A missing marker can mean a slow deploy, failed build, HTTP error, or
   stale content. An endless loop distinguishes none of them and cannot return a useful verdict.

The first two bugs hit one session inside ~30 minutes. They are not in the same family but ride the
same task.

## Context / Trigger Conditions

Any of:

- About to push to a branch where merge = production deploy (GitHub Pages legacy mode, Netlify
  Git, Vercel Git, etc.)
- The platform's own deploy-status API is known to lag (e.g., `gh api repos/.../pages/builds/latest`
  can report stale `building` long after content is live, or report `built` before the CDN
  catches up)
- A task isn't "done" until you've confirmed the new HTML/CSS/JS is served, not just merged

## Solution

### Pick the poll predicate correctly

The string you grep for **must be content that did not exist pre-deploy**. Concretely:

- ✅ Grep for a new CSS rule, new class, new token value, new copy string, new commit hash
  echoed in a meta tag.
- ❌ Grep for an element selector (`.case-footnote`, `<h1>`) that already shipped — the loop
  exits on the cached old content.
- ❌ Grep for a token name (`--accent-dim`) when only its *value* changed — the name was there
  before too.

Rule: `git diff HEAD~1 -- . | grep '^+'` produces candidate strings from every changed path.
Pick one unique to the diff and likely to survive the site's build transformations.

### Avoid blocked timing chains

In Claude Code's Bash tool, do not write:

```bash
sleep 35 && curl ...    # often blocked
```

Use a bounded function. Replace `deploy_status` with the platform's build-status command; it must
print `built` only for a successful build. The status call runs only after all attempts, so a live
deploy makes no extra API call.

```bash
poll_deploy() {
  url=$1 marker=$2 max_attempts=${3:-24}; attempt=1; saw_http_error=false
  while [ "$attempt" -le "$max_attempts" ]; do
    body=$(curl -fsS "$url") && {
      case $body in *"$marker"*) echo "LIVE: new content served"; return 0;; esac
    } || saw_http_error=true
    [ "$attempt" -eq "$max_attempts" ] || sleep 5
    attempt=$((attempt + 1))
  done
  status=$(deploy_status 2>/dev/null || printf unknown)
  if $saw_http_error; then echo "HTTP FAILURE: site returned an error (build: $status)" >&2
  elif [ "$status" = built ]; then echo "STALE CONTENT: build succeeded but marker is absent" >&2
  else echo "TIMEOUT: deploy did not complete (build: $status)" >&2; fi
  return 1
}
```

This stable contract is: bounded attempts, four named outcomes, zero only for `LIVE`, and build
status deferred until the bound. The command used for `deploy_status` and the attempt count are
adopter-specific.

**Pattern A — synchronous until-loop with a check command:**

```bash
poll_deploy "https://your.site/" "<new-content-marker>" 24 &&
  curl -fsS "https://your.site/" | grep -E "<verification-grep>" | head -20
```

**Pattern B — background until-loop (preferred for slow CDNs):**

Invoke `poll_deploy "https://your.site/" "<new-content-marker>" 60` with
`run_in_background: true`. You get a completion notification; do not poll it yourself.

### Three-line template

```
# 1. Push and capture the unique marker
git push origin <branch>
# (mentally note: which line in the diff is unique to this push?)

# 2. Poll on that exact marker (after defining poll_deploy above)
poll_deploy "<prod-url>" "<unique-marker>" 24 || exit $?

# 3. Run the broader verification grep
curl -s <prod-url> | grep -E "(<token>|<class>|<copy-string>)" | head -10
```

## Verification

The bounded poll is correct when:

- `curl <url> | grep "<marker>"` returns NOTHING immediately after push (proves the marker is
  genuinely new).
- A successful poll prints `LIVE` and returns zero; timeout, HTTP failure, and stale content each
  print their named reason and return nonzero.
- `deploy_status` is not called when the marker appears, and is called only after the attempt cap.

If the poll succeeds in less than ~5 seconds for a platform that typically takes 30+ seconds, your
predicate matched pre-existing content. Re-pick the marker.

## Example

Session 2026-05-27, the author's public [azimuth](https://github.com/MrBinnacle/azimuth) skill
repo, fixing WCAG AA contrast on `index.html`:

**First attempt (wrong predicate):**
```bash
poll_deploy "https://mrbinnacle.github.io/azimuth/" "case-footnote" 24
```
Loop exited instantly. `.case-footnote` existed in the OLD HTML — only its `color` value
changed. False positive.

**Second attempt (correct predicate):**
```bash
poll_deploy "https://mrbinnacle.github.io/azimuth/" "overflow-x: auto" 24
```
`overflow-x: auto` was a brand-new declaration on `.v-table-wrap` introduced in the same commit.
Loop waited ~30 seconds, then exited on real new content. Verified.

## Notes

- The `gh api repos/.../pages/builds/latest` endpoint is informational, not authoritative. It
  can read `building` after the site is live, and `built` before the CDN catches up. Always
  verify via `curl <prod-url>` instead.
- Custom domains and CDN edges can delay propagation further (Cloudflare, Fastly). Set an attempt
  cap that covers the expected propagation window, and keep the marker deploy-unique.
- Same pattern works for Netlify, Vercel, Cloudflare Pages, S3+CloudFront, and any other
  static-site CDN. The harness rules apply identically.
- If the deploy is gated on a CI workflow (not Pages legacy auto-build), poll the workflow
  status via `gh run watch` before the curl loop, then run the curl loop to confirm content
  propagation separately.
- This skill complements harness-level guidance that tells you *not to chain sleeps*; this skill
  tells you *what to do instead* for deploy verification specifically.
