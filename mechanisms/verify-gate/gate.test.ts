import { describe, expect, test } from "bun:test";
import { createGate, underRoot } from "./gate";

const CHECKS = ["\\bbun test\\b", "\\bpytest\\b"];

describe("verification gate", () => {
  test("an edit with no check after it gets one nudge naming the file", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("edit", { path: "src/a.ts" }, false);
    const nudge = gate.beforeSettle("completed");
    expect(nudge).toBeDefined();
    expect(nudge).toContain("src/a.ts");
  });

  test("an edit followed by a matching check command stays quiet", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("write", { path: "src/a.ts" }, false);
    gate.toolFinished("bash", { command: "cd pkg && bun test src" }, false);
    expect(gate.beforeSettle("completed")).toBeUndefined();
  });

  test("at most one nudge per run, even if the agent ignores it; a new run may nudge again", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("edit", { path: "a.ts" }, false);
    expect(gate.beforeSettle("completed")).toBeDefined();
    // The continuation runs; the agent edits again without checking.
    gate.toolFinished("edit", { path: "a.ts" }, false);
    expect(gate.beforeSettle("completed")).toBeUndefined();

    gate.runStarted();
    gate.toolFinished("edit", { path: "b.ts" }, false);
    expect(gate.beforeSettle("completed")).toBeDefined();
  });

  test("a failed edit changed nothing, so it does not trip the gate", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("edit", { path: "a.ts" }, true);
    expect(gate.beforeSettle("completed")).toBeUndefined();
  });

  test("an aborted or failed run is never continued", () => {
    for (const outcome of ["aborted", "error"] as const) {
      const gate = createGate(CHECKS);
      gate.runStarted();
      gate.toolFinished("edit", { path: "a.ts" }, false);
      expect(gate.beforeSettle(outcome)).toBeUndefined();
    }
  });

  test("a shell command that is not a check does not clear the gate", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("edit", { path: "a.ts" }, false);
    gate.toolFinished("bash", { command: "git status" }, false);
    expect(gate.beforeSettle("completed")).toBeDefined();
  });

  test("a check run through the powershell tool clears the gate like one through bash", () => {
    const gate = createGate(CHECKS);
    gate.runStarted();
    gate.toolFinished("edit", { path: "a.ts" }, false);
    gate.toolFinished("powershell", { command: "bun test" }, false);
    expect(gate.beforeSettle("completed")).toBeUndefined();
  });

  test("a file outside the project root is not tracked; one inside it, by any spelling, is", () => {
    const root = "C:/work/repo";
    const gate = createGate(CHECKS, root);
    gate.runStarted();
    gate.toolFinished("write", { path: "C:/Users/me/.pi/handoffs/note.md" }, false);
    gate.toolFinished("write", { path: "C:/work/repo-other/x.ts" }, false);
    expect(gate.beforeSettle("completed")).toBeUndefined();

    gate.runStarted();
    gate.toolFinished("edit", { path: "src/a.ts" }, false);
    gate.toolFinished("edit", { path: "C:/work/repo/src/b.ts" }, false);
    gate.toolFinished("edit", { path: "C:\\work\\repo\\src\\c.ts" }, false);
    const nudge = gate.beforeSettle("completed");
    expect(nudge).toContain("src/a.ts");
    expect(nudge).toContain("src/b.ts");
    expect(nudge).toContain("c.ts");
  });

  test("underRoot treats the root itself and its children as inside, siblings and parents as outside", () => {
    expect(underRoot("/r/p", "/r/p")).toBe(true);
    expect(underRoot("/r/p", "/r/p/a")).toBe(true);
    expect(underRoot("/r/p", "a/b")).toBe(true);
    expect(underRoot("/r/p", "/r/p2/a")).toBe(false);
    expect(underRoot("/r/p", "/r")).toBe(false);
    expect(underRoot("/r/p", "../q")).toBe(false);
  });
});
