// Reads an Inspect JSON eval log of observer_task.py, applies the shipped parseReply and grounded
// checks, and writes a labelling sheet: one block per note the observer raised, with the
// incumbent's note and the main agent's verdict beside it where the sample has them.
//
//   bun mechanisms/binnacle-hud/eval/report.ts <log.json> <labels.md>
import { readFileSync, writeFileSync } from "node:fs";
import { grounded, parseReply, recordOf, type Reply } from "../observer";

type LogSample = {
  id: string;
  metadata: Record<string, unknown>;
  input: Array<{ role: string; content: unknown }> | string;
  output?: { completion?: string };
  error?: unknown;
};
type Log = { eval?: { model?: string; task?: string }; stats?: { model_usage?: Record<string, { input_tokens?: number; output_tokens?: number }> }; samples?: LogSample[] };

const text = (c: unknown) => (typeof c === "string" ? c : Array.isArray(c) ? c.map((b) => (b as { text?: string }).text ?? "").join("") : "");

export type Row = { id: string; meta: Record<string, unknown>; reply: Reply; grounded: boolean; error: boolean };

export function rows(log: Log): Row[] {
  return (log.samples ?? []).map((s) => {
    const shown = Array.isArray(s.input) ? text(s.input.find((m) => m.role === "user")?.content) : s.input;
    const reply = s.error ? ({ kind: "bad", why: "sample error" } as Reply) : parseReply(s.output?.completion ?? "");
    return { id: s.id, meta: s.metadata, reply, grounded: reply.kind === "note" && grounded(reply.evidence, recordOf(shown)), error: !!s.error };
  });
}

export function sheet(log: Log): string {
  const all = rows(log);
  const by = (kind: string) => all.filter((r) => r.meta.kind === kind);
  const fired = (rs: Row[]) => rs.filter((r) => r.reply.kind === "note" && r.grounded).length;
  const usage = Object.entries(log.stats?.model_usage ?? {}).map(([m, u]) => `${m}: ${u.input_tokens ?? 0} in, ${u.output_tokens ?? 0} out`).join("; ");
  const head = [
    `# Observer labels: ${log.eval?.model ?? "?"}, prompt ${String(all[0]?.meta.prompt ?? "?")}`,
    "",
    `Samples ${all.length}. Notes kept ${fired(all)}. At incumbent notes ${fired(by("incumbent-note"))} of ${by("incumbent-note").length}; at checkpoints ${fired(by("checkpoint"))} of ${by("checkpoint").length}.`,
    `Dropped: ${all.filter((r) => r.reply.kind === "note" && !r.grounded).length} ungrounded, ${all.filter((r) => r.reply.kind === "bad").length} unreadable (${all.filter((r) => r.error).length} errors). Usage: ${usage || "not recorded"}.`,
    "",
    "Label each note: **worth the interruption?** yes / no, and one line of why. Use the dev split to learn; leave test for the final comparison.",
    "",
  ];
  const blocks = all.flatMap((r) => {
    if (r.meta.kind !== "incumbent-note" && !(r.reply.kind === "note" && r.grounded)) return [];
    const m = r.meta;
    const lines = [`## ${r.id} (${m.split}, ${m.kind}, ${m.at})`];
    if (m.kind === "incumbent-note") lines.push(`- Incumbent note #${m.incumbentNote}; main agent's verdict: ${m.agentVerdict || "not recorded"}`);
    if (r.reply.kind === "note") {
      lines.push(`- **${r.reply.tag}** ${r.reply.line}`, `- agentKnows: ${r.reply.agentKnows}${r.grounded ? "" : " (DROPPED: quote not in record)"}`, `- Evidence: \u201c${r.reply.evidence}\u201d`, "", r.reply.details, "");
    } else lines.push(`- Ours: ${r.reply.kind === "none" ? "silent" : `unreadable (${r.reply.why})`}`);
    lines.push("- Worth it: ", "- Why: ", "");
    return lines;
  });
  return [...head, ...blocks].join("\n");
}

if (import.meta.main) {
  const [logPath, out] = process.argv.slice(2);
  if (!logPath || !out) {
    console.error("usage: bun report.ts <log.json> <labels.md>");
    process.exit(2);
  }
  const s = sheet(JSON.parse(readFileSync(logPath, "utf-8")) as Log);
  writeFileSync(out, s);
  console.log(s.split("\n").slice(0, 4).join("\n"));
}
