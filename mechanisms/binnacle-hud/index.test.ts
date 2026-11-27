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
function harness(replies: string[] = [], opts: { idle?: boolean; refuseSteer?: boolean; hasUI?: boolean; picks?: string[]; duringCall?: (call: number) => void } = {}) {
  const picks = opts.picks ?? [];
  const asked: string[][] = [];
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
    sendMessage: (message: any, options: any) => {
      if (opts.refuseSteer) throw new Error("steer unavailable");
      sent.push({ message, options });
    },
  };
  extension(pi as any);
  const ctx = {
    hasUI: opts.hasUI ?? true,
    mode: "print",
    model: { id: "m", provider: "p" },
    isIdle: () => opts.idle ?? true,
    sessionManager: { getEntries: () => entries, getBranch: () => entries },
    ui: { notify: (m: string) => notes.push(m), setWidget: (_: string, lines?: string[]) => widgets.push(lines), theme: { fg: (_: string, t: string) => t, bold: (t: string) => t }, confirm: async () => true, select: async (_t: string, o: string[]) => { asked.push(o); const p = picks.shift(); return p === undefined ? undefined : o.find((x) => x.startsWith(p)); }, input: async () => picks.shift() },
    modelRegistry: {
      complete: async (_model: unknown, context: any) => {
        requests.push(context);
        opts.duringCall?.(requests.length);
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
  return { emit, run, say, turns, start, entries, sent, requests, notes, widgets, ctx, asked };
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
    await h.run("hud", "observer forward");
    await h.turns(REVIEW_EVERY);
    expect(h.sent).toHaveLength(1);
    expect(h.sent[0]!.options).toEqual({ deliverAs: "steer" });
    expect(h.sent[0]!.message.content).toContain("The agent skipped the migration test.");
  });
  test("when idle, a note waits and rides with the next message, once", async () => {
    const h = harness([NOTE()]);
    await h.emit("session_start");
    await h.run("hud", "observer forward");
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
  test("the cursor moves on a reply it could read, including null, and stays on one it could not", async () => {
    const h = harness(["not json", '{"note": null}']);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.requests.length).toBe(1);
    expect(h.entries.filter((e) => e.data?.k === "reviewed")).toHaveLength(0);
    await h.turns(REVIEW_EVERY);
    const reviewed = h.entries.filter((e) => e.data?.k === "reviewed");
    expect(reviewed).toHaveLength(1);
    expect(reviewed[0]!.data.upTo).toBe(h.entries.filter((e) => e.type === "message").at(-1)!.id);
    // The second look covered the turns the failed one did not.
    expect(h.requests[1].messages[0].content[0].text).toContain("step 0.");
  });
  test("a note whose quote is not in the record is dropped", async () => {
    const h = harness([NOTE({ evidence: "the agent deleted the production database" })], { idle: false });
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY);
    expect(h.entries.some((e) => e.data?.k === "note")).toBe(false);
    expect(h.sent).toHaveLength(0);
  });
  test("a note cannot ground itself on an earlier note", async () => {
    const first = "The agent skipped the migration test.";
    const h = harness([NOTE(), NOTE({ note: "Another thing entirely happened here.", evidence: first })]);
    await h.emit("session_start");
    await h.turns(REVIEW_EVERY * 2);
    expect(h.requests).toHaveLength(2);
    expect(JSON.stringify(h.requests[1])).toContain(first); // it is in <already_raised>, which is not the record
    expect(h.entries.filter((e) => e.data?.k === "note")).toHaveLength(1);
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
  test("defaults to panel, and /hud observer writes one setting for every session", async () => {
    expect(readMode(join(agentDir, "missing.json"))).toBe("panel");
    const h = harness();
    await h.emit("session_start");
    await h.run("hud", "observer forward");
    expect(readMode(settingsPath())).toBe("forward");
    await h.run("hud", "observer loud");
    expect(readMode(settingsPath())).toBe("forward");
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

describe("alt+h menu: the person acts on a heads-up without leaving the prompt", () => {
  const raise = async (picks: string[], idle = true) => {
    const h = harness([NOTE()], { picks, idle });
    await h.emit("session_start");
    await h.run("hud", "observer panel");
    await h.turns(REVIEW_EVERY);
    await h.run("hud", "");
    await h.run("hud", "observer forward");
    return h;
  };
  const how = (h: any) => h.entries.filter((e: any) => e.data?.k === "how").map((e: any) => e.data.how);
  const marks = (h: any) => h.entries.filter((e: any) => e.data?.k === "mark").map((e: any) => e.data.mark);

  test("send reaches the agent now: steers a busy run, starts a turn on an idle one", async () => {
    const h = await raise(["1.", "Send"]);
    expect(h.sent).toHaveLength(1);
    expect(h.sent[0]!.options).toEqual({ deliverAs: "steer", triggerTurn: true });
    expect(h.sent[0]!.message.content).toContain("The agent skipped the migration test.");
    expect(how(h)).toEqual(["you sent it"]);
    expect(marks(h)).toEqual(["read", "useful"]);
  });
  test("a sent note offers no second send", async () => {
    const h = await raise(["1.", "Send"]);
    // a sent note is closed (marked useful), so the menu no longer lists it
    await h.run("hud", "");
    expect(h.asked.at(-1)!.some((o: string) => o.startsWith("1."))).toBe(false);
  });
  test("marking from the menu closes the note and sends nothing", async () => {
    const h = await raise(["1.", "Wrong"]);
    expect(h.sent).toHaveLength(0);
    expect(marks(h)).toEqual(["read", "wrong"]);
  });
  test("cancelling leaves the note open and only read", async () => {
    const h = await raise(["1."]);
    expect(h.sent).toHaveLength(0);
    expect(marks(h)).toEqual(["read"]);
  });
  test("Log and Memory are typed through prompts, not a panel field", async () => {
    const h = harness([], { picks: ["Keep a thought", "buy milk", "Add a Memory", "use pnpm", "Remove a Memory", "1. use pnpm"] });
    await h.emit("session_start");
    await h.run("hud", "");
    await h.run("hud", "");
    await h.run("hud", "");
    const ks = h.entries.map((e: any) => e.data?.k);
    expect(h.entries.find((e: any) => e.data?.k === "thought").data.text).toBe("buy milk");
    expect(ks.filter((k: string) => k === "draft")).toHaveLength(2);
    expect(h.entries.filter((e: any) => e.data?.k === "draft").at(-1).data.lines).toEqual([]);
  });
});

// The paths TLC checked in the README statechart (HudNote.tla), replayed on the real code.
describe("a note is reread against turns that came while the observer worked", () => {
  const run = async (replies: string[], agentActs: boolean) => {
    let h: any;
    h = harness(replies, { duringCall: (call) => { if (agentActs && call === 1) h.say("assistant", [{ type: "text", text: "Fixed it: the test no longer names the county." }]); } });
    await h.emit("session_start");
    await h.run("hud", "observer panel");
    await h.turns(REVIEW_EVERY);
    await h.run("hud", "observer forward");
    return { h, notes: h.entries.filter((e: any) => e.data?.k === "note"), stale: h.entries.filter((e: any) => e.data?.k === "stale") };
  };
  test("no later turns: shown with no second call", async () => {
    const { h, notes } = await run([NOTE()], false);
    expect(h.requests).toHaveLength(1);
    expect(notes).toHaveLength(1);
  });
  test("the agent fixed it meanwhile: dropped, recorded stale, never shown (the BERGEN path)", async () => {
    const { h, notes, stale } = await run([NOTE(), '{"holds": false, "why": "Fixed it: the test no longer names the county."}'], true);
    expect(h.requests).toHaveLength(2);
    expect(h.requests[1].messages[0].content[0].text).toContain("Fixed it");
    expect(notes).toHaveLength(0);
    expect(stale[0].data.why).toContain("Fixed it");
  });
  test("later turns that leave it open: shown", async () => {
    const { notes } = await run([NOTE(), '{"holds": true}'], true);
    expect(notes).toHaveLength(1);
  });
  test("an unreadable recheck keeps the grounded note", async () => {
    const { notes } = await run([NOTE(), "no json"], true);
    expect(notes).toHaveLength(1);
  });
  test("stakes and decision ride on the note", async () => {
    const { notes } = await run([NOTE({ stakes: "Private repo; only collaborators see it.", decision: "Purge the commit or leave it." })], false);
    expect(notes[0].data.note).toMatchObject({ stakes: "Private repo; only collaborators see it.", decision: "Purge the commit or leave it." });
  });
});

test("Send approves the preview even when another line arrives during confirmation", async () => {
  const h = harness();
  await h.emit("session_start");
  await h.run("hud", "add reviewed");
  h.ctx.ui.confirm = async () => {
    await h.run("hud", "add still drafting");
    return true;
  };
  await h.run("hud", "send");
  expect(h.entries.at(-1).data.lines).toEqual(["reviewed"]);
  expect(h.widgets.at(-1)?.[0]).toContain("draft changed");
  expect((await h.start()).sections[SECTION]).not.toContain("still drafting");
});

test("a branch change retires an open confirmation", async () => {
  const h = harness();
  await h.emit("session_start");
  await h.run("hud", "add on branch A");
  h.ctx.ui.confirm = async () => {
    await h.emit("session_tree");
    return true;
  };
  await h.run("hud", "send");
  expect(h.entries.some(e => e.data?.k === "approve")).toBe(false);
});

test("removing one of two identical Memory lines preserves its sibling", async () => {
  const h = harness([], { picks: ["Remove a Memory line", "2."] });
  await h.emit("session_start");
  await h.run("hud", "add duplicate");
  await h.run("hud", "add duplicate");
  await h.run("hud", "");
  expect(h.entries.at(-1).data.lines).toEqual(["duplicate"]);
});

test("a delayed observer reply after off leaves no note or cursor", async () => {
  const h = harness([NOTE()], { duringCall: () => { void h.run("hud", "observer off"); } });
  await h.emit("session_start");
  await h.run("hud", "observer panel");
  await h.turns(REVIEW_EVERY);
  expect(h.requests).toHaveLength(1);
  expect(h.entries.filter(e => ["reviewed", "note"].includes(e.data?.k))).toHaveLength(0);
});

test("an old longer snapshot cannot receipt a newly approved prefix", async () => {
  const h = harness();
  await h.emit("session_start");
  await h.run("hud", "add task");
  await h.run("hud", "send");
  const { sections } = await h.start();
  sections[SECTION] += " that was superseded";
  await h.emit("context_with_system", { messages: [{ role: "system", sections }] });
  expect(h.entries.some(e => e.data?.k === "delivered")).toBe(false);
});

test("a failed observer settings write keeps the effective mode and reports it", async () => {
  const h = harness();
  await h.emit("session_start");
  await h.run("hud", "observer off");
  const dir = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = settingsPath(); // a file cannot contain another settings file
  try {
    await h.run("hud", "observer forward");
    expect(h.notes.at(-1)).toContain("Still off");
    await h.turns(REVIEW_EVERY);
    expect(h.requests).toHaveLength(0);
  } finally {
    process.env.PI_CODING_AGENT_DIR = dir;
  }
});

test("a heads-up delivered while its menu is open cannot start a second turn", async () => {
  const h = harness([NOTE()]);
  await h.emit("session_start");
  await h.run("hud", "observer forward");
  await h.turns(REVIEW_EVERY);
  h.ctx.ui.select = async (_title, options) => {
    if (options.some(o => o.startsWith("1."))) return options[0];
    await h.start();
    return "Send to the agent now";
  };
  await h.run("hud", "");
  expect(h.entries.some(e => e.data?.how === "sent with your message")).toBe(true);
  expect(h.sent).toHaveLength(0);
});

test("a rejected busy steer preserves the note for the next user message", async () => {
  const h = harness([NOTE()], { idle: false, refuseSteer: true });
  await h.emit("session_start");
  await h.run("hud", "observer forward");
  await h.turns(REVIEW_EVERY);
  expect(h.entries.find(e => e.data?.k === "note").data.note.how).toBe("waits for your next message");
  expect((await h.start()).result.message.content).toContain("skipped the migration test");
});

test("switching branch during the recheck discards its note and review cursor", async () => {
  const h = harness([NOTE(), '{"holds":true}'], {
    duringCall: count => {
      if (count === 1) h.say("assistant", "new work since the first look");
      if (count === 2) void h.emit("session_tree");
    },
  });
  await h.emit("session_start");
  await h.run("hud", "observer panel");
  await h.turns(REVIEW_EVERY);
  expect(h.requests).toHaveLength(2);
  expect(h.entries.filter(e => ["reviewed", "note", "stale"].includes(e.data?.k))).toHaveLength(0);
});
