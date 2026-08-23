---
name: anti-slop-frontend-secure
description: Security-first frontend skill for single-file HTML artifacts and secure UI components. Invoke when the user needs a single-file HTML UI artifact or secure frontend component and the output must pass security gates - no emoji icons, safe DOM patterns, strict CSP, and outlined SVG only.
---

# anti-slop-frontend-secure

<!-- Provenance: materialized 2026-08-09 (S228) from the operator's Notion Skills
     Library page (v1.2.0, "1% Skill Engine v1.0" anatomy, page 6f67647aeef947919b0fa291c06db09e).
     Faithful transcription of the page's Core Execution Flow; not re-authored.
     The page's deliverables table lists scanner scripts (scan_emoji.js,
     scan_external_hosts.js, scan_dom_sinks.js, emit_netlify_headers.js) in a ZIP
     that is NOT attached to the Notion row - retrieval is an operator step. -->

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

**Gate sequence**
- **Gate A:** valid single-file HTML structure
- **Gate B:** no external host connections unless explicitly approved
- **Gate C:** no blocked DOM sink usage
- **Gate D:** iconography check. Outlined SVG only. Emoji blocked unless user overrides
- **Gate E:** generate CSP headers for NETLIFY mode

**Mindset**
- Apply anti-slop frontend discipline. No generic Bootstrap patterns. No stock filler
  copy. Clean typography. Purposeful whitespace. Every element earns its place.

## Step 4. Verification

- Run all 5 gates as a pass or fail checklist.
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
