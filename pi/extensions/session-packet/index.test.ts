import { describe, expect, spyOn, test } from "bun:test";
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import extension from "./index";
import { makeRepo, nodeExec } from "./testkit";

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

function fakeCtx(cwd: string, hasUI = true) {
  const notes: { message: string; level?: string }[] = [];
  return {
    ctx: { cwd, hasUI, mode: hasUI ? "tui" : "print", isIdle: () => true, ui: { notify: (message: string, level?: string) => notes.push({ message, level }) } },
    notes,
  };
}

function writeConfig(root: string, sessionPacket: unknown) {
  mkdirSync(join(root, ".pi"), { recursive: true });
  writeFileSync(join(root, ".pi", "engineering-env.json"), JSON.stringify({ sessionPacket }));
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
  test("registers both commands and the lifecycle handlers", () => {
    const { commands, events } = fakePi();
    expect([...commands.keys()].sort()).toEqual(["packet-close", "packet-open"]);
    expect(events.has("session_start")).toBe(true);
    expect(events.has("agent_before_settle")).toBe(true);
  });

  test("/packet-close without an objective refuses and asks the agent nothing", async () => {
    const { root } = await makeRepo();
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("  ", ctx);
    expect(sent).toEqual([]);
    expect(notes[0]?.level).toBe("error");
    expect(notes[0]?.message).toContain("objective");
  });

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
  });

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
  });

  test("/packet-close refuses on a red receiver check and writes nothing", async () => {
    const { root } = await makeRepo();
    writeConfig(root, { receiverChecks: [{ name: "red", command: "exit 1" }] });
    const { commands, sent } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    expect(sent).toEqual([]);
    expect(notes[0]?.message).toContain("a receiver check is red");
  });

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
  });

  test("/packet-open without a sessionPacket config rejects instead of skipping checks", async () => {
    const { root } = await makeRepo();
    const { commands, events } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    fillLatest(root);
    await events.get("agent_before_settle")!(settle, ctx);
    await commands.get("packet-open")!("", ctx);
    expect(JSON.parse(notes.at(-1)!.message).errors).toContain("receive mode requires a sessionPacket config");
  });

  test("session_start checks the latest packet only when the project declares sessionPacket", async () => {
    const { root } = await makeRepo();
    writeConfig(root, undefined); // a config file with no sessionPacket section
    const { commands, events } = fakePi();
    const { ctx, notes } = fakeCtx(root);
    await commands.get("packet-close")!("Ship", ctx);
    fillLatest(root);
    await events.get("agent_before_settle")!(settle, ctx);
    const before = notes.length;
    await events.get("session_start")!({ type: "session_start", reason: "startup" }, ctx);
    expect(notes.length).toBe(before);
    writeConfig(root, {});
    await events.get("session_start")!({ type: "session_start", reason: "startup" }, ctx);
    expect(notes.at(-1)?.message).toContain("ACCEPTED");
  });

  test("session_start never throws: a failure is reported, on stderr when there is no UI", async () => {
    const root = join(import.meta.dir, "fixtures");
    const { events } = fakePi();
    const { ctx, notes } = fakeCtx(root, false);
    const spy = spyOn(console, "error").mockImplementation(() => {});
    try {
      // The fixtures directory is inside a repo but has no config: nothing to check, nothing thrown.
      await events.get("session_start")!({ type: "session_start", reason: "startup" }, ctx);
      const bad = (await makeRepo()).root;
      mkdirSync(join(bad, ".pi"));
      writeFileSync(join(bad, ".pi", "engineering-env.json"), "{ broken");
      await events.get("session_start")!({ type: "session_start", reason: "startup" }, { ...ctx, cwd: bad });
      expect(spy).toHaveBeenCalled();
      expect(String(spy.mock.calls.at(-1)![0])).toContain("engineering-env.json");
      expect(notes).toEqual([]);
    } finally {
      spy.mockRestore();
    }
  });
});
