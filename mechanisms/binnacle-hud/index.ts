import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { grounded, newest, recordOf, OUTPUT_TOKENS, parseRecheck, parseReply, PROMPT_VERSION, quoted, RECHECK, recheckMessage, repeats, serialize, SYSTEM, TRANSCRIPT_CHARS, userMessage, Watch, type Msg } from "./observer";
import { type Kit, openNotes, Panel } from "./panel";
import { CLOSED, clip, fold, type How, type Mark, MEMORY_MAX, memoryText, type Note, type Rec, SECTION, type State, statusOf, TYPE } from "./state";

/** off: no looks. panel: notes stay with the person. forward: notes also reach the agent. */
export type Mode = "off" | "panel" | "forward";
const MODES: readonly Mode[] = ["off", "panel", "forward"];
// panel until the prompt measures >=50% worth-it and <=10% not-true on delivered notes (README).
export const DEFAULT_MODE: Mode = "panel";
/** A strip headline clears after this many of the person's prompts, read or not. */
export const STRIP_PROMPTS = 2;
/** Rereads of later turns before a note is shown; see stillHolds. */
export const RECHECKS_MAX = 3;

// One setting for every session (HAX guideline 17, global controls), beside Pi's own settings.
export const settingsPath = () => join(process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent"), "binnacle-hud.json");
export function readMode(path = settingsPath()): Mode {
  try {
    const v = (JSON.parse(readFileSync(path, "utf-8")) as { observer?: unknown }).observer;
    return MODES.find((m) => m === v) ?? DEFAULT_MODE;
  } catch {
    return DEFAULT_MODE;
  }
}
function writeMode(mode: Mode, path = settingsPath()) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify({ observer: mode }, null, 2)}
`);
}

/**
 * Binnacle HUD for Pi: a Log of thoughts kept beside the session, a Memory the person approves
 * into the agent's system prompt, and an observer that reads the session every few turns and
 * raises what the person should know. The Log never reaches a model; Memory reaches it only
 * after Send; a note goes to the agent unless the agent already stated it.
 */
export default function (pi: ExtensionAPI) {
  let ctx: ExtensionContext | undefined;
  let state: State = fold([], []);
  let kit: Kit | undefined;
  let panel: { done: () => void } | undefined;
  let watch = new Watch();
  let looking: AbortController | undefined;
  let mode: Mode = DEFAULT_MODE;
  let prompts: number[] = []; // when the person sent each prompt this session

  const refold = () => {
    if (!ctx) return;
    state = fold(ctx.sessionManager.getEntries(), ctx.sessionManager.getBranch());
    paint();
  };
  const add = (rec: Rec) => {
    pi.appendEntry(TYPE, rec);
    refold();
  };

  // --- surfaces -------------------------------------------------------------------------------
  function paint() {
    if (!ctx?.hasUI) return;
    const t = ctx.ui.theme;
    const fresh = state.notes.filter((n) => !n.mark && prompts.filter((p) => p > n.at).length < STRIP_PROMPTS).at(-1);
    const parts: string[] = [];
    if (state.approved) parts.push(state.delivered?.at === state.approved.at ? "Memory in instructions" : "Memory sent");
    else if (state.draft.length) parts.push("Memory not sent");
    const open = state.notes.filter((n) => !CLOSED.has(n.mark)).length;
    if (open) parts.push(`${open} heads-up${open === 1 ? "" : "s"}`);
    if (state.log.length) parts.push(`${state.log.length} kept`);
    const line = fresh
      ? `${t.fg("warning", "◆")} ${t.bold(fresh.tag === "heads-up" ? "Heads up" : "Worth knowing")} ${t.fg("dim", "·")} ${fresh.line} ${t.fg("dim", "· alt+h")}`
      : parts.length
        ? `${t.fg("accent", "◆")} ${t.fg("dim", `Binnacle · ${parts.join(" · ")} · alt+h`)}`
        : undefined;
    ctx.ui.setWidget(TYPE, line ? [line] : undefined);
  }

  async function loadKit(): Promise<Kit | undefined> {
    if (kit) return kit;
    try {
      kit = (await import("@earendil-works/pi-tui")) as unknown as Kit;
    } catch {
      kit = undefined;
    }
    return kit;
  }

  // The panel only displays; it never takes the keys, so the prompt stays the one place to type.
  async function show(c: ExtensionContext) {
    if (panel || c.mode !== "tui") return;
    const k = await loadKit();
    if (!k) return c.ui.notify("Binnacle: the TUI kit did not load.", "error");
    void c.ui.custom<void>(
      (_tui, theme, _keys, done) => {
        panel = { done: () => done() };
        return Object.assign(new Panel(k, theme, () => state), { dispose: () => (panel = undefined) });
      },
      {
        overlay: true,
        overlayOptions: () => {
          const cols = process.stdout.columns ?? 120;
          return cols >= 110
            ? { anchor: "top-right", width: "36%", minWidth: 40, maxHeight: "85%", margin: { top: 1, right: 1 }, nonCapturing: true }
            : { anchor: "top-center", width: "94%", maxHeight: "70%", margin: { top: 1 }, nonCapturing: true };
        },
      },
    ).finally(() => (panel = undefined));
  }

  // --- alt+h: one menu for every action -----------------------------------------------------
  const SEND = "Send to the agent now";
  const COPY = "Copy to the clipboard";
  const NOTE_MARKS: Array<[string, Mark]> = [["Useful: worth receiving", "useful"], ["I knew this", "known"], ["Wrong", "wrong"], ["Dismiss", "dismissed"]];
  const SENT: ReadonlySet<How> = new Set(["steered into the run", "sent with your message", "you sent it"]);

  async function menu(c: ExtensionContext) {
    if (!c.hasUI) return;
    await show(c);
    const notes = openNotes(state);
    const rows = new Map<string, () => Promise<unknown> | unknown>();
    notes.forEach((n, i) => rows.set(`${i + 1}. ${n.line}`, () => noteMenu(c, n)));
    rows.set("Keep a thought in the Log", () => logPrompt(c));
    rows.set("Add a Memory line", async () => {
      if (state.draft.length >= MEMORY_MAX) return c.ui.notify(`Memory keeps at most ${MEMORY_MAX} lines.`, "warning");
      const text = clip((await c.ui.input("Add a Memory line", "a fact the agent should keep")) ?? "");
      if (text) add({ k: "draft", lines: [...state.draft, text] });
    });
    if (statusOf(state).send) rows.set("Send Memory to the agent", () => sendMemory(c));
    if (state.draft.length) rows.set("Remove a Memory line", async () => {
      const pick = await c.ui.select("Remove which Memory line?", state.draft);
      if (pick !== undefined) add({ k: "draft", lines: state.draft.filter((l) => l !== pick) });
    });
    if (state.log.length) rows.set("Forget a thought", async () => {
      const recent = state.log.slice(-10).reverse();
      const pick = await c.ui.select("Forget which thought?", recent.map((t) => t.text));
      const hit = recent.find((t) => t.text === pick);
      if (hit) add({ k: "forget", at: hit.at });
    });
    rows.set("Hide the panel", () => panel?.done());
    const title = notes.length ? `Binnacle · ${notes.length} heads-up${notes.length === 1 ? "" : "s"}` : "Binnacle · no heads-ups";
    const pick = await c.ui.select(title, [...rows.keys()]);
    if (pick !== undefined) await rows.get(pick)?.();
  }

  async function noteMenu(c: ExtensionContext, n: Note) {
    if (!n.mark) markNote(n.key, "read");
    const head = [n.line, n.stakes && `Why it matters: ${n.stakes}`, n.decision && `Your call: ${n.decision}`].filter(Boolean);
    const body = [...head, "", n.details, n.evidence ? `\nFrom the record: “${n.evidence}”` : "", `\n${n.how}`].join("\n");
    const options = [...(SENT.has(n.how) ? [] : [SEND]), COPY, ...NOTE_MARKS.map(([label]) => label)];
    const pick = await c.ui.select(body, options);
    if (pick === SEND) {
      // Steer a busy agent before its next model call; start a turn on an idle one.
      pi.sendMessage({ customType: TYPE, content: quoted(n), display: true, details: { key: n.key } }, { deliverAs: "steer", triggerTurn: true });
      add({ k: "how", key: n.key, how: "you sent it" });
      markNote(n.key, "useful"); // sending it says it was worth receiving
    } else if (pick === COPY) {
      const text = [n.line, "", n.details, n.evidence ? `\nFrom the record: "${n.evidence}"` : ""].join("\n").trim();
      try {
        const { copyToClipboard } = await import("@earendil-works/pi-coding-agent");
        await copyToClipboard(text);
        c.ui.notify("Heads-up copied.", "info");
      } catch {
        c.ui.notify("Could not reach the clipboard.", "error");
      }
    } else {
      const mark = NOTE_MARKS.find(([label]) => label === pick)?.[1];
      if (mark) markNote(n.key, mark);
    }
  }

  async function logPrompt(c: ExtensionContext) {
    const text = await c.ui.input("Keep a thought in the Log", "never reaches the model");
    if (text && keep(text)) c.ui.notify("Kept in the Log.", "info");
  }

  async function sendMemory(c: ExtensionContext) {
    if (!state.draft.length && !state.approved) return c.ui.notify("Memory is empty.", "info");
    const ok = await c.ui.confirm("Send Memory", `Give these ${state.draft.length} lines to the agent's instructions? It keeps them until you send again.\n\n${state.draft.map((l) => `- ${l}`).join("\n")}`);
    if (!ok) return;
    approve();
    c.ui.notify("Sent. It reaches the agent with its next request.", "info");
  }

  // --- Log and Memory -------------------------------------------------------------------------
  function keep(text: string) {
    const t = clip(text);
    if (!t) return false;
    add({ k: "thought", text: t, at: Date.now() });
    return true;
  }

  function approve() {
    add({ k: "approve", lines: [...state.draft], at: Date.now() });
  }

  function markNote(key: string, mark: Mark) {
    add({ k: "mark", key, mark });
    if (mark === "dismissed" || mark === "wrong") watch.dismissed();
    if (mark === "read" || mark === "useful") watch.valued();
  }

  // --- the observer ---------------------------------------------------------------------------
  type EntryLike = { id: string; type: string; message?: Msg; summary?: string; customType?: string; content?: unknown };

  const msgs = (es: readonly EntryLike[]): Msg[] =>
    es.flatMap((e): Msg[] =>
      e.type === "message" && e.message ? [e.message]
      : e.type === "custom_message" ? [{ role: "custom", customType: e.customType, content: e.content }]
      : []);

  function lookAt(branch: readonly EntryLike[]) {
    const from = state.reviewedUpTo ? branch.findIndex((e) => e.id === state.reviewedUpTo) + 1 : 0;
    const lastCompaction = branch.findLastIndex((e) => e.type === "compaction");
    const start = Math.max(from, lastCompaction + 1);
    const fresh = msgs(branch.slice(start));
    const hasRequest = fresh.some((m) => m.role === "user");
    const before = hasRequest ? undefined : msgs(branch.slice(0, start)).findLast((m) => m.role === "user");
    return {
      request: before ? serialize([before], TYPE).replace(/^\[Person\]: /, "") : "",
      summary: lastCompaction >= 0 ? String(branch[lastCompaction]!.summary ?? "") : "",
      turns: newest(serialize(fresh, TYPE), TRANSCRIPT_CHARS),
      upTo: branch.at(-1)?.id,
    };
  }

  async function review(c: ExtensionContext) {
    if (looking || mode === "off" || !c.hasUI || !c.model) return;
    const branch = c.sessionManager.getBranch() as unknown as EntryLike[];
    const look = lookAt(branch);
    if (!look.upTo || !look.turns.trim()) return;
    watch.reviewed();
    const by = (m?: Mark) => state.notes.filter((n) => n.mark === m).map((n) => n.line);
    const text = userMessage({ ...look, raised: state.notes.filter((n) => !n.mark || n.mark === "read").map((n) => n.line), known: [...by("known"), ...by("useful")], dismissed: by("dismissed") });
    const ac = (looking = new AbortController());
    try {
      const reply = await c.modelRegistry.complete(
        c.model,
        { systemPrompt: SYSTEM, messages: [{ role: "user", content: [{ type: "text", text }], timestamp: Date.now() }] },
        // One-off call: a cache write costs extra and is never read back.
        { signal: ac.signal, maxTokens: OUTPUT_TOKENS, cacheRetention: "none", sessionId: `${TYPE}-observer-${Date.now()}` },
      );
      if (ac.signal.aborted || reply.stopReason === "error" || reply.stopReason === "aborted") return;
      const said = reply.content.filter((b) => b.type === "text").map((b) => (b as { text: string }).text).join("\n");
      const r = parseReply(said);
      if (r.kind === "bad") return; // not a review: the cursor stays, so these turns are looked at again
      add({ k: "reviewed", upTo: look.upTo });
      if (r.kind !== "note" || !grounded(r.evidence, recordOf(text)) || repeats(r.line, state.notes.map((n) => n.line))) return;
      if (!(await stillHolds(c, r, look.upTo, ac.signal))) return;
      deliver(c, { key: `${Date.now().toString(36)}`, tag: r.tag, line: r.line, details: r.details, evidence: r.evidence, agentKnows: r.agentKnows, at: Date.now(), how: "for you only", version: PROMPT_VERSION, ...(r.stakes && { stakes: r.stakes }), ...(r.decision && { decision: r.decision }) });
    } catch {
      // A failed look shows nothing and moves no cursor; the next look reads these turns again.
    } finally {
      if (looking === ac) looking = undefined;
    }
  }

  // The statechart in the README: the agent keeps working while the observer answers, so turns
  // that arrived meanwhile are read before a note is shown, and again if more arrive during that
  // read. A note they settled is recorded as stale and never shown.
  async function stillHolds(c: ExtensionContext, note: { line: string; details: string }, readUpTo: string, signal: AbortSignal): Promise<boolean> {
    for (let pass = 0; pass < RECHECKS_MAX; pass++) {
      const branch = c.sessionManager.getBranch() as unknown as EntryLike[];
      const turns = serialize(msgs(branch.slice(branch.findIndex((e) => e.id === readUpTo) + 1)), TYPE);
      if (!turns.trim()) return true;
      readUpTo = branch.at(-1)!.id;
      const reply = await c.modelRegistry.complete(
        c.model!,
        { systemPrompt: RECHECK, messages: [{ role: "user", content: [{ type: "text", text: recheckMessage(note, newest(turns, TRANSCRIPT_CHARS)) }], timestamp: Date.now() }] },
        { signal, maxTokens: OUTPUT_TOKENS, cacheRetention: "none", sessionId: `${TYPE}-recheck-${Date.now()}` },
      );
      if (signal.aborted) return false;
      if (reply.stopReason === "error" || reply.stopReason === "aborted") return true; // the note was grounded; a failed check keeps it
      const v = parseRecheck(reply.content.filter((b) => b.type === "text").map((b) => (b as { text: string }).text).join("\n"));
      if (!v.holds) {
        add({ k: "stale", line: note.line, why: v.why, version: PROMPT_VERSION });
        return false;
      }
    }
    // shortcut: an agent still moving after RECHECKS_MAX rereads gets the note as last read; holding it until agent_end would close this.
    return true;
  }

  // A note the agent already stated is for the person only. Otherwise a busy agent gets it
  // before its next model call; an idle one gets it with the person's next message.
  function deliver(c: ExtensionContext, note: Note) {
    let how: How = "for you only";
    if (!note.agentKnows && mode === "forward") {
      if (c.isIdle()) how = "waits for your next message";
      else {
        pi.sendMessage({ customType: TYPE, content: quoted(note), display: true, details: { key: note.key } }, { deliverAs: "steer" });
        how = "steered into the run";
      }
    }
    add({ k: "note", note: { ...note, how } });
  }

  // --- events ---------------------------------------------------------------------------------
  pi.on("session_start", async (_e, c) => {
    ctx = c;
    watch = new Watch();
    prompts = [];
    mode = readMode();
    refold();
    void loadKit();
  });
  pi.on("session_tree", async (_e, c) => {
    ctx = c;
    refold();
  });
  pi.on("session_shutdown", async () => {
    looking?.abort();
    panel?.done();
    ctx = undefined;
  });

  pi.on("before_agent_start", async (event, c) => {
    ctx = c;
    const sections = event.systemPromptOptions.sections ?? (event.systemPromptOptions.sections = {});
    if (state.approved?.lines.length) sections[SECTION] = memoryText(state.approved);
    else delete sections[SECTION];
    if (event.messageType !== "user") return;
    prompts.push(Date.now());
    paint();
    const waiting = mode === "forward" ? state.notes.filter((n) => n.how === "waits for your next message" && !CLOSED.has(n.mark)) : [];
    if (!waiting.length) return;
    for (const n of waiting) add({ k: "how", key: n.key, how: "sent with your message" });
    return { message: { customType: TYPE, content: waiting.map(quoted).join("\n\n"), display: true, details: { keys: waiting.map((n) => n.key) } } };
  });

  // Delivery is a fact about a request, not a Send: record it when a request carries the snapshot.
  pi.on("context_with_system", async (event) => {
    const snap = state.approved;
    if (!snap || state.delivered?.at === snap.at) return;
    let carried: string | null | undefined;
    for (const m of event.messages as Array<{ role: string; sections?: Record<string, string | null> }>) {
      if (m.role === "system" && m.sections && SECTION in m.sections) carried = m.sections[SECTION];
    }
    if (carried?.includes(memoryText(snap))) add({ k: "delivered", at: snap.at, since: Date.now() });
  });

  pi.on("turn_end", async (_e, c) => {
    if (watch.turn()) void review(c);
  });
  pi.on("agent_settled", async (e, c) => {
    if (!e.aborted && watch.settled()) void review(c);
  });

  // A note handed to the agent shows in the transcript as its headline, with details on expand.
  pi.registerMessageRenderer(TYPE, (message, { expanded }, theme) => {
    const d = (message.details ?? {}) as { key?: string; keys?: string[] };
    const keys = d.key ? [d.key] : d.keys ?? [];
    const notes = state.notes.filter((n) => keys.includes(n.key));
    if (!kit || !notes.length) return undefined;
    const k = kit;
    return {
      render(width: number) {
        const out: string[] = [];
        for (const n of notes) {
          out.push(`${theme.fg("warning", "◆")} ${theme.fg("dim", "Note given to the agent ·")} ${n.line}`);
          if (expanded) out.push(...k.wrapTextWithAnsi(n.details, Math.max(10, width - 4)).map((l) => `  ${l}`));
        }
        return out.flatMap((l) => k.wrapTextWithAnsi(l, width)).map((l) => k.truncateToWidth(l, width));
      },
      invalidate() {},
    };
  });

  // --- commands and keys ----------------------------------------------------------------------
  pi.registerCommand("log", {
    description: "Keep a thought in the Binnacle Log. It never reaches the model.",
    handler: async (args, c) => {
      ctx = c;
      if (!args.trim()) return logPrompt(c);
      keep(args);
      if (c.hasUI) c.ui.notify("Kept in the Log.", "info");
    },
  });

  pi.registerCommand("hud", {
    description: "Binnacle panel: /hud, /hud add <Memory line>, /hud send, /hud observer off|panel|forward, /hud close",
    getArgumentCompletions: (p) => ["add ", "send", "close", "observer off", "observer panel", "observer forward"].filter((x) => x.startsWith(p)).map((x) => ({ value: x, label: x.trim() })),
    handler: async (args, c) => {
      ctx = c;
      const [word = "", ...rest] = args.trim().split(/\s+/);
      if (word === "close") return panel?.done();
      if (word === "observer") {
        const want = MODES.find((m) => m === rest[0]);
        if (!want) return c.ui.notify(`Observer is ${mode}. /hud observer off stops it; panel keeps notes with you; forward also gives them to the agent.`, "info");
        mode = want;
        writeMode(want);
        // A note queued for the agent stays with the person once forwarding stops.
        if (want !== "forward") for (const n of state.notes.filter((x) => x.how === "waits for your next message")) add({ k: "how", key: n.key, how: "for you only" });
        return c.ui.notify(`Observer ${want === "off" ? "off" : want === "panel" ? "on, notes stay with you" : "on, notes also go to the agent"}. This applies to every session.`, "info");
      }
      if (word === "add") {
        const text = clip(rest.join(" "));
        if (!text) return c.ui.notify("Nothing added: write the line after /hud add.", "warning");
        if (state.draft.length >= MEMORY_MAX) return c.ui.notify(`Memory keeps at most ${MEMORY_MAX} lines.`, "warning");
        add({ k: "draft", lines: [...state.draft, text] });
        return c.ui.notify(`Added to Memory. Not sent: /hud send gives it to the agent.`, "info");
      }
      if (word === "send") return sendMemory(c);
      return menu(c);
    },
  });

  pi.registerShortcut("alt+h", {
    description: "Binnacle: act on a heads-up, or manage Memory and the Log",
    handler: async (c) => {
      ctx = c;
      await menu(c);
    },
  });
}
