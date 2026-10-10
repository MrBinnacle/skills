/**
 * Detects a uniform line-ending conversion: a tracked file that was LF-only at HEAD and is now
 * CRLF-only, or the reverse. The mixed-endings predicate a typical guard uses (`crlf > 0 &&
 * lf > 0`) is blind to exactly this case, and the case is the one where the diff damage is
 * total (`uniform-eol/guard-design.md`). No Pi imports: file and git reads are injected so the
 * tests run on bytes.
 */

export interface EolCount {
  crlf: number;
  lf: number;
}

export type EolKind = "crlf" | "lf" | "mixed" | "none";

export function countEol(bytes: Uint8Array): EolCount {
  let crlf = 0;
  let lf = 0;
  for (let i = 0; i < bytes.length; i++) {
    if (bytes[i] === 0x0a) {
      if (i > 0 && bytes[i - 1] === 0x0d) crlf++;
      else lf++;
    }
  }
  return { crlf, lf };
}

export function kindOf(count: EolCount): EolKind {
  if (count.crlf === 0 && count.lf === 0) return "none";
  if (count.lf === 0) return "crlf";
  if (count.crlf === 0) return "lf";
  return "mixed";
}

/** True when `before` and `after` are each uniform and of opposite kinds. */
export function isUniformConversion(before: EolCount, after: EolCount): boolean {
  const b = kindOf(before);
  const a = kindOf(after);
  return (b === "lf" && a === "crlf") || (b === "crlf" && a === "lf");
}

export interface EolGuardDeps {
  /** Bytes of the working file, or undefined when it does not exist. */
  readWorking(relPath: string): Promise<Uint8Array | undefined>;
  /** Bytes of the file at HEAD, or undefined when HEAD does not hold it. */
  readHead(relPath: string): Promise<Uint8Array | undefined>;
  /** Tracked files that differ from HEAD, as repository-relative POSIX paths. */
  changedFiles(): Promise<string[]>;
  /** Repository-relative POSIX path for a tool-call path, or undefined when outside the repo. */
  toRepoPath(path: string): string | undefined;
}

export interface EolGuard {
  runStarted(): void;
  /** A note to append to the tool result, or undefined when nothing was converted. */
  toolFinished(toolName: string, input: Record<string, unknown>, isError: boolean): Promise<string | undefined>;
}

/** Shell-ish tools after which any tracked file may have changed. */
const SHELL_TOOLS: ReadonlySet<string> = new Set(["bash", "powershell"]);
const FILE_TOOLS: ReadonlySet<string> = new Set(["edit", "write"]);
/** Beyond this, a shell command touched too many files for a per-file byte read to stay cheap. */
const MAX_FILES_PER_SHELL_CALL = 200;

export function describe(relPath: string, before: EolCount, after: EolCount): string {
  const label = (c: EolCount) => `${kindOf(c).toUpperCase()}-only (${c.crlf + c.lf} lines)`;
  return [
    `EOL guard: ${relPath} was ${label(before)} at HEAD and is now ${label(after)}.`,
    "Every line of it will show as changed. If a script wrote it, the write translated the line endings",
    "(on Windows, Python's text-mode write does this by default): rewrite the file with its original",
    "endings - write bytes, or open with newline='' - before going on. The diffstat is the only other",
    "place this shows, and only at commit time.",
  ].join(" ");
}

export function createEolGuard(deps: EolGuardDeps): EolGuard {
  const reported = new Set<string>();

  async function check(relPath: string): Promise<string | undefined> {
    if (reported.has(relPath)) return undefined;
    const [head, working] = await Promise.all([deps.readHead(relPath), deps.readWorking(relPath)]);
    if (head === undefined || working === undefined) return undefined;
    const before = countEol(head);
    const after = countEol(working);
    if (!isUniformConversion(before, after)) return undefined;
    reported.add(relPath);
    return describe(relPath, before, after);
  }

  return {
    runStarted() {
      reported.clear();
    },
    async toolFinished(toolName, input, isError) {
      if (isError) return undefined;
      if (FILE_TOOLS.has(toolName)) {
        const rel = deps.toRepoPath(String(input.path));
        return rel === undefined ? undefined : check(rel);
      }
      if (SHELL_TOOLS.has(toolName)) {
        const files = await deps.changedFiles();
        if (files.length === 0 || files.length > MAX_FILES_PER_SHELL_CALL) return undefined;
        const notes: string[] = [];
        for (const f of files) {
          const note = await check(f);
          if (note) notes.push(note);
        }
        return notes.length ? notes.join("\n") : undefined;
      }
      return undefined;
    },
  };
}
