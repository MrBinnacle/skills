import { describe, expect } from "bun:test";
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { git, GIT_TIMEOUT, makeRepo, nodeExec, test } from "../session-packet/testkit";
import extension from "./index";

type Handler = (...args: any[]) => any;

function fakePi(exec: Handler = nodeExec) {
  const events = new Map<string, Handler>();
  extension({ on: (event: string, handler: Handler) => events.set(event, handler), exec } as any);
  return events;
}

const ctxFor = (cwd: string) => ({ cwd, hasUI: false });
const edit = (path: string) => ({ toolName: "edit", input: { path }, isError: false, content: [] });

describe("eol-guard adapter", () => {
  test("under core.autocrlf=true an untouched CRLF checkout is not a conversion; under false it is", async () => {
    const { root } = await makeRepo();
    // Commit a.md as LF (makeRepo sets autocrlf=false), then hold it CRLF in the working tree, as an
    // autocrlf checkout does. makeRepo's README.md has no line ending at all, so it cannot serve.
    writeFileSync(join(root, "a.md"), "one\ntwo\n");
    await git(root, "add", "a.md");
    await git(root, "commit", "-q", "-m", "lf");
    writeFileSync(join(root, "a.md"), "one\r\ntwo\r\n");
    await git(root, "config", "core.autocrlf", "true");
    const events = fakePi();
    await events.get("session_start")!({}, ctxFor(root));
    await events.get("before_agent_start")!({}, ctxFor(root));
    expect(await events.get("tool_result")!(edit("a.md"), ctxFor(root))).toBeUndefined();

    await git(root, "config", "core.autocrlf", "false");
    await events.get("session_start")!({}, ctxFor(root));
    await events.get("before_agent_start")!({}, ctxFor(root));
    const result = await events.get("tool_result")!(edit("a.md"), ctxFor(root));
    expect(result?.content.at(-1)?.text).toContain("a.md was LF-only (2 lines) at HEAD and is now CRLF-only");
  }, GIT_TIMEOUT);

  test.each([
    ["the same text", "one\ntwo\nthree\n"],
    ["one line changed", "one\nTWO\nthree\n"],
  ])("under core.autocrlf=true an LF write of %s over a CRLF checkout is not reported, because git stores LF", async (_, text) => {
    const { root } = await makeRepo();
    writeFileSync(join(root, "a.md"), "one\ntwo\nthree\n");
    await git(root, "add", "a.md");
    await git(root, "commit", "-q", "-m", "lf");
    await git(root, "config", "core.autocrlf", "true");
    writeFileSync(join(root, "a.md"), "one\r\ntwo\r\nthree\r\n");
    await git(root, "add", "a.md");
    const events = fakePi();
    await events.get("session_start")!({}, ctxFor(root));
    await events.get("before_agent_start")!({}, ctxFor(root));
    writeFileSync(join(root, "a.md"), text);
    const write = { toolName: "write", input: { path: "a.md" }, isError: false, content: [] };
    expect(await events.get("tool_result")!(write, ctxFor(root))).toBeUndefined();
  }, GIT_TIMEOUT);

  test("when git cannot diff the file the guard reports the conversion rather than stay quiet", async () => {
    const { root } = await makeRepo();
    writeFileSync(join(root, "a.md"), "one\ntwo\n");
    await git(root, "add", "a.md");
    await git(root, "commit", "-q", "-m", "lf");
    writeFileSync(join(root, "a.md"), "one\r\ntwo\r\n");
    const numstatFails: Handler = (command: string, args: string[], options: unknown) =>
      args.includes("--numstat") ? Promise.resolve({ stdout: "", stderr: "fatal", code: 128, killed: false }) : nodeExec(command, args, options);
    const events = fakePi(numstatFails);
    await events.get("session_start")!({}, ctxFor(root));
    await events.get("before_agent_start")!({}, ctxFor(root));
    const result = await events.get("tool_result")!(edit("a.md"), ctxFor(root));
    expect(result?.content.at(-1)?.text).toContain("a.md was LF-only (2 lines) at HEAD and is now CRLF-only");
  }, GIT_TIMEOUT);

  test("under core.autocrlf=false a conversion that also changes one line is still reported", async () => {
    const { root } = await makeRepo();
    writeFileSync(join(root, "a.md"), "one\ntwo\nthree\n");
    await git(root, "add", "a.md");
    await git(root, "commit", "-q", "-m", "lf");
    const events = fakePi();
    await events.get("session_start")!({}, ctxFor(root));
    await events.get("before_agent_start")!({}, ctxFor(root));
    writeFileSync(join(root, "a.md"), "one\r\nTWO\r\nthree\r\n");
    const result = await events.get("tool_result")!(edit("a.md"), ctxFor(root));
    expect(result?.content.at(-1)?.text).toContain("a.md was LF-only (3 lines) at HEAD and is now CRLF-only");
  }, GIT_TIMEOUT);
});
