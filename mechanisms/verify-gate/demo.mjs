// Runs Pi's real agent loop twice on a throwaway project: once without verify-gate, once
// with it. Only the model's replies are scripted. Usage: node mechanisms/verify-gate/demo.mjs
import { execSync, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const GATE_DIR = dirname(fileURLToPath(import.meta.url));
const SCOPE = "@earendil-works";

function managedInstall() {
  const root = join(homedir(), ".pi", "agent", "install");
  const versionFile = join(root, "current-version");
  if (!existsSync(versionFile)) return undefined;
  const version = readFileSync(versionFile, "utf-8").trim();
  return join(root, "releases", version, "node_modules", SCOPE, "pi-coding-agent");
}

function globalInstall() {
  try {
    return join(execSync("npm root -g", { encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] }).trim(), SCOPE, "pi-coding-agent");
  } catch {
    return undefined;
  }
}

async function loadPi() {
  const candidates = [process.env.PI_CODING_AGENT_PACKAGE, managedInstall(), globalInstall()];
  for (const dir of candidates) {
    if (!dir || !existsSync(join(dir, "dist", "index.js"))) continue;
    const aiDir = [join(dir, "..", "pi-ai"), join(dir, "node_modules", SCOPE, "pi-ai")]
      .find((d) => existsSync(join(d, "dist", "index.js")));
    if (!aiDir) continue;
    const pi = await import(pathToFileURL(join(dir, "dist", "index.js")).href);
    const ai = await import(pathToFileURL(join(aiDir, "dist", "index.js")).href);
    const version = JSON.parse(readFileSync(join(dir, "package.json"), "utf-8")).version;
    return { pi, ai, version };
  }
  console.error("Pi not found. Install it from https://pi.dev, or set PI_CODING_AGENT_PACKAGE to the @earendil-works/pi-coding-agent directory.");
  process.exit(2);
}

const PROJECT = {
  "package.json": JSON.stringify({ name: "shop", type: "module", scripts: { test: "node --test" } }, null, 2),
  "price.mjs": "export function orderTotal(subtotal) {\n  return subtotal;\n}\n",
  "price.test.mjs": [
    'import { test } from "node:test";',
    'import assert from "node:assert/strict";',
    'import { orderTotal } from "./price.mjs";',
    "",
    'test("every order gets 10% off", () => {',
    "  assert.equal(orderTotal(100), 90);",
    "});",
    "",
  ].join("\n"),
};

function makeProject() {
  const cwd = mkdtempSync(join(tmpdir(), "verify-gate-demo-"));
  for (const [name, text] of Object.entries(PROJECT)) writeFileSync(join(cwd, name), text);
  return cwd;
}

function textOf(message) {
  const content = message.content;
  if (typeof content === "string") return content;
  return content.filter((c) => c.type === "text").map((c) => c.text).join("\n");
}

// The last reply reads the real test output from the transcript, so it reports what happened.
function reportTestResult(ai) {
  return (context) => {
    const result = [...context.messages].reverse().find((m) => m.role === "toolResult");
    const output = result ? textOf(result) : "";
    const failed = result?.isError || /\bfail [1-9]/.test(output);
    const evidence = output.split("\n").map((l) => l.trim())
      .filter((l) => /^not ok|expected|actual|^# (pass|fail)/i.test(l)).slice(0, 5);
    const verdict = failed
      ? "I ran npm test and it failed, so the discount is not done:"
      : "I ran npm test and it passed:";
    return ai.fauxAssistantMessage([verdict, ...evidence.map((l) => `  ${l}`)].join("\n"));
  };
}

function script(ai) {
  return [
    ai.fauxAssistantMessage(ai.fauxToolCall("edit", {
      path: "price.mjs",
      edits: [{ oldText: "return subtotal;", newText: "return subtotal * 0.1;" }],
    }), { stopReason: "toolUse" }),
    ai.fauxAssistantMessage("Done. Every order now gets a 10% discount."),
    ai.fauxAssistantMessage(ai.fauxToolCall("bash", { command: "npm test" }), { stopReason: "toolUse" }),
    reportTestResult(ai),
  ];
}

function show(who, text) {
  const lines = text.split("\n");
  console.log(`  ${who.padEnd(6)}| ${lines[0]}`);
  for (const l of lines.slice(1)) console.log(`        | ${l}`);
}

async function runAgent({ pi, ai }, cwd, withGate) {
  const agentDir = join(cwd, ".pi-agent");
  const faux = ai.fauxProvider();
  faux.setResponses(script(ai));
  const modelRuntime = await pi.ModelRuntime.create({ authPath: join(agentDir, "auth.json"), modelsPath: null, refreshOnCreate: false });
  modelRuntime.registerNativeProvider(faux.provider);
  await modelRuntime.setRuntimeApiKey(faux.provider.id ?? faux.getModel().provider, "faux");

  const resourceLoader = new pi.DefaultResourceLoader({
    cwd, agentDir, noExtensions: true, additionalExtensionPaths: withGate ? [GATE_DIR] : [],
    noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
  });
  await resourceLoader.reload();
  const { errors } = resourceLoader.getExtensions();
  if (errors.length) throw new Error(`extension load failed: ${JSON.stringify(errors)}`);

  const { session } = await pi.createAgentSession({
    cwd, agentDir, model: faux.getModel(), modelRuntime, resourceLoader, tools: ["edit", "bash"],
    sessionManager: pi.SessionManager.inMemory(), settingsManager: pi.SettingsManager.inMemory(),
  });
  await session.bindExtensions({});

  await session.prompt("Give every order a 10% discount.");

  // Read back the transcript the session kept, in order.
  const trace = { gateMessages: [], bashCalls: [], modelCalls: faux.state.callCount };
  for (const m of session.messages) {
    if (m.role === "user") show("user", textOf(m));
    else if (m.role === "custom") {
      if (m.customType === "verify-gate") trace.gateMessages.push(textOf(m));
      show(m.customType === "verify-gate" ? "gate" : m.customType, textOf(m));
    } else if (m.role === "assistant") {
      for (const c of m.content.filter((c) => c.type === "toolCall")) {
        show("agent", `calls ${c.name} ${JSON.stringify(c.arguments)}`);
        if (c.name === "bash") trace.bashCalls.push({ command: c.arguments.command });
      }
      if (textOf(m)) show("agent", textOf(m));
    } else if (m.role === "toolResult") {
      const call = trace.bashCalls.at(-1);
      if (m.toolName === "bash" && call) call.isError = m.isError;
      show("tool", `${m.toolName} ${m.isError ? "FAILED" : "ok"}`);
    }
  }
  return trace;
}

function runTests(cwd) {
  return { passed: spawnSync(process.execPath, ["--test"], { cwd }).status === 0 };
}

const failures = [];
const check = (ok, what) => { if (!ok) failures.push(what); };

const started = Date.now();
const loaded = await loadPi();
console.log(`verify-gate demo: Pi ${loaded.version}'s real agent loop, edit and bash tools, scripted model replies.\n`);

const cwd1 = makeProject();
const cwd2 = makeProject();
try {
  console.log("Run 1: verify-gate not loaded");
  const run1 = await runAgent(loaded, cwd1, false);
  const tests1 = runTests(cwd1);
  console.log(`  The run settled after ${run1.modelCalls} model calls and ${run1.bashCalls.length} checks.`);
  console.log(`  The demo now runs the project's tests itself: ${tests1.passed ? "PASS." : "FAIL. The bug would have shipped."}\n`);
  check(run1.modelCalls === 2, `run 1: expected 2 model calls, got ${run1.modelCalls}`);
  check(run1.bashCalls.length === 0, "run 1: expected no check to run");
  check(run1.gateMessages.length === 0, "run 1: expected no verify-gate message");
  check(!tests1.passed, "run 1: expected the project's tests to fail on the bug");

  console.log(`Run 2: verify-gate loaded from ${GATE_DIR}, same script`);
  const run2 = await runAgent(loaded, cwd2, true);
  const npmTest = run2.bashCalls[0];
  const sentBack = run2.gateMessages.length > 0 && run2.bashCalls.length > 0;
  console.log(`  The run settled after ${run2.modelCalls} model calls.${sentBack ? " The gate sent the agent back to check." : ""}\n`);
  check(run2.gateMessages.length === 1, `run 2: expected one verify-gate message, got ${run2.gateMessages.length}`);
  check(run2.bashCalls.length === 1, `run 2: expected one npm test call, got ${run2.bashCalls.length}`);
  check(npmTest?.command === "npm test", "run 2: expected the agent to run npm test");
  check(npmTest?.isError === true, "run 2: expected npm test to fail");
} finally {
  rmSync(cwd1, { recursive: true, force: true });
  rmSync(cwd2, { recursive: true, force: true });
}

console.log("Real: Pi's agent loop, its edit and bash tools, npm test, and the verify-gate extension as shipped.");
console.log("Scripted: the model's replies. The last one reads the real test output from the transcript.");
console.log(`Guard: mechanisms/verify-gate/ (gate.ts holds the rule). Took ${((Date.now() - started) / 1000).toFixed(1)}s.`);

if (failures.length) {
  console.error(`\nDEMO FAILED: the gate did not behave as expected.\n- ${failures.join("\n- ")}`);
  process.exit(1);
}
