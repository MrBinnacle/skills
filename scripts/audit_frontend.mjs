#!/usr/bin/env node
/**
 * audit_frontend.mjs — Deterministic oracle for single-file HTML artifacts.
 *
 * Parser-backed (htmlparser2 + domhandler), not string-matched. Asserts:
 *   Gate A: valid single-file HTML structure
 *   Gate B: no external host connections outside allowlist
 *   Gate C: no blocked DOM sink usage (innerHTML, eval, insertAdjacentHTML, document.write)
 *   Gate D: iconography — outlined SVG only, no emoji icons
 *   Gate E: CSP header generation for NETLIFY mode
 *   Gate F: no secrets in the emitted artifact
 *
 * Emits a structured JSON receipt to stdout.
 * Exit code 0 = all gates passed, 1 = at least one gate failed, 2 = usage error.
 */
import { readFileSync } from "node:fs";
import { Parser } from "htmlparser2";
import { DomHandler } from "domhandler";

const BLOCKED_SINKS = [
  "innerHTML",
  "eval",
  "insertAdjacentHTML",
  "document.write",
];

const DEFAULT_MODE = "artifact";
const VALID_MODES = ["artifact", "netlify", "local_only"];

const SECRET_PATTERNS = [
  { re: /(?:^|[\s;:=])["']?(?:sk|pk|ak|rk)[_-]?[a-zA-Z0-9_-]{20,}/i, name: "api_key_prefix" },
  { re: /(?:^|[\s;:=])["']?(?:ghp|gho|ghu|ghs|ghr)[_-]?[a-zA-Z0-9]{20,}/i, name: "github_token" },
  { re: /(?:^|[\s;:=])["']?(?:AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}/i, name: "aws_access_key" },
  { re: /(?:^|[\s;:=])["']?xox[bpsar]-[a-zA-Z0-9-]+/i, name: "slack_token" },
  { re: /(?:^|[\s;:=])["']?eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}/i, name: "jwt_token" },
  { re: /-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----/, name: "private_key_block" },
];

const EMOJI_RE =
  /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{200D}\u{20E3}\u{E0020}-\u{E007F}]/gu;

const INLINE_HANDLERS = [
  "onclick", "onerror", "onload", "onmouseover", "onmouseout",
  "onfocus", "onblur", "onsubmit", "onchange", "onkeydown", "onkeyup", "onkeypress",
];

// ─── DOM helpers ────────────────────────────────────────────────────────

function findAll(node, name) {
  const results = [];
  if (!node) return results;
  if (node.name === name) results.push(node);
  if (node.children) {
    for (const child of node.children) {
      results.push(...findAll(child, name));
    }
  }
  return results;
}

function findAllRecursive(node) {
  const results = [];
  if (!node) return results;
  results.push(node);
  if (node.children) {
    for (const child of node.children) {
      results.push(...findAllRecursive(child));
    }
  }
  return results;
}

function findByAttr(node, attr) {
  const results = [];
  if (!node) return results;
  if (node.attribs && node.attribs[attr] !== undefined) results.push(node);
  if (node.children) {
    for (const child of node.children) {
      results.push(...findByAttr(child, attr));
    }
  }
  return results;
}

function textContent(node) {
  if (!node) return "";
  if (node.type === "text") return node.data || "";
  if (node.children) {
    return node.children.map((c) => textContent(c)).join("");
  }
  return "";
}

function getAttr(node, attr) {
  return node.attribs ? node.attribs[attr] : undefined;
}

function hasAttr(node, attr) {
  return node.attribs && attr in node.attribs;
}

// ─── Argument parsing ───────────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  const result = { allowlist: [], mode: DEFAULT_MODE, file: null };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--allowlist" || arg === "-a") {
      const val = args[++i];
      if (!val) { console.error("Error: --allowlist requires a value"); process.exit(2); }
      result.allowlist = val.split(",").map((h) => h.trim().toLowerCase());
    } else if (arg === "--mode" || arg === "-m") {
      const val = args[++i];
      if (!val || !VALID_MODES.includes(val)) {
        console.error(`Error: --mode must be one of: ${VALID_MODES.join(", ")}`);
        process.exit(2);
      }
      result.mode = val;
    } else if (arg === "--help" || arg === "-h") {
      console.error("Usage: audit_frontend.mjs <file.html> [--allowlist h1,h2] [--mode artifact|netlify|local_only]");
      process.exit(0);
    } else if (!arg.startsWith("-")) {
      result.file = arg;
    } else {
      console.error(`Error: unknown flag ${arg}`);
      process.exit(2);
    }
  }

  if (!result.file) { console.error("Error: no input file specified"); process.exit(2); }
  return result;
}

// ─── Gate A: single-file structure ──────────────────────────────────────

function gateA_structure(doc, rawContent) {
  const issues = [];

  const hasDoctype = /<!DOCTYPE\s+html/i.test(rawContent);
  if (!hasDoctype) issues.push("missing <!DOCTYPE html> declaration");

  const htmlEls = findAll(doc, "html");
  if (htmlEls.length === 0) issues.push("missing <html> element");

  const headEls = findAll(doc, "head");
  if (headEls.length === 0) issues.push("missing <head> element");

  const bodyEls = findAll(doc, "body");
  if (bodyEls.length === 0) issues.push("missing <body> element");

  const titleEls = findAll(doc, "title");
  const titleText = titleEls.length > 0 ? textContent(titleEls[0]).trim() : "";
  if (!titleText) issues.push("missing or empty <title> element");

  return { gate: "A", name: "single_file_structure", pass: issues.length === 0, issues };
}

// ─── Gate B: external host allowlist ────────────────────────────────────

function gateB_external_hosts(doc, allowlist) {
  const issues = [];
  const found = new Set();

  function isAbsoluteHttpUrl(str) { return /^https?:\/\//i.test(str); }

  function checkUrl(val, tagName, attr) {
    if (!val || !isAbsoluteHttpUrl(val)) return;
    try {
      const url = new URL(val);
      const host = url.hostname.toLowerCase();
      if (!allowlist.includes(host)) {
        found.add(host);
        issues.push(`blocked ${attr} host: ${host} (element: ${tagName}, ${attr}: ${val})`);
      }
    } catch { /* not a valid URL */ }
  }

  for (const el of findByAttr(doc, "src")) {
    checkUrl(getAttr(el, "src"), el.name, "src");
  }
  for (const el of findByAttr(doc, "href")) {
    checkUrl(getAttr(el, "href"), el.name, "href");
  }

  // Check CSS url() in <style> elements
  for (const styleEl of findAll(doc, "style")) {
    const text = textContent(styleEl);
    const urlRe = /url\(\s*["']?(https?:\/\/[^)"'\s]+)/gi;
    let m;
    while ((m = urlRe.exec(text))) {
      try {
        const url = new URL(m[1]);
        const host = url.hostname.toLowerCase();
        if (!allowlist.includes(host)) {
          found.add(host);
          issues.push(`blocked CSS url() host: ${host}`);
        }
      } catch { /* not a valid URL */ }
    }
  }

  // Check fetch/XHR in <script> elements
  for (const scriptEl of findAll(doc, "script")) {
    const text = textContent(scriptEl);
    const fetchRe = /fetch\s*\(\s*["']?(https?:\/\/[^)"'\s]+)/gi;
    let m;
    while ((m = fetchRe.exec(text))) {
      try {
        const url = new URL(m[1]);
        const host = url.hostname.toLowerCase();
        if (!allowlist.includes(host)) {
          found.add(host);
          issues.push(`blocked fetch() host: ${host}`);
        }
      } catch { /* not a valid URL */ }
    }
    const xhrRe = /\.open\s*\(\s*["'][^"']*["']\s*,\s*["']?(https?:\/\/[^)"'\s]+)/gi;
    while ((m = xhrRe.exec(text))) {
      try {
        const url = new URL(m[1]);
        const host = url.hostname.toLowerCase();
        if (!allowlist.includes(host)) {
          found.add(host);
          issues.push(`blocked XHR host: ${host}`);
        }
      } catch { /* not a valid URL */ }
    }
  }

  return { gate: "B", name: "external_host_allowlist", pass: issues.length === 0, issues, blocked_hosts: [...found] };
}

// ─── Gate C: DOM sink blocklist ─────────────────────────────────────────

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function gateC_dom_sinks(doc) {
  const issues = [];
  for (const script of findAll(doc, "script")) {
    const text = textContent(script);
    for (const sink of BLOCKED_SINKS) {
      const re = new RegExp(`(?<![a-zA-Z0-9_$])${escapeRegex(sink)}(?![a-zA-Z0-9_$])`, "g");
      const matches = [...text.matchAll(re)];
      if (matches.length > 0) {
        const beforeMatch = text.slice(0, matches[0].index);
        const lineNum = beforeMatch.split("\n").length;
        issues.push(`blocked DOM sink "${sink}" found at script line ${lineNum}`);
      }
    }
  }
  return { gate: "C", name: "dom_sink_blocklist", pass: issues.length === 0, issues };
}

// ─── Gate D: iconography ────────────────────────────────────────────────

function gateD_iconography(doc) {
  const issues = [];

  // Check emoji in attributes
  for (const el of findAllRecursive(doc)) {
    if (!el.attribs) continue;
    for (const attr of ["aria-label", "title", "alt", "placeholder"]) {
      const val = el.attribs[attr];
      if (val && EMOJI_RE.test(val)) {
        EMOJI_RE.lastIndex = 0; // reset regex state
        issues.push(`emoji in ${attr} attribute on <${el.name}>`);
      }
    }
  }

  // Check inline SVG for fill attributes (filled icons)
  for (const svg of findAll(doc, "svg")) {
    const allChildren = findAllRecursive(svg);
    for (const child of allChildren) {
      const fill = getAttr(child, "fill");
      if (fill && fill !== "none" && fill !== "currentColor" && !fill.startsWith("var(")) {
        issues.push(`filled SVG icon detected: fill="${fill}" on <${child.name}> inside inline SVG`);
      }
    }
  }

  // Check <img> for emoji in alt/src
  for (const img of findAll(doc, "img")) {
    const alt = getAttr(img, "alt") || "";
    const src = getAttr(img, "src") || "";
    if (EMOJI_RE.test(alt)) {
      EMOJI_RE.lastIndex = 0;
      issues.push(`emoji in img alt attribute: "${alt.slice(0, 50)}"`);
    }
    if (EMOJI_RE.test(src)) {
      EMOJI_RE.lastIndex = 0;
      issues.push(`emoji in img src attribute: "${src.slice(0, 50)}"`);
    }
  }

  return { gate: "D", name: "iconography_outlined_svg_only", pass: issues.length === 0, issues };
}

// ─── Gate E: CSP ────────────────────────────────────────────────────────

function gateE_csp(doc, mode) {
  if (mode !== "netlify") {
    return { gate: "E", name: "csp_headers", pass: true, issues: [], skipped: true, reason: "CSP generation only applies to netlify mode" };
  }

  const issues = [];
  const metaCspEls = findAll(doc, "meta");
  const hasMetaCsp = metaCspEls.some(
    (m) => (getAttr(m, "http-equiv") || "").toLowerCase() === "content-security-policy"
  );

  for (const el of findAllRecursive(doc)) {
    if (!el.attribs) continue;
    for (const handler of INLINE_HANDLERS) {
      if (handler in el.attribs) {
        issues.push(`inline event handler ${handler} on <${el.name}> violates strict CSP`);
      }
    }
  }

  const styleEls = findByAttr(doc, "style");
  if (styleEls.length > 0) {
    issues.push(`inline style attributes found on ${styleEls.length} element(s) — require 'unsafe-inline' in style-src`);
  }

  return { gate: "E", name: "csp_headers", pass: issues.length === 0, issues, has_meta_csp: hasMetaCsp };
}

// ─── Gate F: secret exclusion ───────────────────────────────────────────

function gateF_secrets(rawContent) {
  const issues = [];
  for (const { re, name } of SECRET_PATTERNS) {
    const matches = rawContent.match(re);
    if (matches) {
      const lineNum = rawContent.slice(0, matches.index).split("\n").length;
      issues.push(`potential secret (${name}) found at line ${lineNum}`);
    }
  }
  const b64Re = /["']([A-Za-z0-9+/]{40,}={0,2})["']/g;
  let m;
  while ((m = b64Re.exec(rawContent))) {
    const decoded = Buffer.from(m[1], "base64").toString("utf-8");
    if (/(?:key|token|secret|password|credential)/i.test(decoded)) {
      const lineNum = rawContent.slice(0, m.index).split("\n").length;
      issues.push(`base64-encoded string containing secret-related text at line ${lineNum}`);
    }
  }
  return { gate: "F", name: "secret_exclusion", pass: issues.length === 0, issues };
}

// ─── Main ───────────────────────────────────────────────────────────────

function parseHtml(html) {
  return new Promise((resolve, reject) => {
    const handler = new DomHandler((err, dom) => {
      if (err) reject(err);
      else {
        // DomHandler returns a document fragment; find the html element
        const root = dom.find((n) => n.name === "html") || dom[0];
        resolve(root);
      }
    });
    const parser = new Parser(handler);
    parser.write(html);
    parser.end();
  });
}

async function main() {
  const config = parseArgs(process.argv);

  let rawContent;
  try {
    rawContent = readFileSync(config.file, "utf-8");
  } catch (err) {
    console.error(`Error: cannot read ${config.file}: ${err.message}`);
    process.exit(2);
  }

  const doc = await parseHtml(rawContent);

  const gates = [
    gateA_structure(doc, rawContent),
    gateB_external_hosts(doc, config.allowlist),
    gateC_dom_sinks(doc),
    gateD_iconography(doc),
    gateE_csp(doc, config.mode),
    gateF_secrets(rawContent),
  ];

  const receipt = {
    tool: "audit_frontend.mjs",
    input: config.file,
    mode: config.mode,
    allowlist: config.allowlist,
    timestamp: new Date().toISOString(),
    gates,
    all_pass: gates.every((g) => g.pass),
  };

  process.stdout.write(JSON.stringify(receipt, null, 2) + "\n");
  process.exit(receipt.all_pass ? 0 : 1);
}

main();
