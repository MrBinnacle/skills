#!/usr/bin/env python3
"""Emit a content-security policy for a single-file artifact, or validate one.

TWO ACTIONS
    emit      derive the tightest policy the document actually needs, and render
              it for the deployment mode: a `_headers` block for `netlify`, a
              `<meta http-equiv>` tag for `artifact`.
    validate  read a policy -- supplied on the command line, or taken from the
              document's own meta tag -- and report where it disagrees with what
              the document does.

WHY DERIVE RATHER THAN TEMPLATE
    A policy copied from a template is either too loose, in which case it grants
    what the page never needed, or too tight, in which case the page breaks and
    the next person widens it with `'unsafe-inline'` and stops there. Deriving
    the policy from the parsed document gives a starting point that is exactly
    the page's own surface, and `validate` is what keeps it that way afterwards.

    Inline scripts are pinned by `'sha256-...'` rather than waved through. That
    is what makes a strict policy compatible with a single-file artifact at all:
    the script cannot be moved to its own file without breaking the single-file
    promise, so it is admitted by digest instead.

WHAT THIS DOES NOT DO
    It does not judge whether the policy is a good idea, and it does not rewrite
    the document. It reports, and `audit_frontend.py` Gate E is what blocks.

EXIT CODES
    0  the policy was emitted, or the supplied policy agrees with the document
    1  the supplied policy disagrees with the document
    2  usage error
    3  refused: the input is out of scope
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_frontend import (  # noqa: E402
    CSS_URL_RE,
    EXIT_FAIL,
    EXIT_PASS,
    EXIT_REFUSED,
    EXIT_USAGE,
    FETCH_URL_RE,
    INLINE_HANDLER_RE,
    WEBSOCKET_URL_RE,
    XHR_URL_RE,
    Document,
    executed_scripts,
    host_of,
    in_scope,
    parse,
    split_srcset,
)

TOOL: Final[str] = "emit_csp.py"
RECEIPT_SCHEMA: Final[str] = "anti-slop-frontend-secure/csp-receipt/1"

DEPLOY_MODES: Final[tuple[str, ...]] = ("netlify", "artifact")

# The directives this tool states, in the order a reader expects them. Every one
# is written even when its value is `'none'`: an absent directive falls back to
# `default-src`, and a reader cannot tell a deliberate fallback from a
# forgotten line.
DIRECTIVE_ORDER: Final[tuple[str, ...]] = (
    "default-src",
    "script-src",
    "style-src",
    "img-src",
    "font-src",
    "connect-src",
    "form-action",
    "frame-ancestors",
    "base-uri",
    "object-src",
)

# `<meta http-equiv>` cannot carry these, so `emit --deploy artifact` drops them
# and says it did rather than emitting a tag a browser silently ignores.
META_UNSUPPORTED: Final[frozenset[str]] = frozenset({"frame-ancestors"})

NONE: Final[str] = "'none'"
SELF: Final[str] = "'self'"


def script_hash(body: str) -> str:
    """The `'sha256-...'` source expression for one inline script body.

    The digest is over the script's text exactly as the browser sees it, which
    is the decoded character data between the tags. Whitespace is part of it, so
    reformatting the document changes the hash -- that is the mechanism working,
    not a defect.
    """
    digest = hashlib.sha256(body.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


class Surface:
    """Everything about a document that a policy has to account for."""

    def __init__(self, document: Document) -> None:
        self.inline_script_hashes: list[str] = []
        self.script_hosts: set[str] = set()
        self.style_hosts: set[str] = set()
        self.image_hosts: set[str] = set()
        self.font_hosts: set[str] = set()
        self.connect_hosts: set[str] = set()
        self.form_actions: set[str] = set()
        self.has_inline_style_attributes = False
        self.has_inline_style_elements = False
        self.has_inline_handlers = False
        self.uses_data_images = False
        self.declared_meta_policy: str | None = None

        for script in executed_scripts(document):
            body = script.text()
            if body.strip():
                self.inline_script_hashes.append(script_hash(body))
            for pattern in (FETCH_URL_RE, XHR_URL_RE, WEBSOCKET_URL_RE):
                for match in pattern.finditer(body):
                    host = host_of(match.group(1))
                    if host:
                        self.connect_hosts.add(host)

        for element in document.elements():
            source = element.attrs.get("src", "")
            if element.tag == "script" and source:
                host = host_of(source)
                if host:
                    self.script_hosts.add(host)
            if element.tag in ("img", "picture", "source"):
                for value in ([source] if source else []) + split_srcset(
                    element.attrs.get("srcset", "")
                ):
                    if value.startswith("data:"):
                        self.uses_data_images = True
                        continue
                    host = host_of(value)
                    if host:
                        self.image_hosts.add(host)
            if element.tag == "link":
                relation = element.attrs.get("rel", "").lower()
                host = host_of(element.attrs.get("href", ""))
                if host and "stylesheet" in relation:
                    self.style_hosts.add(host)
                elif host and "preload" in relation and element.attrs.get("as") == "font":
                    self.font_hosts.add(host)
            if element.tag == "form":
                action = element.attrs.get("action", "").strip()
                if action:
                    self.form_actions.add(host_of(action) or SELF)
            if element.tag == "style":
                self.has_inline_style_elements = True
                for match in CSS_URL_RE.finditer(element.text()):
                    value = match.group(1)
                    if value.startswith("data:"):
                        continue
                    host = host_of(value)
                    if host:
                        self.font_hosts.add(host)
            if element.attrs.get("style"):
                self.has_inline_style_attributes = True
            for attribute in element.attrs:
                if INLINE_HANDLER_RE.match(attribute):
                    self.has_inline_handlers = True
            if element.tag == "meta" and (
                element.attrs.get("http-equiv", "").lower() == "content-security-policy"
            ):
                self.declared_meta_policy = element.attrs.get("content", "")


def derive(surface: Surface, deploy: str, allowlist: list[str]) -> dict[str, list[str]]:
    """The tightest policy that still lets this document work.

    `default-src 'none'` and then grant back, rather than `'self'` and then
    restrict. A policy built by subtraction grants whatever nobody thought to
    subtract.
    """
    allowed = sorted({h.strip().lower() for h in allowlist if h.strip()})

    script: list[str] = list(surface.inline_script_hashes)
    script += [h for h in sorted(surface.script_hosts) if h in allowed]
    if surface.has_inline_handlers:
        # Stated, never granted. Gate E blocks the document instead.
        script.append("/* inline handlers present: remove them, do not add 'unsafe-inline' */")
        script = [part for part in script if not part.startswith("/*")]

    style: list[str] = []
    if surface.has_inline_style_elements or surface.has_inline_style_attributes:
        style.append("'unsafe-inline'")
    style += [h for h in sorted(surface.style_hosts) if h in allowed]

    image: list[str] = []
    if surface.uses_data_images:
        image.append("data:")
    image += [h for h in sorted(surface.image_hosts) if h in allowed]

    font = [h for h in sorted(surface.font_hosts) if h in allowed]

    # The card's own rule, quoted from SKILL.md Step 2: connect-src is 'none'
    # for a deployed page unless a host was explicitly declared.
    connect = [h for h in sorted(surface.connect_hosts) if h in allowed]
    if deploy == "netlify" and not connect:
        connect = [NONE]
    elif not connect:
        connect = [NONE]

    form = sorted(surface.form_actions) if surface.form_actions else [NONE]

    return {
        "default-src": [NONE],
        "script-src": script or [NONE],
        "style-src": style or [NONE],
        "img-src": image or [NONE],
        "font-src": font or [NONE],
        "connect-src": connect,
        "form-action": form,
        "frame-ancestors": [NONE],
        "base-uri": [NONE],
        "object-src": [NONE],
    }


def render_policy(directives: dict[str, list[str]], omit: frozenset[str] = frozenset()) -> str:
    parts = [
        f"{name} {' '.join(directives[name])}"
        for name in DIRECTIVE_ORDER
        if name in directives and name not in omit
    ]
    return "; ".join(parts)


def render_headers(policy: str) -> str:
    """A Netlify `_headers` block. Wildcard path: the policy is the whole site."""
    return "\n".join(
        [
            "/*",
            f"  Content-Security-Policy: {policy}",
            "  X-Content-Type-Options: nosniff",
            "  Referrer-Policy: no-referrer",
            "  X-Frame-Options: DENY",
        ]
    )


def render_meta(policy: str) -> str:
    escaped = policy.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    return f'<meta http-equiv="Content-Security-Policy" content="{escaped}">'


def parse_policy(text: str) -> dict[str, list[str]]:
    directives: dict[str, list[str]] = {}
    for clause in text.split(";"):
        parts = clause.split()
        if not parts:
            continue
        directives[parts[0].lower()] = parts[1:]
    return directives


def validate_policy(
    policy: str, surface: Surface, deploy: str
) -> tuple[list[str], list[str]]:
    """Disagreements between a stated policy and what the document does.

    Two lists, and the split matters. `violations` are places the policy is
    WEAKER than the document needs it to be, which is the direction that costs
    something. `unused` are grants the document never exercises, which is a
    tightening opportunity and not a failure.
    """
    directives = parse_policy(policy)
    violations: list[str] = []
    unused: list[str] = []

    default = directives.get("default-src", [])
    if NONE not in default:
        violations.append(f"default-src is {' '.join(default) or 'absent'}, not {NONE}")

    script = directives.get("script-src", directives.get("default-src", []))
    if "'unsafe-inline'" in script:
        violations.append("script-src grants 'unsafe-inline', which defeats the policy")
    if "'unsafe-eval'" in script:
        violations.append("script-src grants 'unsafe-eval'")
    for digest in surface.inline_script_hashes:
        if digest not in script:
            violations.append(f"script-src does not pin an inline script: {digest[:24]}...")
    for host in sorted(surface.script_hosts):
        if host not in script and "*" not in script:
            violations.append(f"script-src omits a host the document loads: {host}")

    connect = directives.get("connect-src", directives.get("default-src", []))
    for host in sorted(surface.connect_hosts):
        if host not in connect and "*" not in connect:
            violations.append(f"connect-src omits a host the document reaches: {host}")
    if deploy == "netlify" and not surface.connect_hosts and NONE not in connect:
        unused.append(
            f"connect-src is {' '.join(connect)} but the document makes no request; "
            f"{NONE} would be exact"
        )

    style = directives.get("style-src", directives.get("default-src", []))
    needs_inline_style = (
        surface.has_inline_style_elements or surface.has_inline_style_attributes
    )
    if needs_inline_style and "'unsafe-inline'" not in style:
        violations.append(
            "style-src omits 'unsafe-inline' but the document carries inline styles"
        )
    if not needs_inline_style and "'unsafe-inline'" in style:
        unused.append("style-src grants 'unsafe-inline' that the document does not use")

    if surface.has_inline_handlers:
        violations.append(
            "the document carries inline event handlers; no strict policy admits them"
        )

    for name in ("frame-ancestors", "base-uri", "object-src"):
        if name not in directives and deploy == "netlify":
            unused.append(f"{name} is not stated, so it falls back to default-src")

    return violations, unused


def build_receipt(
    path: Path,
    source: str,
    action: str,
    deploy: str,
    allowlist: list[str],
    stamp: bool,
) -> tuple[dict[str, Any], int, str]:
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "tool": TOOL,
        "input": path.as_posix(),
        "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "action": action,
        "deploy": deploy,
        "allowlist": sorted({h.strip().lower() for h in allowlist if h.strip()}),
    }
    if stamp:
        receipt["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    scoped, reason = in_scope(path, source)
    if not scoped:
        receipt.update({"verdict": "REFUSED", "refusal_reason": reason})
        return receipt, EXIT_REFUSED, ""

    document = parse(source)
    surface = Surface(document)
    receipt["surface"] = {
        "inline_scripts": len(surface.inline_script_hashes),
        "script_hosts": sorted(surface.script_hosts),
        "connect_hosts": sorted(surface.connect_hosts),
        "style_hosts": sorted(surface.style_hosts),
        "image_hosts": sorted(surface.image_hosts),
        "inline_handlers": surface.has_inline_handlers,
        "inline_styles": surface.has_inline_style_elements
        or surface.has_inline_style_attributes,
        "declared_meta_policy": surface.declared_meta_policy,
    }
    return receipt, EXIT_PASS, "ready"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL, description="Emit or validate a content-security policy."
    )
    parser.add_argument("file", type=Path, help="the artifact to read")
    parser.add_argument(
        "--action", choices=("emit", "validate"), default="emit", help="what to do"
    )
    parser.add_argument(
        "--deploy", choices=DEPLOY_MODES, default="netlify", help="deployment mode"
    )
    parser.add_argument(
        "--allowlist", default="", help="comma-separated hosts the policy may grant"
    )
    parser.add_argument(
        "--policy",
        default=None,
        help="the policy to validate; defaults to the document's own meta tag",
    )
    parser.add_argument(
        "--receipt", type=Path, default=None, help="write the receipt here as well"
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="omit generated_at so two runs on one input are byte-equal",
    )
    args = parser.parse_args(argv)

    try:
        source = args.file.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        print(f"REFUSED: cannot read {args.file}: {error}", file=sys.stderr)
        return EXIT_USAGE

    allowlist = args.allowlist.split(",") if args.allowlist else []
    receipt, code, state = build_receipt(
        args.file, source, args.action, args.deploy, allowlist, not args.no_timestamp
    )
    if state != "ready":
        print(json.dumps(receipt, indent=2, ensure_ascii=True))
        return code

    document = parse(source)
    surface = Surface(document)

    if args.action == "emit":
        directives = derive(surface, args.deploy, allowlist)
        omit = META_UNSUPPORTED if args.deploy == "artifact" else frozenset()
        policy = render_policy(directives, omit)
        receipt.update(
            {
                "verdict": "EMITTED",
                "directives": {k: v for k, v in directives.items() if k not in omit},
                "policy": policy,
                "omitted_directives": sorted(omit),
                "rendered": render_headers(policy)
                if args.deploy == "netlify"
                else render_meta(policy),
                "rendered_as": "_headers" if args.deploy == "netlify" else "meta",
            }
        )
        exit_code = EXIT_PASS
    else:
        policy = args.policy or surface.declared_meta_policy
        if not policy:
            receipt.update(
                {
                    "verdict": "FAIL",
                    "violations": [
                        "no policy supplied and the document states no "
                        "<meta http-equiv=Content-Security-Policy>"
                    ],
                    "unused_grants": [],
                }
            )
            print(json.dumps(receipt, indent=2, ensure_ascii=True))
            return EXIT_FAIL
        violations, unused = validate_policy(policy, surface, args.deploy)
        receipt.update(
            {
                "verdict": "PASS" if not violations else "FAIL",
                "policy": policy,
                "policy_source": "argument" if args.policy else "meta tag",
                "violations": violations,
                "unused_grants": unused,
            }
        )
        exit_code = EXIT_PASS if not violations else EXIT_FAIL

    rendered = json.dumps(receipt, indent=2, ensure_ascii=True)
    print(rendered)
    if args.receipt is not None:
        args.receipt.write_text(rendered + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
