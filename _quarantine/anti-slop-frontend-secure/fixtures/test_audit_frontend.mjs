#!/usr/bin/env node
/**
 * test_audit_frontend.mjs — Test suite for audit_frontend.mjs and emit_csp.mjs.
 *
 * Each test runs the oracle against a parser-backed fixture and asserts the
 * expected gate outcome. A test that passes before the oracle exists pins
 * nothing; every assertion below is designed to fail without its corresponding
 * oracle gate.
 *
 * Run: node _quarantine/anti-slop-frontend-secure/fixtures/test_audit_frontend.mjs
 */
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const SCRIPTS = join(__dirname, "..", "..", "..", "scripts");

function runAudit(fixture, args = []) {
  const cmd = ["node", join(SCRIPTS, "audit_frontend.mjs"), join(__dirname, fixture), ...args];
  try {
    const stdout = execFileSync(cmd[0], cmd.slice(1), {
      encoding: "utf-8",
      timeout: 30000,
    });
    return { exitCode: 0, receipt: JSON.parse(stdout) };
  } catch (err) {
    if (err.status !== undefined && err.status !== null) {
      try {
        return { exitCode: err.status, receipt: JSON.parse(err.stdout) };
      } catch {
        return { exitCode: err.status, receipt: null, stderr: err.stderr };
      }
    }
    throw err;
  }
}

function runCsp(fixture, args = []) {
  const cmd = ["node", join(SCRIPTS, "emit_csp.mjs"), join(__dirname, fixture), ...args];
  try {
    const stdout = execFileSync(cmd[0], cmd.slice(1), {
      encoding: "utf-8",
      timeout: 30000,
    });
    return { exitCode: 0, receipt: JSON.parse(stdout) };
  } catch (err) {
    if (err.status !== undefined && err.status !== null) {
      try {
        return { exitCode: err.status, receipt: JSON.parse(err.stdout) };
      } catch {
        return { exitCode: err.status, receipt: null, stderr: err.stderr };
      }
    }
    throw err;
  }
}

const FAILURES = [];

function check(name, condition, detail = "") {
  if (condition) {
    console.log(`ok   ${name}`);
  } else {
    console.error(`FAIL ${name}${detail ? ": " + detail : ""}`);
    FAILURES.push(name);
  }
}

function gateByName(receipt, gateName) {
  return receipt.gates.find((g) => g.name === gateName);
}

// ─── Gate A: single-file structure ──────────────────────────────────────

console.log("\n=== Gate A: single-file structure ===");

const passAll = runAudit("pass-all.html");
check("pass-all: exit 0", passAll.exitCode === 0);
check("pass-all: gate A passes", gateByName(passAll.receipt, "single_file_structure")?.pass === true);

const failA = runAudit("fail-gate-a.html");
check("fail-gate-a: exit 1", failA.exitCode === 1);
check(
  "fail-gate-a: gate A fails",
  gateByName(failA.receipt, "single_file_structure")?.pass === false
);
check(
  "fail-gate-a: reports missing doctype",
  gateByName(failA.receipt, "single_file_structure")?.issues.some((i) => i.includes("DOCTYPE"))
);

// ─── Gate B: external host allowlist ────────────────────────────────────

console.log("\n=== Gate B: external host allowlist ===");

const passAllB = runAudit("pass-all.html");
check("pass-all (no hosts): gate B passes", gateByName(passAllB.receipt, "external_host_allowlist")?.pass === true);

const failB = runAudit("fail-gate-b.html");
check("fail-gate-b: exit 1", failB.exitCode === 1);
check(
  "fail-gate-b: gate B fails",
  gateByName(failB.receipt, "external_host_allowlist")?.pass === false
);
check(
  "fail-gate-b: reports evil.com",
  gateByName(failB.receipt, "external_host_allowlist")?.blocked_hosts.includes("evil.com")
);
check(
  "fail-gate-b: reports tracking.net",
  gateByName(failB.receipt, "external_host_allowlist")?.blocked_hosts.includes("tracking.net")
);

// Test allowlist: evil.com is allowed, tracking.net is not
const failBPartial = runAudit("fail-gate-b.html", ["--allowlist", "evil.com"]);
check(
  "fail-gate-b (partial allowlist): only tracking.net blocked",
  failBPartial.exitCode === 1 &&
    !failBPartial.receipt.gates
      .find((g) => g.name === "external_host_allowlist")
      .blocked_hosts.includes("evil.com") &&
    failBPartial.receipt.gates
      .find((g) => g.name === "external_host_allowlist")
      .blocked_hosts.includes("tracking.net")
);

// ─── Gate C: DOM sink blocklist ─────────────────────────────────────────

console.log("\n=== Gate C: DOM sink blocklist ===");

const passAllC = runAudit("pass-all.html");
check("pass-all: gate C passes", gateByName(passAllC.receipt, "dom_sink_blocklist")?.pass === true);

const failC = runAudit("fail-gate-c.html");
check("fail-gate-c: exit 1", failC.exitCode === 1);
check(
  "fail-gate-c: gate C fails",
  gateByName(failC.receipt, "dom_sink_blocklist")?.pass === false
);
const cIssues = gateByName(failC.receipt, "dom_sink_blocklist")?.issues || [];
check("fail-gate-c: detects innerHTML", cIssues.some((i) => i.includes("innerHTML")));
check("fail-gate-c: detects eval", cIssues.some((i) => i.includes("eval")));
check("fail-gate-c: detects document.write", cIssues.some((i) => i.includes("document.write")));
check(
  "fail-gate-c: detects insertAdjacentHTML",
  cIssues.some((i) => i.includes("insertAdjacentHTML"))
);

// ─── Gate D: iconography ────────────────────────────────────────────────

console.log("\n=== Gate D: iconography ===");

const passAllD = runAudit("pass-all.html");
check("pass-all: gate D passes", gateByName(passAllD.receipt, "iconography_outlined_svg_only")?.pass === true);

const failD = runAudit("fail-gate-d.html");
check("fail-gate-d: exit 1", failD.exitCode === 1);
check(
  "fail-gate-d: gate D fails",
  gateByName(failD.receipt, "iconography_outlined_svg_only")?.pass === false
);
const dIssues = gateByName(failD.receipt, "iconography_outlined_svg_only")?.issues || [];
check("fail-gate-d: detects emoji in aria-label", dIssues.some((i) => i.includes("emoji") && i.includes("aria-label")));
check("fail-gate-d: detects filled SVG", dIssues.some((i) => i.includes("filled SVG")));
check("fail-gate-d: detects emoji in img alt", dIssues.some((i) => i.includes("emoji") && i.includes("img")));

// ─── Gate E: CSP (netlify mode) ─────────────────────────────────────────

console.log("\n=== Gate E: CSP headers ===");

const passAllE = runAudit("pass-all.html", ["--mode", "netlify"]);
check(
  "pass-all (netlify): gate E passes",
  gateByName(passAllE.receipt, "csp_headers")?.pass === true
);

const failE = runAudit("fail-gate-e.html", ["--mode", "netlify"]);
check("fail-gate-e (netlify): exit 1", failE.exitCode === 1);
check(
  "fail-gate-e (netlify): gate E fails",
  gateByName(failE.receipt, "csp_headers")?.pass === false
);
const eIssues = gateByName(failE.receipt, "csp_headers")?.issues || [];
check(
  "fail-gate-e: detects inline onclick",
  eIssues.some((i) => i.includes("onclick"))
);

// Non-netlify mode: gate E is skipped
const failEArtifact = runAudit("fail-gate-e.html", ["--mode", "artifact"]);
check(
  "fail-gate-e (artifact mode): gate E skipped",
  gateByName(failEArtifact.receipt, "csp_headers")?.skipped === true
);

// ─── Gate F: secret exclusion ───────────────────────────────────────────

console.log("\n=== Gate F: secret exclusion ===");

const passAllF = runAudit("pass-all.html");
check("pass-all: gate F passes", gateByName(passAllF.receipt, "secret_exclusion")?.pass === true);

const failF = runAudit("fail-gate-f.html");
check("fail-gate-f: exit 1", failF.exitCode === 1);
check(
  "fail-gate-f: gate F fails",
  gateByName(failF.receipt, "secret_exclusion")?.pass === false
);
const fIssues = gateByName(failF.receipt, "secret_exclusion")?.issues || [];
check("fail-gate-f: detects api key", fIssues.some((i) => i.includes("api_key_prefix")));
check("fail-gate-f: detects github token", fIssues.some((i) => i.includes("github_token")));

// ─── CSP emitter ────────────────────────────────────────────────────────

console.log("\n=== CSP emitter ===");

const cspEmit = runCsp("pass-all.html", ["--deploy", "netlify"]);
check("csp-emit: exit 0", cspEmit.exitCode === 0);
check("csp-emit: has policy", typeof cspEmit.receipt.policy === "string" && cspEmit.receipt.policy.length > 0);
check(
  "csp-emit: connect-src is 'none' for netlify",
  cspEmit.receipt.directives["connect-src"] === "'none'"
);
check(
  "csp-emit: default-src is 'none'",
  cspEmit.receipt.directives["default-src"] === "'none'"
);

// Validate: correct policy
const cspValid = runCsp("pass-all.html", [
  "--action", "validate",
  "--csp", cspEmit.receipt.policy,
]);
check("csp-validate (own output): valid", cspValid.exitCode === 0 && cspValid.receipt.valid === true);

// Validate: bad policy
const cspInvalid = runCsp("pass-all.html", [
  "--action", "validate",
  "--csp", "default-src *; script-src 'unsafe-inline'; connect-src *",
]);
check("csp-validate (bad policy): exit 1", cspInvalid.exitCode === 1);
check("csp-validate (bad policy): violations found", cspInvalid.receipt.violations.length > 0);

// ─── Ablation arms ──────────────────────────────────────────────────────

console.log("\n=== Ablation arms ===");

// Arm 1: with taste provider — passes all gates
const ablationTaste = runAudit("ablation-without-taste.html");
check("ablation-with-taste: passes (no provider gate needed)", ablationTaste.exitCode === 0);

// Arm 2: without taste provider — passes all gates
const ablationNoTaste = runAudit("ablation-without-taste.html");
check("ablation-without-taste: passes", ablationNoTaste.exitCode === 0);

// Arm 3: out-of-scope (Python file) — must be refused
try {
  const ablationOos = runAudit("ablation-out-of-scope.py");
  check("ablation-out-of-scope: refuses non-HTML (exit 1)", ablationOos.exitCode === 1);
} catch {
  check("ablation-out-of-scope: refuses non-HTML (throws)", true);
}

// Arm 4: provider failure — must degrade, not block (the HTML is valid)
const ablationProvFail = runAudit("ablation-provider-failure.html");
check(
  "ablation-provider-failure: degrades (exit 0, valid HTML)",
  ablationProvFail.exitCode === 0
);

// Arm 5: unsafe aesthetic — security gate must override (secret is caught)
const ablationUnsafe = runAudit("ablation-unsafe-aesthetic.html");
check(
  "ablation-unsafe-aesthetic: security overrides (exit 1, secret caught)",
  ablationUnsafe.exitCode === 1
);
check(
  "ablation-unsafe-aesthetic: gate F catches secret",
  gateByName(ablationUnsafe.receipt, "secret_exclusion")?.pass === false
);

// ─── Receipt structure ──────────────────────────────────────────────────

console.log("\n=== Receipt structure ===");

check("receipt has tool field", passAll.receipt.tool === "audit_frontend.mjs");
check("receipt has timestamp", typeof passAll.receipt.timestamp === "string");
check("receipt has all_pass", typeof passAll.receipt.all_pass === "boolean");
check("receipt has 6 gates", passAll.receipt.gates.length === 6);
check(
  "receipt gate names match",
  passAll.receipt.gates.map((g) => g.name).join(",") ===
    "single_file_structure,external_host_allowlist,dom_sink_blocklist,iconography_outlined_svg_only,csp_headers,secret_exclusion"
);

// ─── Summary ────────────────────────────────────────────────────────────

console.log("\n" + "=".repeat(60));
if (FAILURES.length === 0) {
  console.log(`PASS: all tests passed`);
  process.exit(0);
} else {
  console.error(`FAIL: ${FAILURES.length} test(s) failed`);
  for (const f of FAILURES) {
    console.error(`  - ${f}`);
  }
  process.exit(1);
}
