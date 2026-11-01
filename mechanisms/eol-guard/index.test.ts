import { describe, expect, test } from "bun:test";
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { git, GIT_TIMEOUT, makeRepo, nodeExec } from "../session-packet/testkit";
import extension from "./index";

type Handler = (...args: any[]) => any;

function fakePi() {
  const events = new Map<string, Handler>();
  extension({ on: (event: string, handler: Handler) => events.set(event, handler), exec: nodeExec } as any);
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
});
