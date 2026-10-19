import { describe, expect, test } from "bun:test";
import { countEol, createEolGuard, isUniformConversion, kindOf, type EolGuardDeps } from "./eol";

const enc = (s: string) => new TextEncoder().encode(s);
const LF3 = "a\nb\nc\n";
const CRLF3 = "a\r\nb\r\nc\r\n";

describe("eol counting", () => {
  test("counts CRLF and bare LF separately", () => {
    expect(countEol(enc(LF3))).toEqual({ crlf: 0, lf: 3 });
    expect(countEol(enc(CRLF3))).toEqual({ crlf: 3, lf: 0 });
    expect(countEol(enc("a\r\nb\nc"))).toEqual({ crlf: 1, lf: 1 });
    expect(kindOf(countEol(enc("")))).toBe("none");
    expect(kindOf(countEol(enc("a\r\nb\n")))).toBe("mixed");
  });

  test("a uniform conversion is LF-only to CRLF-only or the reverse; mixed and same-kind are not", () => {
    expect(isUniformConversion(countEol(enc(LF3)), countEol(enc(CRLF3)))).toBe(true);
    expect(isUniformConversion(countEol(enc(CRLF3)), countEol(enc(LF3)))).toBe(true);
    expect(isUniformConversion(countEol(enc(LF3)), countEol(enc(LF3 + "d\n")))).toBe(false);
    // The stray-separator case belongs to a mixed-endings guard, not this one.
    expect(isUniformConversion(countEol(enc(LF3)), countEol(enc("a\r\nb\nc\n")))).toBe(false);
    expect(isUniformConversion(countEol(enc("")), countEol(enc(CRLF3)))).toBe(false);
  });
});

function fakeDeps(head: Record<string, string>, working: Record<string, string>, changed: string[]): EolGuardDeps {
  return {
    readWorking: async (p) => (p in working ? enc(working[p]) : undefined),
    readHead: async (p) => (p in head ? enc(head[p]) : undefined),
    changedFiles: async () => changed,
    toRepoPath: (p) => (p.startsWith("/outside/") ? undefined : p.replace(/^\.\//, "")),
  };
}

describe("eol guard", () => {
  test("a write that converted a tracked LF file to CRLF gets a note naming the file and both counts", async () => {
    const guard = createEolGuard(fakeDeps({ "a.md": LF3 }, { "a.md": CRLF3 }, []));
    guard.runStarted();
    const note = await guard.toolFinished("write", { path: "a.md" }, false);
    expect(note).toContain("a.md");
    expect(note).toContain("LF-only (3 lines) at HEAD");
    expect(note).toContain("CRLF-only (3 lines)");
  });

  test("an edit that kept the endings, or touched an untracked or outside file, stays quiet", async () => {
    const guard = createEolGuard(fakeDeps({ "a.md": LF3 }, { "a.md": LF3 + "d\n", "new.md": CRLF3 }, []));
    guard.runStarted();
    expect(await guard.toolFinished("edit", { path: "a.md" }, false)).toBeUndefined();
    expect(await guard.toolFinished("write", { path: "new.md" }, false)).toBeUndefined();
    expect(await guard.toolFinished("write", { path: "/outside/x.md" }, false)).toBeUndefined();
  });

  test("after a shell command, every changed tracked file is checked and converted ones are listed", async () => {
    const guard = createEolGuard(
      fakeDeps({ "a.py": LF3, "b.py": CRLF3, "c.py": LF3 }, { "a.py": CRLF3, "b.py": LF3, "c.py": LF3 + "x\n" }, ["a.py", "b.py", "c.py"]),
    );
    guard.runStarted();
    const note = await guard.toolFinished("bash", { command: "python fix.py" }, false);
    expect(note).toContain("a.py was LF-only");
    expect(note).toContain("b.py was CRLF-only");
    expect(note).not.toContain("c.py");
    expect(await guard.toolFinished("powershell", { command: "git status" }, false)).toBeUndefined();
  });

  test("a converted file is reported once per run, and again in a new run", async () => {
    const guard = createEolGuard(fakeDeps({ "a.md": LF3 }, { "a.md": CRLF3 }, ["a.md"]));
    guard.runStarted();
    expect(await guard.toolFinished("write", { path: "a.md" }, false)).toBeDefined();
    expect(await guard.toolFinished("bash", { command: "ls" }, false)).toBeUndefined();
    guard.runStarted();
    expect(await guard.toolFinished("bash", { command: "ls" }, false)).toBeDefined();
  });

  test("a failed tool call and a non-file, non-shell tool are ignored", async () => {
    const guard = createEolGuard(fakeDeps({ "a.md": LF3 }, { "a.md": CRLF3 }, ["a.md"]));
    guard.runStarted();
    expect(await guard.toolFinished("write", { path: "a.md" }, true)).toBeUndefined();
    expect(await guard.toolFinished("read", { path: "a.md" }, false)).toBeUndefined();
  });
});
