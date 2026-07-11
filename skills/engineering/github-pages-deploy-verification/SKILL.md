---
name: github-pages-deploy-verification
description: Verify a GitHub Pages (or any CDN-fronted) deploy actually serves new content. Poll on a marker that did not exist pre-deploy; avoid sleep-and-curl chains the agent harness blocks.
---

# GitHub Pages deploy verification

## Problem

Two failure modes when verifying that a deploy is live via `curl`:

1. **False-positive poll predicate.** Polling `until curl ... | grep -q "<selector>"; do sleep; done`
   succeeds instantly if the selector existed before the deploy too. The loop exits on the OLD
   content; you think you've verified the new state and you haven't.

2. **Blocked timing chain.** `sleep 35 && curl ...` looks reasonable but the Claude Code harness
   blocks long leading sleeps inside Bash to prevent dead polling. Worse, even short
   `sleep N && curl` followed by additional pipes can hit "Blocked: sleep N followed by:" errors
   that cancel parallel tool calls.

Both bugs hit one session inside ~30 minutes. They are not in the same family but they ride the
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

Rule: `git diff HEAD~1 -- index.html | grep '^+'` produces candidate strings. Pick the one most
unique to the diff.

### Avoid blocked timing chains

In Claude Code's Bash tool, do not write:

```bash
sleep 35 && curl ...    # often blocked
```

Use one of these instead:

**Pattern A — synchronous until-loop with a check command:**

```bash
until curl -s https://your.site/ | grep -q "<new-content-marker>"; do sleep 5; done
echo "--- LIVE ---"
curl -s https://your.site/ | grep -E "<verification-grep>" | head -20
```

**Pattern B — background until-loop (preferred for slow CDNs):**

Same command, but invoked with `run_in_background: true`. You get a completion notification; do
not poll yourself.

### Three-line template

```
# 1. Push and capture the unique marker
git push origin <branch>
# (mentally note: which line in the diff is unique to this push?)

# 2. Poll on that exact marker
until curl -s <prod-url> | grep -q "<unique-marker>"; do sleep 5; done

# 3. Run the broader verification grep
curl -s <prod-url> | grep -E "(<token>|<class>|<copy-string>)" | head -10
```

## Verification

The poll predicate is correct when:

- `curl <url> | grep "<marker>"` returns NOTHING immediately after push (proves the marker is
  genuinely new).
- The same command returns the marker once the loop exits (proves the deploy reached the CDN).

If the loop exits in less than ~5 seconds for a platform that typically takes 30+ seconds, your
predicate matched pre-existing content. Re-pick the marker.

## Example

Session 2026-05-27, the author's public [azimuth](https://github.com/MrBinnacle/azimuth) skill
repo, fixing WCAG AA contrast on `index.html`:

**First attempt (wrong predicate):**
```bash
until curl -s https://mrbinnacle.github.io/azimuth/ | grep -q "case-footnote"; do sleep 5; done
```
Loop exited instantly. `.case-footnote` existed in the OLD HTML — only its `color` value
changed. False positive.

**Second attempt (correct predicate):**
```bash
until curl -s https://mrbinnacle.github.io/azimuth/ | grep -q "overflow-x: auto"; do sleep 5; done
```
`overflow-x: auto` was a brand-new declaration on `.v-table-wrap` introduced in the same commit.
Loop waited ~30 seconds, then exited on real new content. Verified.

## Notes

- The `gh api repos/.../pages/builds/latest` endpoint is informational, not authoritative. It
  can read `building` after the site is live, and `built` before the CDN catches up. Always
  verify via `curl <prod-url>` instead.
- Custom domains and CDN edges can delay propagation further (Cloudflare, Fastly). The poll loop
  handles this transparently — just give it the right marker.
- Same pattern works for Netlify, Vercel, Cloudflare Pages, S3+CloudFront, and any other
  static-site CDN. The harness rules apply identically.
- If the deploy is gated on a CI workflow (not Pages legacy auto-build), poll the workflow
  status via `gh run watch` before the curl loop, then run the curl loop to confirm content
  propagation separately.
- This skill complements harness-level guidance that tells you *not to chain sleeps*; this skill
  tells you *what to do instead* for deploy verification specifically.
