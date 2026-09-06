#!/usr/bin/env node
/**
 * emit_csp.mjs — Emit and validate Content-Security-Policy for single-file HTML.
 *
 * Two modes:
 *   emit   — parse the HTML, derive a CSP, emit the header
 *   validate — read an existing CSP header and check it against the document
 *
 * Parser-backed (htmlparser2 + domhandler). Emits structured JSON receipt to stdout.
 * Exit code 0 = valid, 1 = violations found, 2 = usage error.
 */
import { readFileSync } from "node:fs";
import { Parser } from "htmlparser2";
import { DomHandler } from "domhandler";

const VALID_MODES = ["emit", "validate"];
const VALID_DEPLOY = ["netlify", "artifact"];

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

function parseHtml(html) {
  return new Promise((resolve, reject) => {
    const handler = new DomHandler((err, dom) => {
      if (err) reject(err);
      else {
        const root = dom.find((n) => n.name === "html") || dom[0];
        resolve(root);
      }
    });
    const parser = new Parser(handler);
    parser.write(html);
    parser.end();
  });
}

// ─── Argument parsing ───────────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  const result = { action: "emit", deploy: "netlify", file: null, csp: null, allowlist: [] };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--action" || arg === "-a") {
      const val = args[++i];
      if (!val || !VALID_MODES.includes(val)) {
        console.error(`Error: --action must be one of: ${VALID_MODES.join(", ")}`);
        process.exit(2);
      }
      result.action = val;
    } else if (arg === "--deploy" || arg === "-d") {
      const val = args[++i];
      if (!val || !VALID_DEPLOY.includes(val)) {
        console.error(`Error: --deploy must be one of: ${VALID_DEPLOY.join(", ")}`);
        process.exit(2);
      }
      result.deploy = val;
    } else if (arg === "--csp") {
      result.csp = args[++i];
    } else if (arg === "--allowlist") {
      result.allowlist = (args[++i] || "").split(",").map((h) => h.trim().toLowerCase());
    } else if (arg === "--help" || arg === "-h") {
      console.error(
        "Usage: emit_csp.mjs <file.html> [--action emit|validate] [--deploy netlify|artifact] [--csp 'policy'] [--allowlist h1,h2]"
      );
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

// ─── Source discovery ───────────────────────────────────────────────────

function discoverSources(doc) {
  const scriptSrc = new Set();
  const styleSrc = new Set();
  const imgSrc = new Set();
  const connectSrc = new Set();
  const fontSrc = new Set();
  const frameSrc = new Set();
  let hasInlineScript = false;
  let hasInlineStyle = false;
  let hasUnsafeEval = false;

  const scripts = findAll(doc, "script");
  for (const s of scripts) {
    const src = getAttr(s, "src");
    if (src) {
      try {
        const url = new URL(src);
        if (url.protocol === "https:" || url.protocol === "http:") scriptSrc.add(url.hostname);
      } catch { /* relative */ }
    } else if (textContent(s).trim()) {
      hasInlineScript = true;
      if (/\beval\s*\(/.test(textContent(s))) hasUnsafeEval = true;
    }
  }

  const styleEls = findAll(doc, "style");
  for (const s of styleEls) {
    const text = textContent(s);
    if (text.trim()) hasInlineStyle = true;
    const importRe = /@import\s+["']?(https?:\/\/[^"'\s;]+)/gi;
    let m;
    while ((m = importRe.exec(text))) {
      try { fontSrc.add(new URL(m[1]).hostname); } catch { /* not a URL */ }
    }
    const urlRe = /url\(\s*["']?(https?:\/\/[^)"'\s]+)/gi;
    while ((m = urlRe.exec(text))) {
      try {
        const url = new URL(m[1]);
        if (/\.(woff2?|ttf|otf|eot)/i.test(url.pathname)) fontSrc.add(url.hostname);
        else if (/\.(png|jpe?g|gif|svg|webp|ico)/i.test(url.pathname)) imgSrc.add(url.hostname);
        else connectSrc.add(url.hostname);
      } catch { /* not a URL */ }
    }
  }

  const elementsWithStyle = findByAttr(doc, "style");
  if (elementsWithStyle.length > 0) hasInlineStyle = true;

  const imgs = findAll(doc, "img");
  for (const img of imgs) {
    const src = getAttr(img, "src");
    if (!src) continue;
    try {
      const url = new URL(src);
      if (url.protocol === "https:" || url.protocol === "http:") imgSrc.add(url.hostname);
    } catch { /* relative */ }
  }

  const links = findAll(doc, "link");
  for (const link of links) {
    const href = getAttr(link, "href");
    if (!href) continue;
    const rel = (getAttr(link, "rel") || "").toLowerCase();
    try {
      const url = new URL(href);
      if (url.protocol === "https:" || url.protocol === "http:") {
        if (rel === "stylesheet") styleSrc.add(url.hostname);
        else if (rel === "icon" || rel === "shortcut icon") imgSrc.add(url.hostname);
        else if (rel === "preload" || rel === "prefetch") {
          const type = getAttr(link, "as") || "";
          if (type === "font") fontSrc.add(url.hostname);
          else if (type === "image") imgSrc.add(url.hostname);
          else connectSrc.add(url.hostname);
        } else connectSrc.add(url.hostname);
      }
    } catch { /* relative */ }
  }

  const iframes = findAll(doc, "iframe");
  for (const f of iframes) {
    const src = getAttr(f, "src");
    if (!src) continue;
    try {
      const url = new URL(src);
      if (url.protocol === "https:" || url.protocol === "http:") frameSrc.add(url.hostname);
    } catch { /* relative */ }
  }

  return {
    scriptSrc: [...scriptSrc],
    styleSrc: [...styleSrc],
    imgSrc: [...imgSrc],
    connectSrc: [...connectSrc],
    fontSrc: [...fontSrc],
    frameSrc: [...frameSrc],
    hasInlineScript,
    hasInlineStyle,
    hasUnsafeEval,
  };
}

// ─── CSP building ───────────────────────────────────────────────────────

function buildCsp(sources, deploy, allowlist) {
  const directives = [];
  directives.push("default-src 'none'");

  const scriptParts = [];
  if (sources.hasInlineScript) { scriptParts.push("'unsafe-hashes'"); scriptParts.push("'sha256-...'"); }
  if (sources.hasUnsafeEval) scriptParts.push("'unsafe-eval'");
  for (const h of [...sources.scriptSrc, ...allowlist]) {
    if (!scriptParts.includes(h)) scriptParts.push(`https://${h}`);
  }
  directives.push(`script-src ${scriptParts.length ? scriptParts.join(" ") : "'none'"}`);

  const styleParts = [];
  if (sources.hasInlineStyle) styleParts.push("'unsafe-inline'");
  for (const h of [...sources.styleSrc, ...allowlist]) {
    if (!styleParts.includes(h)) styleParts.push(`https://${h}`);
  }
  directives.push(`style-src ${styleParts.length ? styleParts.join(" ") : "'none'"}`);

  const imgParts = ["'self'", "data:"];
  for (const h of [...sources.imgSrc, ...allowlist]) {
    if (!imgParts.includes(h)) imgParts.push(`https://${h}`);
  }
  directives.push(`img-src ${imgParts.join(" ")}`);

  const connectParts = [];
  for (const h of [...sources.connectSrc, ...allowlist]) connectParts.push(`https://${h}`);
  directives.push(`connect-src ${deploy === "netlify" ? (connectParts.length ? connectParts.join(" ") : "'none'") : (connectParts.length ? connectParts.join(" ") : "'self'")}`);

  const fontParts = ["'self'", "data:"];
  for (const h of [...sources.fontSrc, ...allowlist]) {
    if (!fontParts.includes(h)) fontParts.push(`https://${h}`);
  }
  directives.push(`font-src ${fontParts.join(" ")}`);

  if (sources.frameSrc.length) {
    directives.push(`frame-src ${sources.frameSrc.map((h) => `https://${h}`).join(" ")}`);
  }

  directives.push("base-uri 'self'");
  directives.push("form-action 'self'");
  return directives.join("; ");
}

function validateCsp(existingCsp, sources) {
  const violations = [];
  const directives = {};
  for (const part of existingCsp.split(";")) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    const [name, ...values] = trimmed.split(/\s+/);
    directives[name.toLowerCase()] = values;
  }

  if (!directives["default-src"] || !directives["default-src"].includes("'none'")) {
    violations.push("default-src should be 'none' for strict CSP");
  }
  const scriptSrc = directives["script-src"] || [];
  if (scriptSrc.includes("'unsafe-inline'")) violations.push("script-src must not include 'unsafe-inline'");
  for (const h of sources.scriptSrc) {
    if (!scriptSrc.some((s) => s.includes(h) || s === "'self'")) {
      violations.push(`script-src missing declared host: ${h}`);
    }
  }
  const connectSrc = directives["connect-src"] || [];
  if (connectSrc.includes("'none'") && sources.connectSrc.length > 0) {
    violations.push(`connect-src is 'none' but document connects to: ${sources.connectSrc.join(", ")}`);
  }
  if (!directives["form-action"] || !directives["form-action"].includes("'self'")) {
    violations.push("form-action should include 'self'");
  }
  if (!directives["base-uri"] || !directives["base-uri"].includes("'self'")) {
    violations.push("base-uri should include 'self'");
  }
  return violations;
}

// ─── Main ───────────────────────────────────────────────────────────────

async function main() {
  const config = parseArgs(process.argv);

  let rawContent;
  try { rawContent = readFileSync(config.file, "utf-8"); }
  catch (err) { console.error(`Error: cannot read ${config.file}: ${err.message}`); process.exit(2); }

  const doc = await parseHtml(rawContent);
  const sources = discoverSources(doc);

  let receipt;
  if (config.action === "emit") {
    const policy = buildCsp(sources, config.deploy, config.allowlist);
    receipt = {
      tool: "emit_csp.mjs", action: "emit", input: config.file, deploy: config.deploy,
      allowlist: config.allowlist, timestamp: new Date().toISOString(), discovered_sources: sources,
      policy, directives: Object.fromEntries(policy.split("; ").map((d) => { const [name, ...rest] = d.split(" "); return [name, rest.join(" ")]; })),
    };
  } else {
    if (!config.csp) { console.error("Error: --csp required for validate action"); process.exit(2); }
    const violations = validateCsp(config.csp, sources);
    receipt = {
      tool: "emit_csp.mjs", action: "validate", input: config.file, timestamp: new Date().toISOString(),
      discovered_sources: sources, existing_csp: config.csp, violations, valid: violations.length === 0,
    };
  }

  process.stdout.write(JSON.stringify(receipt, null, 2) + "\n");
  process.exit(config.action === "emit" ? 0 : receipt.valid ? 0 : 1);
}

main();
