---
name: anti-slop-frontend-secure
description: Use when writing a single-file HTML artifact or a deployable frontend that must clear security gates - safe DOM construction, a host allowlist, a content-security policy, no secret in the output.
---

# anti-slop-frontend-secure

<!-- Provenance: materialized 2026-08-09 (S228) from the operator's Notion Skills
     Library page (v1.2.0, "1% Skill Engine v1.0" anatomy, page 6f67647aeef947919b0fa291c06db09e).
     Faithful transcription of the page's Core Execution Flow; not re-authored.
     The page's deliverables table lists scanner scripts (scan_emoji.js,
     scan_external_hosts.js, scan_dom_sinks.js, emit_netlify_headers.js) in a ZIP
     that is NOT attached to the Notion row - retrieval is an operator step.
     2026-09-06: those scanners are superseded rather than retrieved. The gates
     below are implemented in this folder, in Python, on the standard library. -->

**Security may block completion; subjective beauty may not.**

That line is the contract. Everything in this card is the security half: safe DOM
construction, network allowlists, content-security policy, secret exclusion. It is
deterministic and it is checkable. A frontend taste provider is optional, scoped to
eligible surfaces, read-only and advisory; this card reproduces no provider's doctrine
and requires nobody to install one.

## The scripts this card asks you to run

Both live in this folder, so an install delivers them and you can read them before you
run them. They import nothing outside the Python standard library.

- `audit_frontend.py` - the deterministic oracle. Six gates over one document.
- `emit_csp.py` - derive a content-security policy for the deployment mode, or check
  one that already exists.
- `test_oracle.py` - the fixture suite. It runs the gates against `fixtures.json` and
  the five arms in `ablations.json`. Run it after any edit to either script.

```bash
python audit_frontend.py <file.html> [--mode artifact|netlify|local_only] \
    [--allowlist host1,host2] [--advisory notes.json] [--receipt receipt.json]
python emit_csp.py <file.html> [--action emit|validate] [--deploy netlify|artifact]
python test_oracle.py
```

Exit codes from `audit_frontend.py`: `0` every gate passed, `1` a gate failed, `2` a
usage error, `3` refused because the input is out of scope. Refusal has its own code
because "this is not an HTML artifact" and "this artifact is unsafe" are different
answers.

## Step 1. Intake and validation

- Classify the request as **FORM_PRODUCT** or **MARKETING_LANDING**.
- Select the runtime mode:
  - **ARTIFACT**: a single-file artifact with an advisory policy in a meta tag.
  - **NETLIFY**: a deployment with a hard policy in `_headers`.
  - **LOCAL_ONLY**: local development and manual validation.
- If the classification is ambiguous, stop and ask: *is this a functional tool or a
  presentation page?*

The mode is an argument to the oracle, not a note to yourself. Gate E enforces in
`netlify` mode, reports without blocking in `artifact` mode, and skips in `local_only`.

## Step 2. Context retrieval

- Iconography: outlined SVG only. No emoji in rendered text or in an accessible name.
- Policy: `connect-src 'none'` for NETLIFY mode unless a host is declared on the
  allowlist.
- DOM sink blocklist: `innerHTML`, `eval`, `insertAdjacentHTML`, `document.write`.

## Step 3. Execute (Router -> Gates -> Mindset)

**Router.** The request type sets the layout primitives and the component expectations.

**Gate sequence.** Each gate is a function in `audit_frontend.py` with a passing and a
failing fixture in `fixtures.json`.

| Gate | Question | Fails on |
|---|---|---|
| A | Is this one well-formed file? | no doctype, no shell, empty title, a subresource pulled from a separate file |
| B | Was every host it reaches declared? | a host outside `--allowlist` in an attribute, a stylesheet, or a network call |
| C | Does it execute a blocked sink? | a blocklist name in an executed script or an inline handler |
| D | Are the icons outlined SVG? | a pictograph in rendered text or an accessible name, a literal `fill` on an SVG shape |
| E | Is it compatible with a strict policy? | an inline handler or a style attribute, in `netlify` mode |
| F | Does it ship a credential? | a key, token or private-key block in any region the parser can name, comments included |

**Mindset.** Anti-slop frontend discipline. No template-kit patterns. No stock filler
copy. Clean typography. Purposeful whitespace. Every element has a reason to be there.
This paragraph is advice and no gate enforces it, which is the authority split working.

## Step 4. Verification

Run the oracle. Do not perform the gates by reading.

```bash
python audit_frontend.py build/index.html --mode netlify --allowlist cdn.example.org
```

The run prints a receipt naming the schema, the input path, the digest of the bytes
audited, the mode, the allowlist, every gate that ran, and the result of each. Keep the
receipt with the artifact: a verdict without one is a claim, and the digest is what ties
the claim to the file it was made about.

If a gate fails, fix the document. Do not widen the allowlist to make Gate B green
unless the host is one you meant to reach, and do not add `'unsafe-inline'` to make a
policy fit a page that carries inline handlers - remove the handlers instead.

For NETLIFY mode, emit the policy alongside the artifact:

```bash
python emit_csp.py build/index.html --action emit --deploy netlify > _headers.json
```

The emitter derives the policy from the parsed document rather than from a template, so
it grants what the page uses and nothing else. Inline scripts are pinned by
`'sha256-...'` digest, which is what lets a strict policy coexist with a single file.

## Step 5. Output (Minimal Change Rule)

- ARTIFACT mode outputs one HTML file.
- NETLIFY mode outputs the HTML plus `_headers`.
- Inline comments show where each gate is enforced.
- When iterating on existing code, return the changed lines. Do not regenerate the whole
  file unless a rewrite was asked for.

## Working with a frontend taste provider

Optional and advisory. A provider writes its notes to a JSON file holding a `notes`
list; pass it with `--advisory`. The notes are copied into the receipt and they change
no gate verdict and no exit code. A provider that cannot be read degrades the run to
`advisory_status: "degraded"` and the security verdict is unaffected.

`ablations.json` declares five arms and `test_oracle.py` executes them: with a provider,
without one, an out-of-scope input that must be refused, a provider failure that must
degrade rather than block, and unsafe aesthetic advice where the security gate overrides
the provider. Arms 1, 2 and 4 are asserted to produce identical gate results, which is
the authority split written as an equality rather than as a sentence.

## Negative constraints

- Never use emoji for icons. Outlined SVG only.
- Never use `innerHTML`, `eval`, `insertAdjacentHTML`, or `document.write`.
- Never reach an external host that was not declared.
- Never put a credential in the artifact, a comment included.
- Never skip the oracle, even for a quick request. Reading the gates is not running them.

## What this card does not claim

The oracle answers six questions about one document. It does not read the server, it
does not judge the design, and a green run is evidence about those six questions and
nothing wider. Gate B sees the hosts a document names; a host assembled at run time from
string fragments is outside what any static check can see, and the policy `emit_csp.py`
emits is the control that still holds there.

See `gotchas.md` for the failure modes worth knowing before the first run, and
`EVIDENCE.md` for what this card can and cannot yet show about its own necessity.
