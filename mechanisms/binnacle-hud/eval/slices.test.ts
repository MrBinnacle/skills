import { expect, test } from "bun:test";
import { REVIEW_EVERY, SETTLE_MIN, SYSTEM } from "../observer";
import { checkpoints, lookAt, toTurns } from "./slices";

const row = (o: object) => JSON.stringify(o);
const user = (content: unknown, extra = {}) => row({ type: "user", timestamp: "t", message: { role: "user", content }, ...extra });
const asst = (id: string, content: unknown[]) => row({ type: "assistant", timestamp: "t", message: { id, role: "assistant", content } });

const jsonl = [
  user("fix the login bug"),
  asst("a1", [{ type: "thinking", thinking: "SECRET" }]),
  asst("a1", [{ type: "text", text: "Looking." }]),
  asst("a1", [{ type: "tool_use", id: "tu1", name: "Bash", input: { command: "npm test" } }]),
  user([{ type: "tool_result", tool_use_id: "tu1", content: "2 failing", is_error: true }]),
  row({ type: "assistant", isSidechain: true, message: { id: "s", content: [{ type: "text", text: "SIDECHAIN" }] } }),
  user("Here is a note offered by a side agent:\n\n> Heads up · The tests never ran on CI.\n\nDetails"),
  user("<command-name>/compact</command-name>"),
  user("<task-notification>\n<status>completed</status>\n</task-notification>"),
  user("This session is being continued…", { isCompactSummary: true }),
  asst("a2", [{ type: "text", text: "Fixed." }]),
].join("\n");

test("toTurns: one assistant message per response, named tool results, carriers and summaries typed", () => {
  const turns = toTurns(jsonl);
  expect(turns.map((t) => t.msg.role)).toEqual(["user", "assistant", "toolResult", "custom", "custom", "custom", "custom", "assistant"]);
  expect(turns.filter((t) => t.human)).toHaveLength(1);
  expect((turns[1]!.msg as { content: unknown[] }).content).toHaveLength(2);
  expect(turns[2]!.msg).toMatchObject({ toolName: "Bash", isError: true });
  expect(turns[6]!.compact).toBe("This session is being continued…");
  expect(JSON.stringify(turns)).not.toContain("SIDECHAIN");
  expect(JSON.stringify(turns)).not.toContain("SECRET");
});

test("lookAt: carriers leave the transcript and enter already-raised; the summary bounds the window", () => {
  const turns = toTurns(jsonl);
  const m = lookAt(turns, turns.length - 1, -1);
  expect(m).toContain("<earlier_summary>\nThis session is being continued…");
  expect(m).toContain("- The tests never ran on CI.");
  expect(m).toContain("[Agent]: Fixed.");
  expect(m).not.toContain("Looking.");
  expect(m).toContain("<request>\nfix the login bug");
  const before = lookAt(turns, 2, -1);
  expect(before).toContain('[Agent tool calls]: Bash({"command":"npm test"})');
  expect(before).not.toContain("Here is a note offered");
});

test("checkpoints: every REVIEW_EVERY assistant turns, and at a hand-back with SETTLE_MIN unseen", () => {
  const a = (n: number) => Array.from({ length: n }, (_, i) => asst(`x${n}-${i}`, [{ type: "text", text: "." }]));
  const long = toTurns([user("go"), ...a(REVIEW_EVERY + SETTLE_MIN), user("next"), ...a(SETTLE_MIN - 1)].join("\n"));
  expect(checkpoints(long)).toEqual([REVIEW_EVERY, REVIEW_EVERY + SETTLE_MIN]);
});

test("samples carry the shipped system prompt", () => expect(SYSTEM).toContain('{"note": null}'));
