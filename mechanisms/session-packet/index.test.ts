import { describe, expect } from "bun:test";
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import extension from "./index";
import { fillScaffold, git, GIT_TIMEOUT, makeRemote, makeRepo, nodeExec, test } from "./testkit";

type Handler = (...args: any[]) => any;

/** A stand-in for Pi's ExtensionAPI recording what the adapter registers and sends. */
function fakePi() {
  const commands = new Map<string, Handler>();
  const events = new Map<string, Handler>();
  const sent: string[] = [];
  const messages: unknown[] = [];
  const pi = {
    registerCommand: (name: string, options: { handler: Handler }) => commands.set(name, options.handler),
    on: (event: string, handler: Handler) => events.set(event, handler),
    sendUserMessage: (content: string) => sent.push(content),
    sendMessage: (message: unknown) => messages.push(message),
    exec: nodeExec,
  };
  extension(pi as any);
  return { commands, events, sent, messages };
}

function fakeCtx(cwd: string, hasUI = true, trusted = true) {
  const notes: { message: string; level?: string }[] = [];
  return {
    ctx: { cwd, hasUI, mode: hasUI ? "tui" : "print", isIdle: () => true, isProjectTrusted: () => trusted, ui: { notify: (message: string, level?: string) => notes.push({ message, level }) } },
    notes,
  };
}

function writeConfig(root: string, sessionPacket: unknown) {
  mkdirSync(join(root, ".pi"), { recursive: true });
  writeFileSync(join(root, ".pi", "engineering-env.json"), JSON.stringify({ sessionPacket }));
  writeFileSync(join(root, ".pi", "settings.json"), "{}");
}

function fillLatest(root: string) {
  const dir = join(root, ".pi", "session-packets");
  const path = join(dir, readdirSync(dir).sort().at(-1)!);
  writeFileSync(path, readFileSync(path, "utf-8")
    .replace('"task": "__REQUIRED__"', '"task": "Run the suite"')
    .replace('"purpose": "__REQUIRED__"', '"purpose": "Confirm green"')
    .replaceAll("__REQUIRED__", "Filled in."));
}

const settle = { type: "agent_before_settle", outcome: "completed", entries: [], continue: false, context: { canContinue: true } };

describe("session-packet adapter", () => {
  test("registers both commands and only the settle handler: nothing runs at session start", () => {
    const { commands, events } = fakePi();
    expect([...commands.keys()].sort()).toEqual(["packet-close", "packet-open"]);
    expect([...events.keys()]).toEqual(["agent_before_settle"]);
  });

  test("/packet-close without an objective refuses and asks the agent nothing", async () => {
    const { root } = await makeRepo();
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("  ", ctx);
    expect(sent).toEqual([]);
    expect(notes[0]?.level).toBe("error");
    expect(notes[0]?.message).toContain("objective");
  }, GIT_TIMEOUT);

  test("/packet-close writes the scaffold, asks the agent to fill it, and validates the fill when the agent stops", async () => {
    const { root } = await makeRepo();
    const { commands, events, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship the port", ctx);
    expect(sent).toHaveLength(1);
    expect(sent[0]).toContain(join(root, ".pi", "session-packets"));
    fillLatest(root);
    const result = await events.get("agent_before_settle")!(settle, ctx);
    expect(result).toBeUndefined();
    expect(notes.at(-1)?.message).toContain('"verdict": "ACCEPTED"');
    // Validated once; the next settle has nothing pending.
    expect(await events.get("agent_before_settle")!(settle, ctx)).toBeUndefined();
    expect(notes).toHaveLength(1);
  }, GIT_TIMEOUT);

  test("an unfilled packet sends the agent back with the errors, then gives up loudly", async () => {
    const { root } = await makeRepo();
    const { commands, events } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship the port", ctx);
    const first = await events.get("agent_before_settle")!(settle, ctx);
    expect(first.continue).toBe(true);
    expect(first.entries[0].content).toContain("unfinished marker present: __REQUIRED__");
    await events.get("agent_before_settle")!(settle, ctx);
    const last = await events.get("agent_before_settle")!(settle, ctx);
    expect(last).toBeUndefined();
    expect(notes.at(-1)?.level).toBe("error");
    expect(notes.at(-1)?.message).toContain('"verdict": "REJECTED"');
  }, GIT_TIMEOUT);

  test("/packet-close refuses on a red receiver check and writes nothing", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { receiverChecks: [{ name: "red", command: "exit 1" }] });
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    expect(sent).toEqual([]);
    expect(notes[0]?.message).toContain("a receiver check is red");
  }, GIT_TIMEOUT);

  test("a trusted project with .pi/settings.json runs its declared receiverChecks on /packet-close", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { receiverChecks: [{ name: "planted", command: "echo ran > planted-marker" }] });
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    expect(existsSync(join(root, "planted-marker"))).toBe(true);
    expect(sent).toHaveLength(1);
    expect(notes).toEqual([]);
  }, GIT_TIMEOUT);

  test("a project with no .pi/settings.json runs no receiverCheck on /packet-close even when Pi reports it trusted", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { receiverChecks: [{ name: "planted", command: "echo ran > planted-marker" }] });
    rmSync(join(root, ".pi", "settings.json"));
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    expect(existsSync(join(root, "planted-marker"))).toBe(false);
    expect(sent).toEqual([]);
    expect(notes).toEqual([{ level: "error", message: expect.stringContaining("no .pi/settings.json") }]);
  }, GIT_TIMEOUT);

  test("in an untrusted project /packet-close runs no receiverCheck and refuses with the ignored-config notice", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { receiverChecks: [{ name: "planted", command: "echo ran > planted-marker" }] });
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root, true, false);
    await commands.get("packet-close")!("Ship", ctx);
    expect(existsSync(join(root, "planted-marker"))).toBe(false);
    expect(sent).toEqual([]);
    expect(notes).toEqual([{ level: "error", message: expect.stringContaining("Pi does not trust this project") }]);
  }, GIT_TIMEOUT);

  test("in an untrusted project /packet-open runs no receiverCheck on an existing packet and refuses with the notice", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { dir: ".pi/session-packets" });
    const { commands, events } = fakePi();
    const trusted = fakeCtx(root);
    await commands.get("packet-close")!("Ship", trusted.ctx);
    fillLatest(root);
    await events.get("agent_before_settle")!(settle, trusted.ctx);
    writeConfig(root, { dir: ".pi/session-packets", receiverChecks: [{ name: "planted", command: "echo ran > planted-marker" }] });
    const { ctx, notes } = fakeCtx(root, true, false);
    await commands.get("packet-open")!("", ctx);
    expect(existsSync(join(root, "planted-marker"))).toBe(false);
    expect(notes).toEqual([{ level: "error", message: expect.stringContaining("Pi does not trust this project") }]);
  }, GIT_TIMEOUT);

  test("/packet-open validates the latest packet in receive mode and reports the receipt", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { dir: ".pi/session-packets", receiverChecks: [{ name: "head", command: "git rev-parse HEAD" }] });
    const { commands, events, messages } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    fillLatest(root);
    await events.get("agent_before_settle")!(settle, ctx);
    await commands.get("packet-open")!("", ctx);
    const receipt = JSON.parse(notes.at(-1)!.message);
    expect(receipt.verdict).toBe("ACCEPTED");
    expect(receipt.checks[0].name).toBe("head");
    expect(messages).toHaveLength(1);
  }, GIT_TIMEOUT);

  test("/packet-open without a sessionPacket config rejects instead of skipping checks", async () => {
    const { root } = await makeRepo();
    const { commands, events } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    fillLatest(root);
    await events.get("agent_before_settle")!(settle, ctx);
    await commands.get("packet-open")!("", ctx);
    expect(JSON.parse(notes.at(-1)!.message).errors).toContain("receive mode requires a sessionPacket config");
  }, GIT_TIMEOUT);

  test("with a branch store, the accepted fill is committed and pushed, and open reads it back from the store", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    writeConfig(root, { store: { kind: "branch", ref: "session-log" }, receiverChecks: [{ name: "head", command: "git rev-parse HEAD" }] });
    const { commands, events } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    const worktree = join(root, "var", "session-log-worktree");
    const name = readdirSync(worktree).find((f) => f.endsWith(".md"))!;
    fillScaffold(join(worktree, name));
    await events.get("agent_before_settle")!(settle, ctx);
    expect(notes.at(-1)?.level).toBe("info");
    expect(notes.at(-1)?.message).toContain("pushed");
    expect(await git(bare, "ls-tree", "--name-only", "session-log")).toBe(name);
    await commands.get("packet-open")!("", ctx);
    const receipt = JSON.parse(notes.at(-1)!.message);
    expect(receipt.verdict).toBe("ACCEPTED");
  }, GIT_TIMEOUT);
});
