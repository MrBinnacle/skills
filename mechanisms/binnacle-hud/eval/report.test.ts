import { expect, test } from "bun:test";
import { rows, sheet } from "./report";

const sample = (id: string, kind: string, completion: string, extra = {}) => ({
  id, metadata: { kind, split: "dev", at: "t", prompt: "observer-x", ...extra },
  input: [{ role: "system", content: "S" }, { role: "user", content: "[Agent]: I merged PR #696 without the full suite." }],
  output: { completion },
});
const note = (evidence: string) => JSON.stringify({ tag: "heads-up", note: "PR #696 merged untested.", details: "**T**", evidence, agentKnows: false });
const log = {
  eval: { model: "anthropic/m" },
  samples: [
    sample("a", "checkpoint", note("merged PR #696 without the full suite")),
    sample("b", "checkpoint", note("deleted the production database")),
    sample("c", "checkpoint", '{"note": null}'),
    sample("d", "incumbent-note", '{"note": null}', { incumbentNote: 44, agentVerdict: "right, new" }),
    { ...sample("e", "checkpoint", ""), error: "rate limit" },
  ],
};

test("rows apply the shipped parser and the grounding check", () => {
  expect(rows(log).map((r) => [r.id, r.reply.kind, r.grounded, r.error])).toEqual([
    ["a", "note", true, false], ["b", "note", false, false], ["c", "none", false, false], ["d", "none", false, false], ["e", "bad", false, true],
  ]);
});

test("the sheet lists kept notes and every incumbent moment, and counts the rest", () => {
  const s = sheet(log);
  expect(s).toContain("Notes kept 1. At incumbent notes 0 of 1; at checkpoints 1 of 4.");
  expect(s).toContain("Dropped: 1 ungrounded, 1 unreadable (1 errors).");
  expect(s).toContain("## a (dev, checkpoint, t)");
  expect(s).toContain("## d (dev, incumbent-note, t)\n- Incumbent note #44; main agent's verdict: right, new\n- Ours: silent");
  expect(s).not.toContain("## b ");
  expect(s).not.toContain("## c ");
});
