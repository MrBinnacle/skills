// Consent, end to end: Pi's real agent loop and session store, the HUD loaded by Pi's own
// extension loader, and only the model's replies scripted. Every request the model receives is
// captured, then checked against what the person agreed to send:
//   - the Log and an unsent Memory draft never reach any request;
//   - a sent Memory reaches the agent's requests, also after /compact, and never the observer's;
//   - the observer is shown the transcript, and nothing else of the person's;
//   - a note reaches the agent only when it is new to the agent and the observer is set to forward.
// Skipped when no Pi install is found (set PI_CODING_AGENT_PACKAGE to point at one).
import { afterAll, beforeAll, expect, test } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { pathToFileURL } from "node:url";
import { SYSTEM } from "./observer";
import { SECTION } from "./state";

const HUD_DIR = import.meta.dir;
const SCOPE = "@earendil-works";

function piDir() {
  if (process.env.PI_CODING_AGENT_PACKAGE) return process.env.PI_CODING_AGENT_PACKAGE;
  const root = join(homedir(), ".pi", "agent", "install");
  const v = join(root, "current-version");
  return existsSync(v) ? join(root, "releases", readFileSync(v, "utf-8").trim(), "node_modules", SCOPE, "pi-coding-agent") : "";
}
const PI = piDir();
const found = !!PI && existsSync(join(PI, "dist", "index.js")) && existsSync(join(PI, "..", "pi-ai", "dist", "index.js"));

const LOG = "LOG-7f3a never send this";
const DRAFT = "DRAFT-91c2 unsent memory line";
const MEMORY = "MEMORY-4be0 the person approved this line";
const OBSERVER_MARK = SYSTEM.slice(0, 80);

type Call = { observer: boolean; text: string };
const calls: Call[] = [];
let session: any;
let entries: () => any[];
let dir = "";

// What the observer says next, and the agent's script, consumed in order.
let observerReplies: string[] = [];
let agentScript: Array<(ai: any) => any> = [];

const note = (line: string, agentKnows: boolean) =>
  JSON.stringify({ tag: "heads-up", note: line, details: "**What happened:** see the record.", evidence: "working on the migration", agentKnows });
const work = (n: number) => (ai: any) => ai.fauxAssistantMessage(ai.fauxToolCall("bash", { command: `echo step ${n}` }), { stopReason: "toolUse" });
const say = (text: string) => (ai: any) => ai.fauxAssistantMessage(text);
const run = (steps: number) => [...Array.from({ length: steps }, (_, i) => work(i)), say("Done; still working on the migration.")];

const notes = () => entries().filter((e) => e.type === "custom" && e.customType === "binnacle-hud" && e.data?.k === "note").map((e) => e.data.note);
async function until(ok: () => boolean, what: string) {
  for (let i = 0; i < 200 && !ok(); i++) await Bun.sleep(10);
  if (!ok()) throw new Error(`timed out waiting for ${what}`);
}
// The Memory section a request leaves in force: system messages patch sections in order, and a
// null removes one. A text search is not enough: after /compact the request still holds the old
// system message carrying Memory, followed by a patch that removes it.
const memoryIn = (c: Call) => {
  let v: string | null | undefined;
  for (const m of JSON.parse(c.text).messages ?? []) if (m.role === "system" && m.sections && SECTION in m.sections) v = m.sections[SECTION];
  return v ?? "";
};
const agentCalls = (from = 0) => calls.slice(from).filter((c) => !c.observer);
const observerCalls = () => calls.filter((c) => c.observer);

beforeAll(async () => {
  if (!found) return;
  const pi = await import(pathToFileURL(join(PI, "dist", "index.js")).href);
  const ai = await import(pathToFileURL(join(PI, "..", "pi-ai", "dist", "index.js")).href);
  dir = mkdtempSync(join(tmpdir(), "binnacle-consent-"));
  process.env.PI_CODING_AGENT_DIR = join(dir, "agent"); // the observer setting file lands here, not in the real ~/.pi

  const faux = ai.fauxProvider();
  const respond = (context: unknown) => {
    const text = JSON.stringify(context);
    const observer = text.includes(JSON.stringify(OBSERVER_MARK).slice(1, -1));
    calls.push({ observer, text });
    if (observer) return ai.fauxAssistantMessage(observerReplies.shift() ?? '{"note": null}');
    if (text.includes("summar")) { if (!agentScript.length) return ai.fauxAssistantMessage("## Goal\nMigration summary."); }
    const next = agentScript.shift();
    return next ? next(ai) : ai.fauxAssistantMessage("Done; still working on the migration.");
  };
  faux.setResponses(Array.from({ length: 400 }, () => respond));
  const modelRuntime = await pi.ModelRuntime.create({ authPath: join(dir, "auth.json"), modelsPath: null, refreshOnCreate: false });
  modelRuntime.registerNativeProvider(faux.provider);
  await modelRuntime.setRuntimeApiKey(faux.provider.id ?? faux.getModel().provider, "faux");

  const resourceLoader = new pi.DefaultResourceLoader({
    cwd: dir, agentDir: join(dir, "agent"), noExtensions: true, additionalExtensionPaths: [HUD_DIR],
    noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
  });
  await resourceLoader.reload();
  const { errors } = resourceLoader.getExtensions();
  if (errors.length) throw new Error(`extension load failed: ${JSON.stringify(errors)}`);

  const sessionManager = pi.SessionManager.inMemory();
  entries = () => sessionManager.getEntries();
  ({ session } = await pi.createAgentSession({
    cwd: dir, agentDir: join(dir, "agent"), model: faux.getModel(), modelRuntime, resourceLoader, tools: ["bash"],
    sessionManager, settingsManager: pi.SettingsManager.inMemory({ compaction: { enabled: false, keepRecentTokens: 1 } } as any),
  }));
  // A terminal is present as far as the HUD can tell; the overlay never opens because no key is
  // pressed. Pi spreads this object, so every member must be an own property, not a Proxy trap.
  const plain = (s: string) => s;
  const theme = { fg: (_c: string, s: string) => s, bg: (_c: string, s: string) => s, bold: plain, italic: plain, underline: plain, dim: plain, strikethrough: plain, inverse: plain };
  const none = () => undefined;
  const ui: any = {
    theme, confirm: async () => true, custom: () => new Promise(() => {}), select: async () => undefined, input: async () => undefined, editor: async () => undefined,
    notify: none, onTerminalInput: () => none, setStatus: none, setWorkingMessage: none, setWorkingVisible: none, setWorkingIndicator: none, setHiddenThinkingLabel: none,
    setWidget: none, setFooter: none, setHeader: none, setTitle: none, setEditorText: none, getEditorText: () => "", pasteToEditor: none, setEditorComponent: none,
    getAllThemes: () => [], getTheme: none, setTheme: () => ({ success: false }), getToolsExpanded: () => false, setToolsExpanded: none,
  };
  await session.bindExtensions({ uiContext: ui, mode: "tui" });
}, 60_000);

afterAll(() => {
  session?.dispose?.();
  if (dir) rmSync(dir, { recursive: true, force: true });
});

test.skipIf(!found)("consent holds across Pi's real agent loop", async () => {
  // 1. A thought in the Log and an unsent Memory line, then a run long enough for a look at settle.
  await session.prompt("/hud observer forward"); // the default is panel; the forwarding rule is what this test checks
  await session.prompt(`/log ${LOG}`);
  await session.prompt(`/hud add ${DRAFT}`);
  observerReplies = [note("The agent is mid-migration with no backup taken.", false)];
  agentScript = run(3);
  await session.prompt("Start the migration.");
  await until(() => notes().length === 1, "the first note");
  expect(notes()[0].how).toBe("waits for your next message");
  expect(observerCalls()).toHaveLength(1);
  expect(observerCalls()[0]!.text).toContain("working on the migration");
  expect(observerCalls()[0]!.text).toContain("Start the migration.");

  // 2. The idle agent gets that note with the person's next message.
  let mark = calls.length;
  agentScript = [say("Noted.")];
  await session.prompt("Carry on.");
  expect(agentCalls(mark)[0]!.text).toContain("The agent is mid-migration with no backup taken.");

  // 3. A note the agent already stated stays with the person.
  observerReplies = [note("The agent said it skipped the dry run.", true)];
  agentScript = run(3);
  await session.prompt("Next table.");
  await until(() => notes().length === 2, "the second note");
  expect(notes()[1].how).toBe("for you only");
  mark = calls.length;
  agentScript = [say("Ok.")];
  await session.prompt("Go on.");
  expect(agentCalls(mark).some((c) => c.text.includes("skipped the dry run"))).toBe(false);

  // 4. A note waiting for the next message stays with the person once forwarding stops.
  observerReplies = [note("The agent left a lock file behind.", false)];
  agentScript = run(3);
  await session.prompt("Clean up.");
  await until(() => notes().length === 3, "the waiting note");
  expect(notes()[2].how).toBe("waits for your next message");
  await session.prompt("/hud observer panel");
  await session.prompt("/hud observer forward");
  mark = calls.length;
  agentScript = [say("Ok.")];
  await session.prompt("Status?");
  expect(agentCalls(mark).some((c) => c.text.includes("lock file"))).toBe(false);

  // 5. Panel mode: a new note stays with the person too.
  await session.prompt("/hud observer panel");
  observerReplies = [note("The agent dropped an index the app still reads.", false)];
  agentScript = run(3);
  await session.prompt("Last table.");
  await until(() => notes().length === 4, "the panel-mode note");
  expect(notes()[3].how).toBe("for you only");
  mark = calls.length;
  agentScript = [say("Ok.")];
  await session.prompt("Thanks.");
  expect(agentCalls(mark).some((c) => c.text.includes("dropped an index"))).toBe(false);
  await session.prompt("/hud observer forward");

  // 6. Memory is absent until sent, then present in every agent request, also after /compact.
  expect(calls.some((c) => c.text.includes("MEMORY-4be0"))).toBe(false);
  await session.prompt(`/hud add ${MEMORY}`);
  await session.prompt("/hud send");
  mark = calls.length;
  agentScript = [say("Ok.")];
  await session.prompt("Check the memory.");
  expect(memoryIn(agentCalls(mark)[0]!)).toContain("MEMORY-4be0");
  agentScript = [];
  await session.compact();
  expect(entries().some((e) => e.type === "compaction")).toBe(true);
  mark = calls.length;
  agentScript = [say("Ok.")];
  await session.prompt("After compaction.");
  // That run left 3 unread turns, so the observer looks once more, now with Memory sent.
  await until(() => observerCalls().length === 5, "the look after /compact");
  expect(memoryIn(agentCalls(mark)[0]!)).toContain("MEMORY-4be0");

  // Across every request of the session: the Log never left, the observer never saw Memory.
  expect(calls.length).toBeGreaterThan(10);
  expect(calls.filter((c) => c.text.includes("LOG-7f3a"))).toHaveLength(0);
  // The draft line was later sent as part of Memory, so it may appear only once Memory was sent.
  const sentAt = calls.findIndex((c) => c.text.includes("MEMORY-4be0"));
  expect(calls.slice(0, sentAt).filter((c) => c.text.includes("DRAFT-91c2"))).toHaveLength(0);
  expect(observerCalls().filter((c) => c.text.includes("MEMORY-4be0") || c.text.includes("DRAFT-91c2"))).toHaveLength(0);
}, 30_000);
