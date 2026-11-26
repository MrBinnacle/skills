// Hindsight labels: a note was worth the interruption when the rest of the session shows it was
// true, new and consequential. A judge model answers those three factual questions, each with a
// quote; the shipped grounded() check verifies every quote, and a fixed rule makes the label.
//   bun hindsight.ts build <observer-log.json> <samples.jsonl> <files.txt> <out.jsonl>
//   (run out.jsonl through observer_task.py, then)
//   bun hindsight.ts score <judge-log.json> <out.md>
import { readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { grounded, newest, recordOf, serialize } from "../observer";
import { rows, type Log } from "./report";
import { TYPE } from "../state";
import { toTurns, type Sample } from "./slices";

export const HINDSIGHT_VERSION = "hindsight-2026-11-26";
export const FUTURE_TURNS = 40;
export const FUTURE_CHARS = 30_000;

export const JUDGE = `You audit one note that a watcher raised to the person during a coding session with an AI agent. You get what the watcher saw (<before>), the note (<note>), and what happened next in the session (<after>). Answer three factual questions from the record only. Do not judge whether you like the note.

1. true: does the record support what the note claims? Quote the line that settles it.
2. new: at the moment of the note, had neither the person nor the agent already said or acted on this, and did the agent not deal with it on its own in <after> before it could matter? Quote the line that settles it; when the answer is yes because nobody mentions it, quote the line in <before> where the issue arises.
3. consequential: does <after> show the issue mattered — a failure, rework, a revert, a correction by the person, a decision going ahead that the note was about, or the person or agent acting on the note? Quote that line. If <after> shows no effect, answer false.

Quotes must be copied exactly from <before> or <after>; use "…" only to join two exact pieces. Answer with this JSON object only:
{"true": {"answer": bool, "quote": str}, "new": {"answer": bool, "quote": str}, "consequential": {"answer": bool, "quote": str}}`;

type Item = { id: string; meta: Record<string, unknown>; note: string; before: string; after: string };

const fileFor = (files: string[], session: string) => files.find((f) => basename(f.replace(/\\/g, "/"), ".jsonl") === session);

/** Turns after the moment the watcher looked; for an incumbent note, skip the note and the agent's reply to it. */
export function afterOf(jsonl: string, at: string, skipNote: boolean): { note: string; after: string } {
  const turns = toTurns(jsonl);
  let i = turns.findLastIndex((t) => t.at <= at) + 1;
  let note = "";
  if (skipNote) {
    const k = turns.findIndex((t, j) => j >= i && t.msg.role === "custom" && t.msg.customType === TYPE);
    if (k >= 0) {
      note = String((turns[k]!.msg as { content: unknown }).content);
      i = k + 1;
      if (turns[i]?.msg.role === "assistant") i++; // the agent's verdict on the note would leak the label
    }
  }
  const msgs = turns.slice(i, i + FUTURE_TURNS).map((t) => t.msg);
  return { note, after: serialize(msgs, TYPE).slice(0, FUTURE_CHARS) };
}

export function items(log: Log, samples: Sample[], files: string[]): Item[] {
  const byId = new Map(samples.map((s) => [s.id, s]));
  const out: Item[] = [];
  for (const r of rows(log)) {
    const s = byId.get(r.id);
    const file = fileFor(files, String(r.meta.session));
    if (!s || !file) continue;
    const jsonl = readFileSync(file, "utf-8");
    const before = newest(recordOf(s.input[1]!.content), 24_000);
    const at = String(r.meta.at);
    if (r.reply.kind === "note" && r.grounded) {
      const { after } = afterOf(jsonl, at, false);
      out.push({ id: r.id, meta: { ...r.meta, source: "observer" }, note: `${r.reply.line}\n${r.reply.details}\nEvidence: ${r.reply.evidence}`, before, after });
    }
    if (r.meta.kind === "incumbent-note") {
      const { note, after } = afterOf(jsonl, at, true);
      if (note) out.push({ id: `${r.id}-incumbent`, meta: { ...r.meta, source: "incumbent" }, note, before, after });
    }
  }
  return out;
}

export const judgeSample = (it: Item): Sample => ({
  id: it.id,
  input: [{ role: "system", content: JUDGE }, { role: "user", content: `<before>\n${it.before}\n</before>\n\n<note>\n${it.note}\n</note>\n\n<after>\n${it.after}\n</after>` }],
  metadata: { ...(it.meta as Record<string, string>), judge: HINDSIGHT_VERSION },
});

export type Verdict = { worth: boolean; true: boolean; new: boolean; consequential: boolean; why: string };

/** The fixed rule: each answer counts only when its quote is in the record; worth needs all three. */
export function verdict(reply: string, shown: string): Verdict | undefined {
  let o: any;
  try {
    o = JSON.parse(reply.slice(reply.indexOf("{"), reply.lastIndexOf("}") + 1));
  } catch {
    return undefined;
  }
  const record = shown.replace(/<note>[\s\S]*?<\/note>/, "");
  const ok = (k: string) => o?.[k]?.answer === true && typeof o[k].quote === "string" && grounded(o[k].quote, record);
  const v = { true: ok("true"), new: ok("new"), consequential: ok("consequential") };
  const why = (["true", "new", "consequential"] as const).find((k) => !v[k]);
  return { ...v, worth: !why, why: why ? `not ${why}: ${o?.[why]?.quote ?? ""}` : String(o.consequential.quote) };
}

/** The main agent's own verdict on an incumbent note, as the same three-part label. */
export const agentWorth = (v: string) => v.startsWith("right, new to the agent");

if (import.meta.main) {
  const [cmd, ...a] = process.argv.slice(2);
  if (cmd === "build") {
    const [logPath, samplesPath, filesPath, out] = a as [string, string, string, string];
    const log = JSON.parse(readFileSync(logPath, "utf-8")) as Log;
    const samples = readFileSync(samplesPath, "utf-8").split("\n").filter(Boolean).map((l) => JSON.parse(l) as Sample);
    const files = readFileSync(filesPath, "utf-8").split(/\r?\n/).filter(Boolean);
    const its = items(log, samples, files);
    writeFileSync(out, its.map((i) => JSON.stringify(judgeSample(i))).join("\n") + "\n");
    console.log(`${its.length} items (${its.filter((i) => i.meta.source === "incumbent").length} incumbent)`);
  } else if (cmd === "score") {
    const [logPath, out] = a as [string, string];
    const log = JSON.parse(readFileSync(logPath, "utf-8")) as any;
    const lines: string[] = [`# Hindsight labels (${HINDSIGHT_VERSION})`, ""];
    const res = log.samples.map((s: any) => ({ s, v: verdict(s.output?.completion ?? "", s.input.find((m: any) => m.role === "user")?.content ?? "") }));
    const obs = res.filter((r: any) => r.s.metadata.source === "observer");
    const inc = res.filter((r: any) => r.s.metadata.source === "incumbent");
    const agree = inc.filter((r: any) => r.v && r.v.worth === agentWorth(String(r.s.metadata.agentVerdict))).length;
    lines.push(`Observer notes worth it: ${obs.filter((r: any) => r.v?.worth).length} of ${obs.length} (unreadable ${obs.filter((r: any) => !r.v).length}).`,
      `Judge agrees with the main agent's verdict on incumbent notes: ${agree} of ${inc.length}.`, "");
    for (const { s, v } of res) lines.push(`- ${s.id} [${s.metadata.split}, ${s.metadata.source}${s.metadata.agentVerdict ? `, agent: ${s.metadata.agentVerdict}` : ""}] **${v ? (v.worth ? "worth it" : "not worth it") : "unreadable"}** — ${v?.why ?? ""}`);
    writeFileSync(out, lines.join("\n") + "\n");
    console.log(lines.slice(2, 4).join("\n"));
  }
}
