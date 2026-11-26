// The HUD's state is a fold over its own session entries (pi.appendEntry), which never enter the
// model's context. The Log and the notes come from every entry, so a /tree jump loses no
// thought; Memory comes from the active branch, because it is part of what that history sent.
import type { Tag } from "./observer";

export const TYPE = "binnacle-hud";
export const LOG_MAX = 100;
export const MEMORY_MAX = 20;
export const TEXT_MAX = 2_000; // characters in one thought or Memory line
export const NOTES_MAX = 50;

export type Thought = { text: string; at: number };
export type Approved = { lines: string[]; at: number };
/** How a note reached the agent, or that it did not. */
export type How = "for you only" | "steered into the run" | "waits for your next message" | "sent with your message";
export type Mark = "known" | "dismissed" | "read" | "wrong" | "useful";
export type Note = { key: string; tag: Tag; line: string; details: string; evidence?: string; agentKnows: boolean; at: number; how: How; mark?: Mark; version?: string };
/** Marks that take a note off the panel. */
export const CLOSED: ReadonlySet<Mark | undefined> = new Set(["known", "dismissed", "wrong", "useful"]);

export type Rec =
  | { k: "thought"; text: string; at: number }
  | { k: "forget"; at: number }
  | { k: "draft"; lines: string[] }
  | { k: "approve"; lines: string[]; at: number }
  | { k: "delivered"; at: number; since: number }
  | { k: "note"; note: Note }
  | { k: "how"; key: string; how: How }
  | { k: "mark"; key: string; mark: Mark }
  | { k: "reviewed"; upTo: string };

export type State = {
  log: Thought[];
  draft: string[];
  approved: Approved | null;
  /** The Send a model request last carried (its `at`), and when one first did. */
  delivered: { at: number; since: number } | null;
  notes: Note[];
  reviewedUpTo: string | null;
};

type EntryLike = { type: string; customType?: string; data?: unknown; id?: string };

const isRecord = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null;
const strings = (v: unknown): v is string[] => Array.isArray(v) && v.every((s) => typeof s === "string");

/** Our records in order. A record that does not have its fields is skipped: the session file is outside our control. */
export function records(entries: readonly EntryLike[]): Rec[] {
  const out: Rec[] = [];
  for (const e of entries) {
    if (e.type !== "custom" || e.customType !== TYPE || !isRecord(e.data)) continue;
    const d = e.data;
    const ok =
      (d.k === "thought" && typeof d.text === "string" && typeof d.at === "number")
      || (d.k === "forget" && typeof d.at === "number")
      || (d.k === "draft" && strings(d.lines))
      || (d.k === "approve" && strings(d.lines) && typeof d.at === "number")
      || (d.k === "delivered" && typeof d.at === "number" && typeof d.since === "number")
      || (d.k === "note" && isRecord(d.note) && typeof d.note.key === "string" && typeof d.note.line === "string")
      || ((d.k === "how" || d.k === "mark") && typeof d.key === "string")
      || (d.k === "reviewed" && typeof d.upTo === "string");
    if (ok) out.push(d as Rec);
  }
  return out;
}

export function fold(all: readonly EntryLike[], branch: readonly EntryLike[]): State {
  const s: State = { log: [], draft: [], approved: null, delivered: null, notes: [], reviewedUpTo: null };
  for (const r of records(all)) {
    if (r.k === "thought") s.log = [...s.log, { text: r.text, at: r.at }].slice(-LOG_MAX);
    else if (r.k === "forget") s.log = s.log.filter((t) => t.at !== r.at);
    else if (r.k === "note") s.notes = [...s.notes.filter((n) => n.key !== r.note.key), r.note].slice(-NOTES_MAX);
    else if (r.k === "how") s.notes = s.notes.map((n) => (n.key === r.key ? { ...n, how: r.how } : n));
    else if (r.k === "mark") s.notes = s.notes.map((n) => (n.key === r.key ? { ...n, mark: r.mark } : n));
    else if (r.k === "reviewed") s.reviewedUpTo = r.upTo;
  }
  for (const r of records(branch)) {
    if (r.k === "draft") s.draft = r.lines.slice(0, MEMORY_MAX);
    // Sending an empty Memory withdraws it from later requests.
    else if (r.k === "approve") s.approved = r.lines.length ? { lines: r.lines.slice(0, MEMORY_MAX), at: r.at } : null;
    else if (r.k === "delivered") s.delivered = { at: r.at, since: r.since };
  }
  return s;
}

export const clip = (text: string) => Array.from(text.trim()).slice(0, TEXT_MAX).join("");
export const same = (a: readonly string[], b: readonly string[]) => a.length === b.length && a.every((x, i) => x === b[i]);

const hhmm = (at: number) => new Date(at).toTimeString().slice(0, 5);

/** The system prompt section the approved snapshot rides in. */
export const SECTION = "binnacle_memory";
export const memoryText = (snap: Approved) =>
  [`Memory the person approved at ${hhmm(snap.at)}. Treat it as their standing notes for this session:`, ...snap.lines.map((l) => `- ${l}`)].join("\n");

export type Tone = "accent" | "success" | "warning" | null;
/** The Memory status line. Only a model request carrying the snapshot says the agent has it; a Send alone is pending. */
export function statusOf(s: Pick<State, "draft" | "approved" | "delivered">): { text: string; tone: Tone; send: boolean } {
  const snap = s.approved;
  if (!snap) return { text: s.draft.length ? "Not sent." : "Empty.", tone: null, send: s.draft.length > 0 };
  const arrived = s.delivered?.at === snap.at;
  if (!same(s.draft, snap.lines)) {
    return arrived
      ? { text: `Changed since Send. The agent has the ${hhmm(snap.at)} version.`, tone: "accent", send: true }
      : { text: `Changed since Send. The ${hhmm(snap.at)} version has not reached the agent yet.`, tone: "accent", send: true };
  }
  return arrived
    ? { text: `In the agent's instructions since ${hhmm(s.delivered!.since)}.`, tone: "success", send: false }
    : { text: `Sent at ${hhmm(snap.at)}. Reaches the agent with its next request.`, tone: null, send: false };
}
