#!/usr/bin/env python3
"""Deterministic security oracle for a single-file HTML frontend artifact.

WHAT THIS IS
    Six gates over one document, each answering a yes-or-no question the card's
    SKILL.md states. The run emits a structured receipt naming which gates ran,
    on what input, with what result, and exits on the verdict. Nothing here is
    advisory and nothing here is a matter of taste.

WHY IT PARSES INSTEAD OF MATCHING STRINGS
    A regular expression over the file's bytes cannot tell a blocked sink from
    the same word written in a paragraph explaining why the sink is blocked, and
    it cannot see a host that only exists once character references are decoded.
    Both directions are wrong, and both are cheap to hit by accident. So the
    document is parsed into a tree first, and every gate asks its question of a
    named region of that tree: script bodies, attribute values, rendered text,
    comments. `fixtures.json` carries a `regex_would_say` field on the cases
    where the two answers differ, and `test_oracle.py` asserts the difference,
    so the claim on this paragraph is checked rather than asserted.

    The parser is `html.parser` from the standard library. This card ships no
    dependency and requires none: `SECURITY.md` commits the collection to a
    closed format vocabulary of `.md`, `.txt`, `.py` and `.json`, and an install
    copies the skill folder and nothing else. A checker that needed a package
    tree would be a checker the reader does not receive.

THE GATES
    A  single-file structure   the document stands alone and is well-formed
    B  external host allowlist  every outbound host was declared
    C  blocked DOM sink         innerHTML, eval, insertAdjacentHTML, document.write
    D  iconography              outlined SVG only, no emoji in rendered text
    E  content-security-policy  the document is compatible with a strict policy
    F  secret exclusion         no credential ships inside the artifact

EXIT CODES
    0  every gate that ran passed
    1  at least one gate failed
    2  usage error
    3  refused: the input is out of scope for this oracle

    Refusal has its own code on purpose. "This is not an HTML artifact" and
    "this HTML artifact is unsafe" are different answers, and a caller that
    cannot tell them apart will read a refusal as a clean bill or as a defect,
    both of which are wrong.

THE AUTHORITY SPLIT
    Security may block completion; subjective beauty may not. A frontend taste
    provider is optional and advisory. Its notes reach this oracle through
    `--advisory <path>` and are copied into the receipt. They never change a
    gate verdict, they never change the exit code, and a note that cannot be
    read degrades to `advisory_status: "degraded"` rather than blocking the run.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Final, Iterator

TOOL: Final[str] = "audit_frontend.py"
RECEIPT_SCHEMA: Final[str] = "anti-slop-frontend-secure/receipt/1"

EXIT_PASS: Final[int] = 0
EXIT_FAIL: Final[int] = 1
EXIT_USAGE: Final[int] = 2
EXIT_REFUSED: Final[int] = 3

# The card's own blocklist, quoted from SKILL.md Step 2. `document.write` is
# dotted, so the match is written against the member expression rather than the
# bare identifier `write`.
BLOCKED_SINKS: Final[tuple[str, ...]] = (
    "innerHTML",
    "eval",
    "insertAdjacentHTML",
    "document.write",
)

RUNTIME_MODES: Final[tuple[str, ...]] = ("artifact", "netlify", "local_only")

# A `<script>` whose type names a template or a data block is not executed, so
# its body is not JavaScript and the sink gate does not read it. This is the
# list of types that ARE executed; anything else is inert.
EXECUTED_SCRIPT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "",
        "module",
        "text/javascript",
        "application/javascript",
        "text/ecmascript",
        "application/ecmascript",
    }
)

# Attributes whose value is a URL the document loads or navigates to.
URL_ATTRIBUTES: Final[tuple[str, ...]] = (
    "src",
    "href",
    "action",
    "formaction",
    "poster",
    "data",
    "srcset",
    "cite",
)

# Elements whose URL attribute pulls a SEPARATE FILE into the artifact. A
# relative path in one of these breaks the single-file promise; the same path in
# an `<a href>` is a link and breaks nothing.
SUBRESOURCE_ELEMENTS: Final[frozenset[str]] = frozenset(
    {"script", "link", "img", "iframe", "video", "audio", "source", "embed", "object"}
)

# Inline event handler attributes. Each one requires `'unsafe-inline'` in
# `script-src`, which is the thing a strict policy exists to refuse.
INLINE_HANDLER_RE: Final[re.Pattern[str]] = re.compile(r"^on[a-z]+$")

# Emoji and pictographic ranges. Deliberately excludes the dingbat and
# geometric ranges that carry text-presentation characters a document may use
# as punctuation.
EMOJI_RE: Final[re.Pattern[str]] = re.compile(
    "["
    "\U0001f300-\U0001f5ff"
    "\U0001f600-\U0001f64f"
    "\U0001f680-\U0001f6ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001faff"
    "\U0001f1e0-\U0001f1ff"
    "☀-⛿"
    "]"
)

# Attributes whose value is read out by a screen reader or shown as a tooltip.
# Emoji there is rendered content even though it is not a text node.
RENDERED_ATTRIBUTES: Final[tuple[str, ...]] = (
    "aria-label",
    "title",
    "alt",
    "placeholder",
    "value",
)

# An SVG fill that is not one of these is a filled icon rather than an outlined
# one. `none` and `currentColor` are the outlined-icon idioms; a custom property
# defers the choice to the stylesheet.
OUTLINE_FILLS: Final[frozenset[str]] = frozenset({"none", "currentcolor", "inherit"})

SECRET_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("aws_access_key_id", re.compile(r"\b(?:AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("slack_token", re.compile(r"\bxox[bpsare]-[A-Za-z0-9-]{10,}")),
    ("stripe_style_api_key", re.compile(r"\b[sprk]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("json_web_token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.")),
    ("google_api_key", re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")),
)

# A base64 blob long enough to hide a credential. Decoded and re-examined, so a
# secret that was encoded to slip past the patterns above is still found.
BASE64_BLOB_RE: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9+/]{32,}={0,2}")

# URL shapes. A protocol-relative `//host/path` is external; a bare `/path` is
# same-origin and is not.
ABSOLUTE_URL_RE: Final[re.Pattern[str]] = re.compile(r"^(?:[a-z][a-z0-9+.-]*:)?//", re.I)
SCHEME_RE: Final[re.Pattern[str]] = re.compile(r"^([a-z][a-z0-9+.-]*):", re.I)
CSS_URL_RE: Final[re.Pattern[str]] = re.compile(r"url\(\s*['\"]?([^)'\"\s]+)", re.I)
FETCH_URL_RE: Final[re.Pattern[str]] = re.compile(
    r"""(?:fetch|importScripts|import)\s*\(\s*['"]([^'"]+)['"]""", re.I
)
XHR_URL_RE: Final[re.Pattern[str]] = re.compile(
    r"""\.open\s*\(\s*['"][A-Z]+['"]\s*,\s*['"]([^'"]+)['"]""", re.I
)
WEBSOCKET_URL_RE: Final[re.Pattern[str]] = re.compile(
    r"""new\s+WebSocket\s*\(\s*['"]([^'"]+)['"]""", re.I
)

# Extensions that are definitely not an HTML artifact. Anything outside both
# lists is decided by looking at the bytes.
HTML_SUFFIXES: Final[frozenset[str]] = frozenset({".html", ".htm", ".xhtml"})
NOT_HTML_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".md",
        ".css", ".txt", ".yml", ".yaml", ".toml", ".sh", ".ps1", ".rb", ".go",
        ".rs", ".java", ".png", ".jpg", ".svg", ".pdf", ".lock",
    }
)
LOOKS_LIKE_HTML_RE: Final[re.Pattern[str]] = re.compile(
    r"<!doctype\s+html|<html[\s>]", re.I
)


# --------------------------------------------------------------- document tree


class Element:
    """One element in the parsed tree.

    Attribute values arrive already decoded: `html.parser` resolves character
    references inside attribute values, so `&#47;` reaches this object as `/`.
    That decoding is the point of parsing rather than matching, and Gate B has a
    fixture that turns on it.
    """

    __slots__ = ("tag", "attrs", "children", "parent", "line")

    def __init__(self, tag: str, attrs: dict[str, str], parent: "Element | None", line: int):
        self.tag = tag
        self.attrs = attrs
        self.children: list["Element | Text"] = []
        self.parent = parent
        self.line = line

    def descendants(self) -> Iterator["Element"]:
        for child in self.children:
            if isinstance(child, Element):
                yield child
                yield from child.descendants()

    def find(self, tag: str) -> list["Element"]:
        return [e for e in self.descendants() if e.tag == tag]

    def text(self) -> str:
        parts: list[str] = []
        for child in self.children:
            if isinstance(child, Text):
                parts.append(child.data)
            else:
                parts.append(child.text())
        return "".join(parts)

    def ancestors(self) -> Iterator["Element"]:
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


class Text:
    """A run of character data, or a comment, with its source line."""

    __slots__ = ("data", "line", "is_comment")

    def __init__(self, data: str, line: int, is_comment: bool = False):
        self.data = data
        self.line = line
        self.is_comment = is_comment


class Document:
    __slots__ = ("root", "doctype", "comments", "parse_errors")

    def __init__(self) -> None:
        self.root = Element("#document", {}, None, 0)
        self.doctype: str | None = None
        self.comments: list[Text] = []
        self.parse_errors: list[str] = []

    def elements(self) -> Iterator[Element]:
        return self.root.descendants()

    def find(self, tag: str) -> list[Element]:
        return self.root.find(tag)


# Void elements never have children, so the builder must not push them onto the
# open-element stack. Getting this wrong reparents everything after an `<img>`.
VOID_ELEMENTS: Final[frozenset[str]] = frozenset(
    {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }
)


class _Builder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Document()
        self._stack: list[Element] = [self.document.root]

    @property
    def _current(self) -> Element:
        return self._stack[-1]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        merged = {name.lower(): (value if value is not None else "") for name, value in attrs}
        element = Element(tag.lower(), merged, self._current, line)
        self._current.children.append(element)
        if tag.lower() not in VOID_ELEMENTS:
            self._stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        merged = {name.lower(): (value if value is not None else "") for name, value in attrs}
        self._current.children.append(Element(tag.lower(), merged, self._current, line))

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == name:
                del self._stack[index:]
                return
        self.document.parse_errors.append(f"line {self.getpos()[0]}: stray </{name}>")

    def handle_data(self, data: str) -> None:
        self._current.children.append(Text(data, self.getpos()[0]))

    def handle_comment(self, data: str) -> None:
        node = Text(data, self.getpos()[0], is_comment=True)
        self.document.comments.append(node)

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.document.doctype = decl


def parse(source: str) -> Document:
    builder = _Builder()
    builder.feed(source)
    builder.close()
    return builder.document


# ------------------------------------------------------------------- utilities


def is_executed_script(element: Element) -> bool:
    """True when a `<script>` body is JavaScript the browser will run.

    A `<script type="text/template">` holding markup is data. Reading its body
    for DOM sinks reports the sink a template SHOWS rather than one the document
    USES, which is the false positive a raw string match cannot avoid.
    """
    if element.tag != "script":
        return False
    if "src" in element.attrs:
        return False
    declared = element.attrs.get("type", "").strip().lower()
    return declared in EXECUTED_SCRIPT_TYPES or "javascript" in declared


def executed_scripts(document: Document) -> list[Element]:
    return [e for e in document.elements() if is_executed_script(e)]


def host_of(url: str) -> str | None:
    """The lowercase hostname of an external URL, or None when it is not one.

    `data:`, `blob:`, `mailto:`, `tel:` and fragment or relative paths are all
    same-document or non-network and return None. Everything reaching the
    network returns a host, so an allowlist decision is never skipped silently.
    """
    value = url.strip()
    if not value or value.startswith("#"):
        return None
    if not ABSOLUTE_URL_RE.match(value):
        return None
    without_scheme = value.split("//", 1)[1]
    authority = without_scheme.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    if "@" in authority:
        authority = authority.rsplit("@", 1)[1]
    if authority.startswith("["):  # IPv6 literal
        return authority.split("]", 1)[0].lstrip("[").lower()
    return authority.split(":", 1)[0].lower() or None


def split_srcset(value: str) -> list[str]:
    return [item.strip().split()[0] for item in value.split(",") if item.strip()]


def sink_pattern(sink: str) -> re.Pattern[str]:
    """A word-bounded pattern for one sink name.

    `(?<![\\w$])` on the left refuses `myinnerHTML` while still matching the
    ordinary `node.innerHTML`, which is the whole point: a member access is how
    the sink is actually reached. An earlier edition of this function excluded
    `.` on the left as well, meaning to refuse `obj.innerHTMLish`. It refused
    every real call instead and passed a document that assigns straight through
    the sink. The right-hand `(?![\\w$])` already refuses that suffix case, and
    it is also what keeps `document.writeln` -- a different call the card does
    not block -- out of the report.
    """
    return re.compile(rf"(?<![\w$]){re.escape(sink)}(?![\w$])")


SINK_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (name, sink_pattern(name)) for name in BLOCKED_SINKS
)


def decoded_base64(blob: str) -> str | None:
    try:
        raw = base64.b64decode(blob + "=" * (-len(blob) % 4), validate=True)
    except (binascii.Error, ValueError):
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def gate(name: str, letter: str, issues: list[str], **extra: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "gate": letter,
        "name": name,
        "pass": not issues,
        "issues": issues,
    }
    record.update(extra)
    return record


def skipped_gate(name: str, letter: str, reason: str) -> dict[str, Any]:
    return {
        "gate": letter,
        "name": name,
        "pass": True,
        "skipped": True,
        "reason": reason,
        "issues": [],
    }


# ----------------------------------------------------------------------- gates


def gate_a_structure(document: Document) -> dict[str, Any]:
    """Gate A: the document is well-formed and stands on its own.

    Two halves. The first is that the shell exists: a doctype, one `html`, a
    `head`, a `body`, a non-empty `title`. The second is the SINGLE-FILE half,
    which is the one a byte scan gets wrong in both directions: a relative
    subresource means the artifact is not one file, while the identical string
    inside an `<a href>` is a link and costs nothing.
    """
    issues: list[str] = []

    if document.doctype is None:
        issues.append("no doctype declaration")
    html_elements = document.find("html")
    if not html_elements:
        issues.append("no <html> element")
    elif len(html_elements) > 1:
        issues.append(f"{len(html_elements)} <html> elements; a document has one")
    if not document.find("head"):
        issues.append("no <head> element")
    if not document.find("body"):
        issues.append("no <body> element")

    titles = document.find("title")
    if not titles:
        issues.append("no <title> element")
    elif not titles[0].text().strip():
        issues.append("<title> is empty")

    for error in document.parse_errors:
        issues.append(f"malformed markup: {error}")

    external_files: list[str] = []
    for element in document.elements():
        if element.tag not in SUBRESOURCE_ELEMENTS:
            continue
        for attribute in ("src", "href", "data", "poster"):
            value = element.attrs.get(attribute, "").strip()
            if not value or value.startswith(("#", "data:", "blob:")):
                continue
            if ABSOLUTE_URL_RE.match(value) or SCHEME_RE.match(value):
                continue  # a network URL: Gate B's subject, not this gate's
            external_files.append(f"<{element.tag} {attribute}=\"{value}\"> on line {element.line}")
    for reference in external_files:
        issues.append(f"separate file required, so the artifact is not single-file: {reference}")

    return gate(
        "single_file_structure",
        "A",
        issues,
        doctype=document.doctype,
        subresource_references=len(external_files),
    )


def gate_b_hosts(document: Document, allowlist: list[str]) -> dict[str, Any]:
    """Gate B: every host the document reaches was declared.

    Reads four regions, all located by the parser: URL attributes, `url()` in
    stylesheets and style attributes, and the network calls inside executed
    scripts. A host named in prose is not a connection and is not read here; a
    host that only appears once character references are decoded is.
    """
    issues: list[str] = []
    found: set[str] = set()
    allowed = {host.strip().lower() for host in allowlist if host.strip()}

    def judge(url: str, where: str) -> None:
        host = host_of(url)
        if host is None:
            return
        found.add(host)
        if host not in allowed:
            issues.append(f"undeclared host {host} ({where})")

    for element in document.elements():
        for attribute in URL_ATTRIBUTES:
            value = element.attrs.get(attribute)
            if not value:
                continue
            targets = split_srcset(value) if attribute == "srcset" else [value]
            for target in targets:
                judge(target, f"<{element.tag} {attribute}> line {element.line}")
        inline_style = element.attrs.get("style", "")
        for match in CSS_URL_RE.finditer(inline_style):
            judge(match.group(1), f"<{element.tag} style> line {element.line}")

    for style in document.find("style"):
        for match in CSS_URL_RE.finditer(style.text()):
            judge(match.group(1), f"<style> line {style.line}")

    for script in executed_scripts(document):
        body = script.text()
        for pattern, label in (
            (FETCH_URL_RE, "fetch"),
            (XHR_URL_RE, "XMLHttpRequest"),
            (WEBSOCKET_URL_RE, "WebSocket"),
        ):
            for match in pattern.finditer(body):
                judge(match.group(1), f"{label}() in <script> line {script.line}")

    return gate(
        "external_host_allowlist",
        "B",
        issues,
        declared_allowlist=sorted(allowed),
        hosts_seen=sorted(found),
    )


def gate_c_sinks(document: Document) -> dict[str, Any]:
    """Gate C: no blocked DOM sink is executed.

    Scope is executed script bodies and inline event handler attributes, and
    nothing else. The same identifier inside `<code>`, inside a comment, or
    inside a `<script type="text/template">` is not code this document runs, and
    reporting it would train a reader to ignore the gate.
    """
    issues: list[str] = []
    for script in executed_scripts(document):
        body = script.text()
        for name, pattern in SINK_PATTERNS:
            for match in pattern.finditer(body):
                offset = body.count("\n", 0, match.start())
                issues.append(
                    f"blocked sink {name} in <script> at line {script.line + offset}"
                )
    for element in document.elements():
        for attribute, value in element.attrs.items():
            if not INLINE_HANDLER_RE.match(attribute):
                continue
            for name, pattern in SINK_PATTERNS:
                if pattern.search(value):
                    issues.append(
                        f"blocked sink {name} in {attribute} on <{element.tag}> "
                        f"line {element.line}"
                    )
    return gate("blocked_dom_sinks", "C", issues, blocklist=list(BLOCKED_SINKS))


def gate_d_iconography(document: Document) -> dict[str, Any]:
    """Gate D: outlined SVG only, and no emoji in anything a reader sees.

    Rendered text, the accessibility attributes, and the fill of every shape
    inside an inline SVG. A `<script>` body and a comment are not rendered, so a
    pictograph in either passes -- which is the case a byte scan calls a defect.
    """
    issues: list[str] = []

    def rendered_text(element: Element) -> Iterator[tuple[str, int]]:
        for child in element.children:
            if isinstance(child, Text):
                if not child.is_comment:
                    yield child.data, child.line
            elif child.tag not in ("script", "style", "template"):
                yield from rendered_text(child)

    for data, line in rendered_text(document.root):
        for match in EMOJI_RE.finditer(data):
            issues.append(f"emoji {match.group(0)!r} in rendered text at line {line}")

    for element in document.elements():
        for attribute in RENDERED_ATTRIBUTES:
            value = element.attrs.get(attribute, "")
            for match in EMOJI_RE.finditer(value):
                issues.append(
                    f"emoji {match.group(0)!r} in {attribute} on <{element.tag}> "
                    f"line {element.line}"
                )

    filled = 0
    for svg in document.find("svg"):
        for shape in svg.descendants():
            fill = shape.attrs.get("fill", "").strip()
            if not fill or fill.lower() in OUTLINE_FILLS or fill.startswith("var("):
                continue
            filled += 1
            issues.append(
                f"filled icon: fill=\"{fill}\" on <{shape.tag}> inside inline SVG "
                f"at line {shape.line}"
            )

    return gate("iconography_outlined_svg_only", "D", issues, filled_shapes=filled)


def gate_e_csp(document: Document, mode: str) -> dict[str, Any]:
    """Gate E: the document is compatible with a strict content-security policy.

    In `netlify` mode this blocks: a deployed page carries a hard policy in
    `_headers`, and an inline handler or a style attribute would force
    `'unsafe-inline'` into it. In `artifact` mode the policy is advisory, so the
    same findings are reported and the gate does not fail on them.
    """
    if mode == "local_only":
        return skipped_gate(
            "content_security_policy", "E", "local_only mode deploys nothing"
        )

    findings: list[str] = []
    for element in document.elements():
        for attribute in element.attrs:
            if INLINE_HANDLER_RE.match(attribute):
                findings.append(
                    f"inline handler {attribute} on <{element.tag}> line {element.line} "
                    "requires 'unsafe-inline' in script-src"
                )
    style_attributes = [e for e in document.elements() if e.attrs.get("style")]
    if style_attributes:
        findings.append(
            f"{len(style_attributes)} style attribute(s) require 'unsafe-inline' in "
            f"style-src; first at line {style_attributes[0].line}"
        )

    meta_policy: str | None = None
    for meta in document.find("meta"):
        if meta.attrs.get("http-equiv", "").lower() == "content-security-policy":
            meta_policy = meta.attrs.get("content", "")
    if mode == "artifact" and meta_policy is None:
        findings.append("artifact mode states no <meta http-equiv=Content-Security-Policy>")

    blocking = mode == "netlify"
    return gate(
        "content_security_policy",
        "E",
        findings if blocking else [],
        enforcing=blocking,
        advisory_findings=[] if blocking else findings,
        meta_policy=meta_policy,
    )


def gate_f_secrets(document: Document) -> dict[str, Any]:
    """Gate F: no credential ships inside the artifact.

    Every region the parser can name is read, comments included: a comment ships
    in the file and a reader of the deployed page can open it. Values are read
    AFTER character-reference decoding, so a key written as `&#115;k_live_...`
    is judged on what it becomes rather than on how it was spelled.
    """
    issues: list[str] = []
    seen: set[str] = set()

    def judge(text: str, where: str) -> None:
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                key = f"{name}:{match.group(0)}"
                if key in seen:
                    continue
                seen.add(key)
                issues.append(f"{name} in {where}: {match.group(0)[:12]}...")
        for match in BASE64_BLOB_RE.finditer(text):
            decoded = decoded_base64(match.group(0))
            if decoded is None:
                continue
            for name, pattern in SECRET_PATTERNS:
                for hit in pattern.finditer(decoded):
                    key = f"{name}:base64:{hit.group(0)}"
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(f"{name} base64-encoded in {where}")

    def walk(element: Element) -> None:
        for child in element.children:
            if isinstance(child, Text):
                judge(child.data, f"text at line {child.line}")
            else:
                for attribute, value in child.attrs.items():
                    if value:
                        judge(value, f"{attribute} on <{child.tag}> line {child.line}")
                walk(child)

    walk(document.root)
    for comment in document.comments:
        judge(comment.data, f"comment at line {comment.line}")

    return gate("secret_exclusion", "F", issues)


# ------------------------------------------------------------------- the run


def in_scope(path: Path, source: str) -> tuple[bool, str]:
    """Whether this input is an HTML artifact this oracle judges.

    Refusal is a verdict, not an error. A card that answers "pass" on a Python
    file it never examined has told the reader something false.
    """
    suffix = path.suffix.lower()
    if suffix in HTML_SUFFIXES:
        return True, f"{suffix} is an HTML artifact"
    if suffix in NOT_HTML_SUFFIXES:
        return False, f"{suffix} is not an HTML artifact"
    if LOOKS_LIKE_HTML_RE.search(source):
        return True, "content declares an HTML document"
    return False, "no HTML document declaration and no HTML suffix"


def read_advisory(path: Path | None) -> tuple[str, list[dict[str, Any]], str | None]:
    """Load the optional taste provider's notes.

    Three outcomes and no fourth: absent, present, or degraded. A provider that
    cannot be read NEVER blocks the run, because the authority split says
    subjective beauty may not block completion, and a provider that is down is
    the weakest possible reason to stop.
    """
    if path is None:
        return "absent", [], None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return "degraded", [], f"{type(error).__name__}: {error}"
    notes = payload.get("notes") if isinstance(payload, dict) else payload
    if not isinstance(notes, list):
        return "degraded", [], "advisory payload states no notes list"
    return "present", [n for n in notes if isinstance(n, dict)], None


def audit(
    path: Path,
    source: str,
    mode: str,
    allowlist: list[str],
    advisory_path: Path | None = None,
    stamp: bool = True,
) -> tuple[dict[str, Any], int]:
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "tool": TOOL,
        "input": path.as_posix(),
        "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "input_bytes": len(source.encode("utf-8")),
        "mode": mode,
        "allowlist": sorted({h.strip().lower() for h in allowlist if h.strip()}),
    }
    if stamp:
        receipt["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    scoped, reason = in_scope(path, source)
    if not scoped:
        receipt.update(
            {
                "verdict": "REFUSED",
                "refusal_reason": reason,
                "gates": [],
                "gates_run": 0,
                "advisory_status": "not_consulted",
                "advisory_notes": [],
            }
        )
        return receipt, EXIT_REFUSED

    document = parse(source)
    gates = [
        gate_a_structure(document),
        gate_b_hosts(document, allowlist),
        gate_c_sinks(document),
        gate_d_iconography(document),
        gate_e_csp(document, mode),
        gate_f_secrets(document),
    ]
    status, notes, error = read_advisory(advisory_path)
    failed = [g["gate"] for g in gates if not g["pass"]]

    receipt.update(
        {
            "verdict": "PASS" if not failed else "FAIL",
            "gates": gates,
            "gates_run": len(gates),
            "gates_failed": failed,
            "advisory_status": status,
            "advisory_notes": notes,
            "advisory_error": error,
            # The authority split, stated in the receipt rather than only in the
            # prose, so a reader of the artifact can check that a provider note
            # never moved a verdict.
            "advisory_affected_verdict": False,
            "security_overrode_advisory": bool(failed and status == "present"),
        }
    )
    return receipt, EXIT_FAIL if failed else EXIT_PASS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL,
        description="Deterministic security oracle for a single-file HTML artifact.",
    )
    parser.add_argument("file", type=Path, help="the artifact to audit")
    parser.add_argument(
        "--mode",
        choices=RUNTIME_MODES,
        default="artifact",
        help="runtime mode; netlify enforces the strict policy gate",
    )
    parser.add_argument(
        "--allowlist",
        default="",
        help="comma-separated hosts the document may reach",
    )
    parser.add_argument(
        "--advisory",
        type=Path,
        default=None,
        help="optional taste provider notes as JSON; advisory only, never blocking",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=None,
        help="write the receipt here as well as to stdout",
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

    receipt, code = audit(
        args.file,
        source,
        args.mode,
        args.allowlist.split(",") if args.allowlist else [],
        args.advisory,
        stamp=not args.no_timestamp,
    )
    rendered = json.dumps(receipt, indent=2, ensure_ascii=True)
    print(rendered)
    if args.receipt is not None:
        args.receipt.write_text(rendered + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
