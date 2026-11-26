import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { grounded, newest, recordOf, OUTPUT_TOKENS, parseReply, PROMPT_VERSION, quoted, repeats, serialize, SYSTEM, TRANSCRIPT_CHARS, userMessage, Watch, type Msg } from "./observer";
import { type Kit, Panel } from "./panel";
import { CLOSED, clip, fold, type How, type Mark, MEMORY_MAX, memoryText, type Note, type Rec, SECTION, type State, TYPE } from "./state";

/** off: no looks. panel: notes stay with the person. forward: notes also reach the agent. */
export type Mode = "off" | "panel" | "forward";
const MODES: readonly Mode[] = ["off", "panel", "forward"];
// panel until the prompt measures >=50% worth-it and <=10% not-true on delivered notes (README).
export const DEFAULT_MODE: Mode = "panel";
/** A strip headline clears after this many of the person's prompts, read or not. */
export const STRIP_PROMPTS = 2;

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
  let panel: { view: Panel; handle?: { focus(): void; unfocus(): void; isFocused(): boolean; setHidden(h: boolean): void }; done: () => void } | undefined;
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

  async function show(c: ExtensionContext, focus: boolean, target?: "log" | "memory") {
    if (c.mode !== "tui") {
      if (c.hasUI) c.ui.notify("The Binnacle panel needs the terminal UI. /log <text> keeps a thought from here.", "info");
      return;
    }
    if (panel) {
      if (target) panel.view.target = target;
      if (focus) panel.handle?.focus();
      return;
    }
    const k = await loadKit();
    if (!k) return c.ui.notify("Binnacle: the TUI kit did not load.", "error");
    void c.ui.custom<void>(
      (tui, theme, _keys, done) => {
        const view = new Panel(k, theme, () => state, {
          keep: (text) => keep(text),
          addMemory: (text) => add({ k: "draft", lines: [...state.draft, clip(text)].slice(0, MEMORY_MAX) }),
          removeMemory: (i) => add({ k: "draft", lines: state.draft.filter((_, n) => n !== i) }),
          send: () => approve(),
          mark: (key, mark) => markNote(key, mark),
          forget: (at) => add({ k: "forget", at }),
          escape: () => panel?.handle?.unfocus(),
          close: () => done(),
        });
        if (target) view.target = target;
        panel = { view, done: () => done() };
        const render = tui.requestRender.bind(tui);
        return Object.assign(view, {
          handleInput: (d: string) => (Panel.prototype.handleInput.call(view, d), render()),
          dispose: () => (panel = undefined),
        });
      },
      {
        overlay: true,
        overlayOptions: () => {
          const cols = process.stdout.columns ?? 120;
          return cols >= 110
            ? { anchor: "top-right", width: "36%", minWidth: 40, maxHeight: "85%", margin: { top: 1, right: 1 }, nonCapturing: true }
            : { anchor: "top-center", width: "94%", maxHeight: "70%", margin: { top: 1 }, nonCapturing: true };
        },
        onHandle: (handle) => {
          if (panel) panel.handle = handle;
          if (focus) handle.focus();
        },
      },
    ).finally(() => (panel = undefined));
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

  function lookAt(branch: readonly EntryLike[]) {
    const from = state.reviewedUpTo ? branch.findIndex((e) => e.id === state.reviewedUpTo) + 1 : 0;
    const lastCompaction = branch.findLastIndex((e) => e.type === "compaction");
    const start = Math.max(from, lastCompaction + 1);
    const msgs = (es: readonly EntryLike[]): Msg[] =>
      es.flatMap((e): Msg[] =>
        e.type === "message" && e.message ? [e.message]
        : e.type === "custom_message" ? [{ role: "custom", customType: e.customType, content: e.content }]
        : []);
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
      deliver(c, { key: `${Date.now().toString(36)}`, tag: r.tag, line: r.line, details: r.details, evidence: r.evidence, agentKnows: r.agentKnows, at: Date.now(), how: "for you only", version: PROMPT_VERSION });
    } catch {
      // A failed look shows nothing and moves no cursor; the next look reads these turns again.
    } finally {
      if (looking === ac) looking = undefined;
    }
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
      if (!args.trim()) return show(c, true, "log");
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
      if (word === "send") {
        if (!state.draft.length && !state.approved) return c.ui.notify("Memory is empty.", "info");
        const ok = c.hasUI && (await c.ui.confirm("Send Memory", `Give these ${state.draft.length} lines to the agent's instructions? It keeps them until you send again.\n\n${state.draft.map((l) => `- ${l}`).join("\n")}`));
        if (!ok) return;
        approve();
        return c.ui.notify("Sent. It reaches the agent with its next request.", "info");
      }
      return show(c, true);
    },
  });

  pi.registerShortcut("alt+h", {
    description: "Binnacle: open the panel, or move the keys between it and the prompt",
    handler: async (c) => {
      ctx = c;
      if (!panel) return show(c, true);
      if (panel.handle?.isFocused()) panel.handle.unfocus();
      else panel.handle?.focus();
    },
  });
}
