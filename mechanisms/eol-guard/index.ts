import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { readFile } from "node:fs/promises";
import { isAbsolute, join, relative, resolve, sep } from "node:path";
import { createEolGuard, type EolGuard } from "./eol";

function report(ctx: ExtensionContext, message: string): void {
  if (ctx.hasUI) ctx.ui.notify(message, "warning");
  else console.error(message);
}

/**
 * Appends a note to a `write`, `edit`, `bash` or `powershell` result when a tracked file under the
 * session's repository went from one uniform line ending to the other. Reads go through
 * `pi.exec("git", ...)`; a session outside a git repository disables the guard and says so once.
 */
export default function (pi: ExtensionAPI) {
  let guard: EolGuard | undefined;

  pi.on("session_start", async (_event, ctx) => {
    const top = await pi.exec("git", ["rev-parse", "--show-toplevel"], { cwd: ctx.cwd });
    if (top.code !== 0) {
      guard = undefined;
      report(ctx, "eol-guard disabled: not inside a git repository");
      return;
    }
    const root = resolve(top.stdout.trim());
    const posix = (p: string) => p.split(sep).join("/");

    guard = createEolGuard({
      async readWorking(rel) {
        try {
          return new Uint8Array(await readFile(join(root, rel)));
        } catch {
          return undefined;
        }
      },
      async readHead(rel) {
        const r = await pi.exec("git", ["show", `HEAD:${rel}`], { cwd: root });
        // stdout is decoded text; `\r` survives decoding, which is all the count needs.
        return r.code === 0 ? new TextEncoder().encode(r.stdout) : undefined;
      },
      async changedFiles() {
        const r = await pi.exec("git", ["-c", "core.quotePath=false", "diff", "--name-only", "HEAD"], { cwd: root });
        return r.code === 0 ? r.stdout.split(/\r?\n/).filter((l) => l.length > 0) : [];
      },
      toRepoPath(path) {
        const rel = relative(root, resolve(ctx.cwd, path));
        if (rel === "" || rel.startsWith("..") || isAbsolute(rel)) return undefined;
        return posix(rel);
      },
    });
  });

  pi.on("before_agent_start", async () => {
    guard?.runStarted();
  });

  pi.on("tool_result", async (event) => {
    const note = await guard?.toolFinished(event.toolName, event.input, event.isError);
    if (!note) return undefined;
    return {
      content: [...event.content, { type: "text", text: `\n${note}` }],
      structuredContent: event.structuredContent,
    };
  });
}
