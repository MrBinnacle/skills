import { afterAll, describe, expect, test } from "bun:test";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import extension from "./index";

type Handler = (...args: any[]) => any;

const roots: string[] = [];
afterAll(() => {
  for (const root of roots) rmSync(root, { recursive: true, force: true });
});

function projectCountingEvilAsCheck(config = JSON.stringify({ checkCommands: ["\\bevil\\b"] })): string {
  const root = mkdtempSync(join(tmpdir(), "verify-gate-adapter-"));
  roots.push(root);
  mkdirSync(join(root, ".pi"));
  writeFileSync(join(root, ".pi", "engineering-env.json"), config);
  writeFileSync(join(root, ".pi", "settings.json"), "{}");
  return root;
}

async function settleAfterWriteThenEvil(trusted: boolean, config?: string) {
  const events = new Map<string, Handler>();
  extension({ on: (event: string, handler: Handler) => events.set(event, handler) } as any);
  const notes: string[] = [];
  const levels: string[] = [];
  const notify = (m: string, level: string) => (notes.push(m), levels.push(level));
  const ctx = { cwd: projectCountingEvilAsCheck(config), hasUI: true, isProjectTrusted: () => trusted, ui: { notify } };
  await events.get("session_start")!({}, ctx);
  await events.get("before_agent_start")!();
  await events.get("tool_result")!({ toolName: "write", input: { path: "a.ts" }, isError: false });
  await events.get("tool_result")!({ toolName: "bash", input: { command: "evil" }, isError: false });
  const result = await events.get("agent_before_settle")!({ outcome: "completed", entries: [] });
  return { nudged: result !== undefined, notes, levels };
}

describe("verify-gate adapter", () => {
  test("a trusted project's checkCommands count as checks", async () => {
    expect(await settleAfterWriteThenEvil(true)).toEqual({ nudged: false, notes: [], levels: [] });
  });

  test("an untrusted project's checkCommands are ignored: the defaults apply and the user is warned", async () => {
    const { nudged, notes, levels } = await settleAfterWriteThenEvil(false);
    expect(nudged).toBe(true);
    expect(notes).toHaveLength(1);
    expect(notes[0]).toContain("Pi does not trust this project");
    expect(levels).toEqual(["warning"]);
  });

  test("a trusted project's malformed config disables the gate with an error", async () => {
    const { nudged, notes, levels } = await settleAfterWriteThenEvil(true, "{not json");
    expect(nudged).toBe(false);
    expect(notes[0]).toContain("verify-gate disabled");
    expect(levels).toEqual(["error"]);
  });
});
