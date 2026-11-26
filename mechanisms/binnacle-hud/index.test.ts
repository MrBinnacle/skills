import { afterAll, describe, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import extension, { readMode, settingsPath, STRIP_PROMPTS } from "./index";

// The observer setting is read from Pi's agent dir; keep the owner's real one out of the tests.
const agentDir = mkdtempSync(join(tmpdir(), "binnacle-hud-agent-"));
process.env.PI_CODING_AGENT_DIR = agentDir;
afterAll(() => rmSync(agentDir, { recursive: true, force: true }));
import { REVIEW_EVERY } from "./observer";
import { SECTION, TYPE } from "./state";

type Handler = (...args: any[]) => any;

/** Pi's extension surface, faked: entries land in one branch, and the model answers from `replies`. */
function harness(replies: string[] = [], opts: { idle?: boolean; hasUI?: boolean } = {}) {
  const on = new Map<string, Handler[]>();
  const commands = new Map<string, Handler>();
  const entries: any[] = [];
  const sent: Array<{ message: any; options: any }> = [];
  const requests: any[] = [];
  const notes: string[] = [];
  const widgets: Array<string[] | undefined> = [];
  let n = 0;
  let step = 0;
  const pi = {
    on: (ev: string, h: Handler) => on.set(ev, [...(on.get(ev) ?? []), h]),
    registerCommand: (name: string, o: { handler: Handler }) => commands.set(name, o.handler),
    registerShortcut: () => {},
    registerMessageRenderer: () => {},
    appendEntry: (customType: string, data: unknown) => entries.push({ type: "custom", customType, data, id: `c${++n}` }),
    sendMessage: (message: any, options: any) => sent.push({ message, options }),
  };
  extension(pi as any);
  const ctx = {
    hasUI: opts.hasUI ?? true,
    mode: "print",
    model: { id: "m", provider: "p" },
    isIdle: () => opts.idle ?? true,
    sessionManager: { getEntries: () => entries, getBranch: () => entries },
    ui: { notify: (m: string) => notes.push(m), setWidget: (_: string, lines?: string[]) => widgets.push(lines), theme: { fg: (_: string, t: string) => t, bold: (t: string) => t }, confirm: async () => true },
    modelRegistry: {
      complete: async (_model: unknown, context: any) => {
        requests.push(context);
        return { stopReason: "stop", content: [{ type: "text", text: replies.shift() ?? '{"note": null}' }] };
      },
    },
  };
  const emit = async (ev: string, event: any = {}) => {
    let out;
    for (const h of on.get(ev) ?? []) out = (await h(event, ctx)) ?? out;
    return out;
  };
  const run = (name: string, args: string) => commands.get(name)!(args, ctx);
  const say = (role: string, content: unknown) => entries.push({ type: "message", id: `m${++n}`, message: { role, content } });
  const turns = async (count: number) => {
    for (let i = 0; i < count; i++) {
      say("assistant", [{ type: "text", text: `step ${step++}. working on the migration` }]);
      await emit("turn_end");
    }
    await new Promise((r) => setTimeout(r, 0));
  };
  const start = (messageType = "user") => {
    const event = { messageType, systemPromptOptions: { sections: {} as Record<string, string> } };
    return emit("before_agent_start", event).then((result) => ({ result, sections: event.systemPromptOptions.sections }));
  };
  return { emit, run, say, turns, start, entries, sent, requests, notes, widgets, ctx };
}

const NOTE = (extra = {}) => JSON.stringify({ tag: "heads-up", note: "The agent skipped the migration test.", details: "**Skipped**\n- why", evidence: "working on the migration", agentKnows: false, ...extra });

describe("Log", () => {
  test("/log keeps the thought as a session entry", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("log", "call the bank");
    expect(h.entries.at(-1)).toMatchObject({ customType: TYPE, data: { k: "thought", text: "call the bank" } });
  });
});

describe("Memory", () => {
  test("a draft does not reach the system prompt; a Send does", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "add use bun for tests");
    expect((await h.start()).sections[SECTION]).toBeUndefined();
    await h.run("hud", "send");
    expect((await h.start()).sections[SECTION]).toContain("- use bun for tests");
  });
  test("Send needs the confirmation", async () => {
    const h = harness();
    h.ctx.ui.confirm = async () => false;
    await h.emit("session_start");
    await h.run("hud", "add x");
    await h.run("hud", "send");
    expect((await h.start()).sections[SECTION]).toBeUndefined();
  });
  test("an empty Send removes the section", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "add x");
    await h.run("hud", "send");
    h.entries.push({ type: "custom", customType: TYPE, data: { k: "draft", lines: [] } });
    await h.emit("session_tree");
    await h.run("hud", "send");
    const event = { messageType: "user", systemPromptOptions: { sections: { [SECTION]: "stale" } as Record<string, string> } };
    await h.emit("before_agent_start", event);
    expect(event.systemPromptOptions.sections[SECTION]).toBeUndefined();
  });
  test("delivery is recorded only when a request carries the snapshot", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "add x");
    await h.run("hud", "send");
    await h.emit("context_with_system", { messages: [{ role: "system", sections: {} }] });
    expect(h.entries.some((e) => e.data?.k === "delivered")).toBe(false);
    const { sections } = await h.start();
    await h.emit("context_with_system", { messages: [{ role: "system", sections }] });
    expect(h.entries.filter((e) => e.data?.k === "delivered").length).toBe(1);
    await h.emit("context_with_system", { messages: [{ role: "system", sections }] });
    expect(h.entries.filter((e) => e.data?.k === "delivered").length).toBe(1);
  });
});

describe("observer", () => {
  test("looks once every REVIEW_EVERY turns, and only at the turns it has not seen", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY - 1);
    expect(h.requests.length).toBe(0);
    await h.turns(1);
    expect(h.requests.length).toBe(1);
    await h.turns(REVIEW_EVERY);
    expect(h.requests.length).toBe(2);
    const second = h.requests[1].messages[0].content[0].text as string;
    expect(second).toContain(`step ${REVIEW_EVERY}.`);
    expect(second).not.toContain(`step ${REVIEW_EVERY - 1}.`);
  });
  test("its request carries neither the Log nor the Memory draft", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("log", "PRIVATE-THOUGHT");
    await h.run("hud", "add PRIVATE-DRAFT");
    h.say("user", "do the work");
    await h.turns(REVIEW_EVERY);
    const body = JSON.stringify(h.requests);
    expect(body).toContain("do the work");
    expect(body).not.toContain("PRIVATE-THOUGHT");
    expect(body).not.toContain("PRIVATE-DRAFT");
  });
  test("no UI, no look", async () => {
    const h = harness([], { hasUI: false });
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.requests.length).toBe(0);
  });
  test("a hand-back with enough unseen turns gets a look; an aborted one does not", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.turns(3);
    await h.emit("agent_settled", { aborted: true });
    expect(h.requests.length).toBe(0);
    await h.emit("agent_settled", { aborted: false });
    await new Promise((r) => setTimeout(r, 0));
    expect(h.requests.length).toBe(1);
  });
  test("while the agent works, a note steers into the run", async () => {
    const h = harness([NOTE()], { idle: false });
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.sent).toHaveLength(1);
    expect(h.sent[0]!.options).toEqual({ deliverAs: "steer" });
    expect(h.sent[0]!.message.content).toContain("The agent skipped the migration test.");
  });
  test("when idle, a note waits and rides with the next message, once", async () => {
    const h = harness([NOTE()]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.sent).toHaveLength(0);
    expect((await h.start("custom")).result).toBeUndefined();
    const { result } = await h.start();
    expect(result.message.content).toContain("The agent skipped the migration test.");
    expect((await h.start()).result).toBeUndefined();
  });
  test("a note the agent already stated is for the person only", async () => {
    const h = harness([NOTE({ agentKnows: true })], { idle: false });
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.sent).toHaveLength(0);
    expect((await h.start()).result).toBeUndefined();
    expect(h.entries.find((e) => e.data?.k === "note")?.data.note.how).toBe("for you only");
  });
  test("a dismissed waiting note is not sent", async () => {
    const h = harness([NOTE()]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    const key = h.entries.find((e) => e.data?.k === "note").data.note.key;
    h.entries.push({ type: "custom", customType: TYPE, data: { k: "mark", key, mark: "dismissed" } });
    await h.emit("session_tree");
    expect((await h.start()).result).toBeUndefined();
  });
  test("a repeated note and a bad reply show nothing", async () => {
    const h = harness([NOTE(), NOTE({ note: "the agent SKIPPED the migration test" }), "not json"]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY * 3);
    expect(h.requests.length).toBe(3);
    expect(h.entries.filter((e) => e.data?.k === "note").length).toBe(1);
  });
  test("a note whose quote is not in the record is dropped", async () => {
    const h = harness([NOTE({ evidence: "the agent deleted the production database" })], { idle: false });
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.entries.some((e) => e.data?.k === "note")).toBe(false);
    expect(h.sent).toHaveLength(0);
  });
  test("each note carries the prompt version and its evidence", async () => {
    const h = harness([NOTE()]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.entries.find((e) => e.data?.k === "note").data.note).toMatchObject({ evidence: "working on the migration", version: expect.stringMatching(/^observer-/) });
  });
  test("the strip headline clears after STRIP_PROMPTS prompts", async () => {
    const h = harness([NOTE({ agentKnows: true })]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.widgets.at(-1)?.[0]).toContain("The agent skipped the migration test.");
    for (let i = 0; i < STRIP_PROMPTS; i++) {
      await new Promise((r) => setTimeout(r, 2));
      await h.start();
    }
    expect(h.widgets.at(-1)?.[0]).not.toContain("The agent skipped the migration test.");
    expect(h.widgets.at(-1)?.[0]).toContain("1 heads-up");
  });
});

describe("observer setting", () => {
  test("defaults to forward, and /hud observer writes one setting for every session", async () => {
    expect(readMode(join(agentDir, "missing.json"))).toBe("forward");
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "observer panel");
    expect(readMode(settingsPath())).toBe("panel");
    await h.run("hud", "observer loud");
    expect(readMode(settingsPath())).toBe("panel");
  });
  test("panel keeps notes with the person: nothing steers, nothing rides along", async () => {
    const h = harness([NOTE(), NOTE({ note: "A second, different note about cost." })], { idle: false });
    await h.emit("session_start");
    await h.run("hud", "observer panel");
    await h.turns(REVIEW_EVERY);
    expect(h.sent).toHaveLength(0);
    expect(h.entries.find((e) => e.data?.k === "note").data.note.how).toBe("for you only");
    await h.run("hud", "observer forward");
  });
  test("off makes no model call", async () => {
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "observer off");
    await h.turns(REVIEW_EVERY * 2);
    expect(h.requests).toHaveLength(0);
    await h.run("hud", "observer forward");
  });
});
