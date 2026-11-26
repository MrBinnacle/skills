// Builds Inspect samples from Claude Code transcripts: each sample is what the observer would
// have been shown at one checkpoint, made by the real serialize/userMessage/SYSTEM from
// observer.ts so the eval tests the shipped prompt, not a copy. This is the only hand-written
// part of the eval; Inspect runs, logs and later scores it (observer_task.py).
//
//   bun mechanisms/binnacle-hud/eval/slices.ts <out-dir> <transcript.jsonl>... [--notes forwarded.jsonl] [--per-session N] [--seed S]
//
// Transcripts hold private work: write <out-dir> outside the repository.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { newest, PROMPT_VERSION, REVIEW_EVERY, serialize, SETTLE_MIN, SYSTEM, TRANSCRIPT_CHARS, userMessage, type Msg } from "../observer";
import { TYPE } from "../state";

/** Text Claude Code puts in a user turn that carries a side-agent note into the conversation. */
export const NOTE_CARRIERS = ["Here is a note offered by a side agent", "A side agent watching this session offers this note", "The binnacle-hud plugin sent a message", "The side-notes plugin sent a message"];

type Row = { type?: string; isSidechain?: boolean; isCompactSummary?: boolean; isMeta?: boolean; timestamp?: string; message?: { id?: string; role?: string; content?: unknown } };
export type Turn = { at: string; msg: Msg; human: boolean; compact?: string };

const blocks = (c: unknown): Array<Record<string, unknown>> => (Array.isArray(c) ? c.filter((b) => typeof b === "object" && b !== null) : []);
const textOf = (c: unknown) => (typeof c === "string" ? c : blocks(c).filter((b) => b.type === "text").map((b) => String(b.text ?? "")).join("\n"));

/** Claude Code JSONL to the observer's message shapes, main thread only, one assistant message per API response. */
export function toTurns(jsonl: string): Turn[] {
  const out: Turn[] = [];
  const toolName = new Map<string, string>();
  let lastAssistantId: string | undefined;
  for (const line of jsonl.split(/\r?\n/)) {
    if (!line.startsWith("{")) continue;
    let r: Row;
    try {
      r = JSON.parse(line);
    } catch {
      continue;
    }
    if ((r.type !== "user" && r.type !== "assistant") || r.isSidechain || !r.message) continue;
    const at = r.timestamp ?? "";
    const c = r.message.content;
    if (r.type === "assistant") {
      const content: unknown[] = [];
      for (const b of blocks(c)) {
        if (b.type === "text") content.push({ type: "text", text: b.text });
        else if (b.type === "tool_use") {
          toolName.set(String(b.id), String(b.name));
          content.push({ type: "toolCall", name: b.name, arguments: b.input });
        }
      }
      // Claude Code writes one row per content block; rows of one response share message.id.
      const prev = out.at(-1);
      if (prev && r.message.id && r.message.id === lastAssistantId && prev.msg.role === "assistant") (prev.msg.content as unknown[]).push(...content);
      else out.push({ at, msg: { role: "assistant", content }, human: false });
      lastAssistantId = r.message.id;
      continue;
    }
    lastAssistantId = undefined;
    const results = blocks(c).filter((b) => b.type === "tool_result");
    for (const b of results) {
      out.push({ at, msg: { role: "toolResult", toolName: toolName.get(String(b.tool_use_id)), content: typeof b.content === "string" ? b.content : blocks(b.content), isError: b.is_error === true }, human: false });
    }
    const text = textOf(c).trim();
    if (!text || r.isMeta) continue;
    if (r.isCompactSummary) out.push({ at, msg: { role: "custom", customType: "compaction", content: "" }, human: false, compact: text });
    else if (NOTE_CARRIERS.some((p) => text.slice(0, 400).includes(p))) out.push({ at, msg: { role: "custom", customType: TYPE, content: text }, human: false });
    // The harness injects these as user turns; in Pi they would be extension messages, not the person.
    else if (/^<(task-notification|system-reminder|local-command|command-|bash-|user-memory)/.test(text)) out.push({ at, msg: { role: "custom", customType: "harness", content: text }, human: false });
    else out.push({ at, msg: { role: "user", content: text }, human: true });
  }
  return out;
}

/** Where the observer would look: every REVIEW_EVERY assistant turns, and at a hand-back with SETTLE_MIN unseen. */
export function checkpoints(turns: readonly Turn[]): number[] {
  const at: number[] = [];
  let unseen = 0;
  turns.forEach((t, i) => {
    if (t.msg.role === "assistant") {
      unseen++;
      if (unseen >= REVIEW_EVERY) (at.push(i), (unseen = 0));
    }
    const next = turns[i + 1];
    const handBack = t.msg.role === "assistant" && (!next || next.human);
    if (handBack && unseen >= SETTLE_MIN) (at.push(i), (unseen = 0));
  });
  return at;
}

/** The observer's message at checkpoint `end` (inclusive), looking back to the previous checkpoint. */
export function lookAt(turns: readonly Turn[], end: number, from: number): string {
  const compact = turns.slice(0, end + 1).findLastIndex((t) => t.compact !== undefined);
  const start = Math.max(from, compact + 1);
  const fresh = turns.slice(start, end + 1).map((t) => t.msg);
  const request = fresh.some((m) => m.role === "user") ? undefined : turns.slice(0, start).findLast((t) => t.human)?.msg;
  const raised = turns.slice(0, end + 1).filter((t) => t.msg.role === "custom" && t.msg.customType === TYPE)
    .map((t) => (textOf((t.msg as { content: unknown }).content).match(/·\s*([^\n]+)/)?.[1] ?? "").trim()).filter(Boolean);
  return userMessage({
    request: request ? serialize([request], TYPE).replace(/^\[Person\]: /, "") : "",
    summary: compact >= 0 ? turns[compact]!.compact! : "",
    turns: newest(serialize(fresh, TYPE), TRANSCRIPT_CHARS),
    raised, known: [], dismissed: [],
  });
}

// Small seeded PRNG so a rerun picks the same checkpoints.
function rng(seed: number) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 2 ** 32);
}

export type Forwarded = { n: number; file: string; ts: string; verdict?: string };
export type Sample = { id: string; input: Array<{ role: string; content: string }>; metadata: Record<string, string | number | boolean> };

export function build(files: readonly string[], forwarded: readonly Forwarded[], perSession: number, seed: number): Sample[] {
  const pick = rng(seed);
  const samples: Sample[] = [];
  for (const file of files) {
    const session = basename(file, ".jsonl");
    const turns = toTurns(readFileSync(file, "utf-8"));
    const cps = checkpoints(turns);
    const prev = (i: number) => cps.filter((c) => c < i).at(-1) ?? -1;
    const split = pick() < 0.5 ? "dev" : "test"; // by session, so one session never sits on both sides
    const meta = (kind: string, end: number) => ({ session, split, kind, at: turns[end]?.at ?? "", prompt: PROMPT_VERSION });
    const sample = (id: string, end: number, from: number, extra: Record<string, string | number | boolean>): Sample => ({
      id, input: [{ role: "system", content: SYSTEM }, { role: "user", content: lookAt(turns, end, from) }], metadata: { ...extra },
    });
    // Positives: the moment before Claude Code's observer note reached this session.
    for (const f of forwarded.filter((x) => basename(x.file, ".jsonl") === session)) {
      const end = turns.findLastIndex((t) => t.at < f.ts);
      if (end < 0) continue;
      const from = Math.max(-1, turns.slice(0, end + 1).reduce((k, t, i) => (t.msg.role === "assistant" ? [...k, i] : k), [] as number[]).at(-REVIEW_EVERY - 1) ?? -1);
      samples.push(sample(`${session.slice(0, 8)}-note${f.n}`, end, from, { ...meta("incumbent-note", end), incumbentNote: f.n, agentVerdict: f.verdict ?? "" }));
    }
    // Checkpoints, sampled without replacement.
    const pool = [...cps];
    for (let k = 0; k < perSession && pool.length; k++) {
      const end = pool.splice(Math.floor(pick() * pool.length), 1)[0]!;
      samples.push(sample(`${session.slice(0, 8)}-cp${end}`, end, prev(end), meta("checkpoint", end)));
    }
  }
  return samples;
}

if (import.meta.main) {
  const args = process.argv.slice(2);
  const flag = (name: string) => {
    const i = args.indexOf(name);
    return i >= 0 ? args.splice(i, 2)[1] : undefined;
  };
  const notes = flag("--notes");
  const perSession = Number(flag("--per-session") ?? 8);
  const seed = Number(flag("--seed") ?? 20261125);
  const [out, ...files] = args;
  if (!out || !files.length) {
    console.error("usage: bun slices.ts <out-dir> <transcript.jsonl>... [--notes forwarded.jsonl] [--per-session N] [--seed S]");
    process.exit(2);
  }
  const forwarded: Forwarded[] = notes ? readFileSync(notes, "utf-8").split(/\r?\n/).filter(Boolean).map((l) => JSON.parse(l)) : [];
  const samples = build(files, forwarded, perSession, seed);
  mkdirSync(out, { recursive: true });
  writeFileSync(join(out, "samples.jsonl"), samples.map((s) => JSON.stringify(s)).join("\n") + "\n");
  const chars = samples.reduce((n, s) => n + s.input.reduce((m, x) => m + x.content.length, 0), 0);
  console.log(`${samples.length} samples (${samples.filter((s) => s.metadata.kind === "incumbent-note").length} at incumbent notes) from ${files.length} transcripts, ~${Math.round(chars / 4 / 1000)}k input tokens, prompt ${PROMPT_VERSION}`);
}
