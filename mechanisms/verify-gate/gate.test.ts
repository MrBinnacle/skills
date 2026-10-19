import { describe, expect, test } from "bun:test";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
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
    // An absolute path is absolute only in the host's own spelling: on POSIX,
    // "C:/work/repo" is relative and resolves inside the root.
    const win = process.platform === "win32";
    const root = win ? "C:/work/repo" : "/work/repo";
    const gate = createGate(CHECKS, root);
    gate.runStarted();
    gate.toolFinished("write", { path: win ? "C:/Users/me/.pi/handoffs/note.md" : "/home/me/.pi/handoffs/note.md" }, false);
    gate.toolFinished("write", { path: win ? "C:/work/repo-other/x.ts" : "/work/repo-other/x.ts" }, false);
    expect(gate.beforeSettle("completed")).toBeUndefined();

    gate.runStarted();
    gate.toolFinished("edit", { path: "src/a.ts" }, false);
    gate.toolFinished("edit", { path: win ? "C:/work/repo/src/b.ts" : "/work/repo/src/b.ts" }, false);
    gate.toolFinished("edit", { path: win ? "C:\\work\\repo\\src\\c.ts" : "/work/repo/src/c.ts" }, false);
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

  const win = process.platform === "win32";

  function shortSpelling(dir: string): string {
    return execFileSync("cmd", ["/d", "/s", "/c", `"for %I in ("${dir}") do @echo %~sI"`], {
      encoding: "utf8",
      windowsVerbatimArguments: true,
    }).trim();
  }

  function withSpellings(body: (long: string, short: string) => void): void {
    const long = realpathSync.native(mkdtempSync(join(tmpdir(), "verify-gate-longname-")));
    try {
      const short = shortSpelling(long);
      expect(short).not.toBe(long);
      body(long, short);
    } finally {
      rmSync(long, { recursive: true, force: true });
    }
  }

  test.skipIf(!win)("underRoot matches a short-name root against a long-name path, and the reverse", () => {
    withSpellings((long, short) => {
      mkdirSync(join(long, "src"));
      writeFileSync(join(long, "src", "a.ts"), "");
      expect(underRoot(short, join(long, "src", "a.ts"))).toBe(true);
      expect(underRoot(long, join(short, "src", "a.ts"))).toBe(true);
      expect(underRoot(short, join(dirname(long), "elsewhere.ts"))).toBe(false);
    });
  });

  test.skipIf(!win)("underRoot matches a short-name root against a long-name file that does not exist yet", () => {
    withSpellings((long, short) => {
      expect(underRoot(short, join(long, "new", "dir", "b.ts"))).toBe(true);
      expect(underRoot(long, join(short, "new", "dir", "b.ts"))).toBe(true);
    });
  });

  test("underRoot still counts a file reached through a link inside the root that points outside it", () => {
    const tmp = mkdtempSync(join(tmpdir(), "verify-gate-link-"));
    try {
      const root = join(tmp, "repo");
      mkdirSync(root);
      mkdirSync(join(tmp, "outside"));
      symlinkSync(join(tmp, "outside"), join(root, "linked"), "junction");
      expect(underRoot(root, join(root, "linked", "x.ts"))).toBe(true);
    } finally {
      rmSync(tmp, { recursive: true, force: true });
    }
  });
});
