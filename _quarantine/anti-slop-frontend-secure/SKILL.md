---
name: anti-slop-frontend-secure
description: "Use when producing a single-file HTML artifact that must pass security gates: no DOM sinks, no unapproved external hosts, strict CSP, no secrets, outlined SVG only."
---

# anti-slop-frontend-secure

**Security may block completion; subjective beauty may not.**

<!-- Provenance: materialized 2026-08-09 (S228) from the operator's Notion Skills
     Library page (v1.2.0, "1% Skill Engine v1.0" anatomy, page 6f67647aeef947919b0fa291c06db09e).
     Oracle built 2026-09-06 (issue #214). The page's deliverables table listed
     scanner scripts that were NOT attached. The oracle is now implemented as
     scripts/audit_frontend.mjs and scripts/emit_csp.mjs. -->

## Authority split

Security gates (A–F) are deterministic and may block completion. The optional
taste provider is advisory, scoped to eligible surfaces only, read-only, and
never overrides a security gate. Do not reproduce another provider's doctrine
inline, and do not require any user to install it.

## Step 1. Intake and validation

- Classify request type as **FORM_PRODUCT** or **MARKETING_LANDING**.
- Select runtime mode:
  - **ARTIFACT**: single-file Claude artifact with advisory CSP via meta tag
  - **NETLIFY**: production deployment with hard CSP via `_headers`
  - **LOCAL_ONLY**: local development and manual validation only
- If classification is ambiguous, stop and ask: *Is this a functional tool or a
  presentation page?*

## Step 2. Context retrieval

- Load icon constraints: outlined SVG only. No emoji. No filled icon sets.
- Load CSP policy: `connect-src 'none'` for NETLIFY mode unless explicitly overridden.
- Load DOM sink blocklist: `innerHTML`, `eval`, `insertAdjacentHTML`, `document.write`.

## Step 3. Execute (Router -> Gates -> Mindset)

**Router**
- Based on request type, set layout primitives and component expectations.

**Gate sequence — run the oracle**
- **Gate A:** valid single-file HTML structure (`audit_frontend.mjs` gate A)
- **Gate B:** no external host connections unless explicitly approved (`audit_frontend.mjs` gate B)
- **Gate C:** no blocked DOM sink usage (`audit_frontend.mjs` gate C)
- **Gate D:** iconography check. Outlined SVG only. Emoji blocked (`audit_frontend.mjs` gate D)
- **Gate E:** generate CSP headers for NETLIFY mode (`emit_csp.mjs` or `audit_frontend.mjs` gate E)
- **Gate F:** no secrets in the emitted artifact (`audit_frontend.mjs` gate F)

**Mindset**
- Apply anti-slop frontend discipline. No generic Bootstrap patterns. No stock filler
  copy. Clean typography. Purposeful whitespace. Every element has a reason to be there.

## Step 4. Verification

- Run `scripts/audit_frontend.mjs <file> [--mode netlify] [--allowlist host1,host2]`
- Run `scripts/emit_csp.mjs <file> [--action emit|validate] [--deploy netlify]`
- If any gate fails, fix before output.
- For NETLIFY mode, emit `_headers` alongside the HTML artifact.

## Step 5. Output (Minimal Change Rule)

- Output a single HTML file for ARTIFACT mode.
- Output HTML plus `_headers` for NETLIFY mode.
- Include inline comments showing where each gate is enforced.
- When iterating on existing code, return only the necessary changed lines. Do not
  regenerate the whole file unless the user explicitly asks for a rewrite.

## Negative constraints

- Never use emoji for icons. Outlined SVG only.
- Never use `innerHTML`, `eval`, `insertAdjacentHTML`, or `document.write`.
- Never connect to external hosts without explicit override.
- Never output generic Bootstrap or template-kit patterns.
- Never skip gate validation, even for quick requests.
- Never let a subjective aesthetic override a security gate.
