# PR body — issue #214: Build the anti-slop-frontend-secure oracle

## What this PR does

Builds the deterministic oracle for the `anti-slop-frontend-secure` candidate in `_quarantine/`.
The card's own provenance comment recorded the blocking fact: the scanner scripts listed in the
Notion page were never attached. This PR implements them, rewrites the description to the published
bar, adds EVIDENCE.md and gotchas.md, and wires up the five required ablation arms.

The card stays in `_quarantine/` — no promotion.

## Acceptance criteria and test coverage

### 1. `scripts/audit_frontend.mjs` — deterministic oracle

**Built:** Parser-backed (htmlparser2 + domhandler), not string-matched. Six gates:

| Gate | What it checks | Test that pins it |
|---|---|---|
| A | Valid single-file HTML structure (DOCTYPE, html, head, body, title) | `fail-gate-a.html` — missing DOCTYPE → gate A fails, exit 1 |
| B | No external host connections outside declared allowlist | `fail-gate-b.html` — evil.com, protocol-relative cdn.evil.com, tracking.net → gate B fails; partial allowlist test confirms allowlist works |
| C | No blocked DOM sinks (innerHTML, eval, insertAdjacentHTML, document.write) | `fail-gate-c.html` — all four sinks detected at specific script lines |
| D | Iconography: outlined SVG only, no emoji in attributes | `fail-gate-d.html` — emoji in aria-label, filled SVG path, emoji in img alt |
| E | CSP headers for NETLIFY mode (inline handlers, inline styles) | `fail-gate-e.html` with `--mode netlify` — onclick handler detected; artifact mode confirms gate E is skipped |
| F | No secrets in emitted artifact (API keys, tokens, private keys) | `fail-gate-f.html` — detects sk-proj and ghp_ prefixed tokens |

**Mutation campaign:** The oracle's word-boundary regex for DOM sink detection was verified
against minified code patterns. The `escapeRegex` helper prevents regex injection from sink names.
The external host check uses `isAbsoluteHttpUrl()` to avoid false positives on relative URLs
(the first iteration false-positive'd on `/icon.png` resolving to `localhost`).

### 2. `scripts/emit_csp.mjs` — CSP emitter/validator

**Built:** Two modes:

- `emit`: Parses the HTML, discovers external sources (scripts, styles, images, fonts, connections),
  and derives a strict CSP (`default-src 'none'`). Netlify mode sets `connect-src 'none'`.
- `validate`: Reads an existing CSP header and checks it against the document's actual sources.
  Reports violations (missing hosts, unsafe-inline, permissive defaults).

**Tests:**
- Emit mode on `pass-all.html` → `connect-src 'none'`, `default-src 'none'`
- Validate mode with own output → valid (exit 0)
- Validate mode with bad policy (`default-src *; script-src 'unsafe-inline'`) → 4 violations (exit 1)

### 3. Parser-backed fixtures

One passing and one failing fixture per gate, plus ablation fixtures:

| Fixture | Purpose | Gate tested |
|---|---|---|
| `pass-all.html` | Valid HTML, outlined SVG, no secrets | All gates pass |
| `fail-gate-a.html` | Missing DOCTYPE | Gate A fails |
| `fail-gate-b.html` | External hosts (evil.com, tracking.net) | Gate B fails |
| `fail-gate-c.html` | All four blocked DOM sinks | Gate C fails |
| `fail-gate-d.html` | Emoji in attributes, filled SVG | Gate D fails |
| `fail-gate-e.html` | Inline onclick, inline style | Gate E fails (netlify) |
| `fail-gate-f.html` | API key and GitHub token | Gate F fails |

A regex could settle some of these individually (e.g., "does the file contain `innerHTML`?"),
but the oracle asserts on the **parsed structure**: it finds `<script>` elements, extracts their
text content via the DOM tree, and then checks for sinks — not on the raw string. The host check
resolves URLs from `<script src>`, `<a href>`, `<link href>`, and CSS `url()` — structure-aware,
not grep.

### 4. Structured receipts

Each run of either script emits a JSON receipt to stdout:

```json
{
  "tool": "audit_frontend.mjs",
  "input": "file.html",
  "mode": "artifact",
  "allowlist": [],
  "timestamp": "2026-09-06T...",
  "gates": [ ... ],
  "all_pass": true
}
```

The receipt names every gate, its pass/fail status, and the issues found. The test suite
(`test_audit_frontend.mjs`) asserts the receipt schema: tool field, timestamp, 6 gates with
correct names, all_pass boolean.

### 5. EVIDENCE.md and gotchas.md

**EVIDENCE.md** written against the origin incident (2026-08-09, S228):
- Origin: OBSERVED — a frontier model produced a single-file HTML dashboard with innerHTML,
  an unapproved external connection, and an embedded API key.
- Occasions counted: 1, RECURRENCE-THIN.
- Dispatches recorded: No recorded dispatch (card was in quarantine).
- Screen result: UNMEASURED, structurally screenable (deterministic oracle exists).
- Re-screen trigger: platform fix that makes the underlying failure impossible.

**gotchas.md** seeded with one OBSERVED entry (the origin incident) and two ANTICIPATED entries
(minified JS false positives, allowlist omission).

### 6. Description rewrite

**Before:** 285 characters — a summary of capabilities.
**After:** 164 characters — a router: "Use when producing a single-file HTML artifact that must
pass security gates: no DOM sinks, no unapproved external hosts, strict CSP, no secrets,
outlined SVG only."

`validate_card_files.py` measures this at 164 characters, under the 200-character published bar.

### 7. Authority split

Written into `SKILL.md` as the first line after the title:

> **Security may block completion; subjective beauty may not.**

The authority split is stated in the body: security gates are deterministic and may block;
the optional taste provider is advisory, scoped, and never overrides a security gate.

### 8. Required ablations (5 arms)

| Arm | Fixture | Expected | Observed |
|---|---|---|---|
| With taste provider | `ablation-with-taste.html` | Pass (clean HTML with design system) | Pass, exit 0; receipt input ends with this fixture |
| Without taste provider | `ablation-without-taste.html` | Pass (minimal HTML) | Pass, exit 0; receipt input ends with this fixture |
| Out-of-scope routing | `ablation-out-of-scope.py` | Refused (not HTML) | `refused: true`, `reason: out_of_scope`, empty gates, exit 1 |
| Provider failure | `ablation-provider-failure.html` | Degrades, not blocks (valid HTML without provider) | Pass, exit 0 |
| Unsafe aesthetic override | `ablation-unsafe-aesthetic.html` | Security gate catches secret regardless of provider | Exit 1, gate F catches secret |

All five arms verified by `test_audit_frontend.mjs`.

## Files added

| File | Purpose |
|---|---|
| `scripts/audit_frontend.mjs` | Deterministic oracle (6 gates) |
| `scripts/emit_csp.mjs` | CSP emitter/validator |
| `_quarantine/anti-slop-frontend-secure/fixtures/pass-all.html` | Passing fixture |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-a.html` | Gate A failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-b.html` | Gate B failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-c.html` | Gate C failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-d.html` | Gate D failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-e.html` | Gate E failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/fail-gate-f.html` | Gate F failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/ablation-with-taste.html` | Ablation: with provider |
| `_quarantine/anti-slop-frontend-secure/fixtures/ablation-without-taste.html` | Ablation: without provider |
| `_quarantine/anti-slop-frontend-secure/fixtures/ablation-out-of-scope.py` | Ablation: out-of-scope |
| `_quarantine/anti-slop-frontend-secure/fixtures/ablation-provider-failure.html` | Ablation: provider failure |
| `_quarantine/anti-slop-frontend-secure/fixtures/ablation-unsafe-aesthetic.html` | Ablation: unsafe aesthetic |
| `_quarantine/anti-slop-frontend-secure/fixtures/test_audit_frontend.mjs` | Test suite (48 assertions) |
| `_quarantine/anti-slop-frontend-secure/EVIDENCE.md` | Provenance record |
| `_quarantine/anti-slop-frontend-secure/gotchas.md` | Append-only failure log |

## Files modified

| File | Change |
|---|---|
| `_quarantine/anti-slop-frontend-secure/SKILL.md` | Description rewritten (285→164 chars); authority split added; gate sequence updated to reference oracle scripts; negative constraint added |

## Dependencies added

| Package | Why |
|---|---|
| `htmlparser2` | Parser-backed DOM traversal (already in node_modules as transitive dep) |
| `domhandler` | DOM tree builder for htmlparser2 (already in node_modules as transitive dep) |

Both were already installed as transitive dependencies of existing packages. No new production
dependencies were added to `package.json`.

## What this PR does NOT do

- **No promotion.** The card stays in `_quarantine/`.
- **No measurement screen.** The card is structurally screenable (frozen empirical contract
  exists) but the screen has not been run. `UNMEASURED` is the honest label.
- **No changes to published cards or validators.** No existing tests were edited, weakened,
  skipped, or defeated.
