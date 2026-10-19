import { realpathSync } from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fusionReceipt } from "./fusion";

export type RunOutcome = "completed" | "aborted" | "error";

export interface Gate {
  /** A user prompt started a run. Continuations the gate requested are part of the same run. */
  runStarted(): void;
  toolFinished(toolName: string, input: Record<string, unknown>, isError: boolean, details?: unknown): void;
  /** The continuation prompt to send, or undefined to let the run settle. */
  beforeSettle(outcome: RunOutcome): string | undefined;
}

function textuallyUnder(root: string, path: string): boolean {
  const rel = relative(root, path);
  return rel !== "" ? !rel.startsWith("..") && !isAbsolute(rel) : true;
}

function realSpelling(path: string): string {
  try {
    return realpathSync.native(path);
  } catch {
    const parent = dirname(path);
    return parent === path ? path : join(realSpelling(parent), basename(path));
  }
}

/**
 * True when `path` (absolute or relative to `root`) lies under `root`, compared both as
 * written and by real spelling. Windows spells one directory as a long name or an 8.3 short
 * name, so a cwd and a tool's path can disagree as text.
 */
export function underRoot(root: string, path: string): boolean {
  const base = resolve(root);
  const target = resolve(root, path);
  return textuallyUnder(base, target) || textuallyUnder(realSpelling(base), realSpelling(target));
}

/**
 * Tracks files the `edit` and `write` tools changed since the last check command in the
 * current run. Only those two tools are observed: a file changed by a shell command is not
 * seen. A file outside `projectRoot` is not tracked either: a project's check cannot cover a
 * file the project does not contain. Measured 2026-10-10 over the first day's sessions, 7 of
 * 8 nudges named files under the operator's handoff directory, outside every repository.
 */
export function createGate(checkCommands: readonly string[], projectRoot?: string): Gate {
  const patterns = checkCommands.map((p) => new RegExp(p));
  const unchecked = new Set<string>();
  let nudged = false;

  return {
    runStarted() {
      unchecked.clear();
      nudged = false;
    },
    toolFinished(toolName, input, isError, details) {
      const receipt = toolName === "edit" || toolName === "write" ? fusionReceipt(details) : undefined;
      if ((toolName === "edit" || toolName === "write") && (!isError || receipt)) {
        const path = String(input.path);
        if (projectRoot === undefined || underRoot(projectRoot, path)) unchecked.add(path);
      }
      // Nested Bash was observed before the parent mutation result. Replay only
      // a successful follow-up after recording that mutation; failures stay pending.
      if (receipt?.followUp.status === "succeeded" &&
          patterns.some((p) => p.test(receipt.followUp.command))) unchecked.clear();
      if ((toolName === "bash" || toolName === "powershell") && patterns.some((p) => p.test(String(input.command)))) {
        unchecked.clear();
      }
    },
    beforeSettle(outcome) {
      if (outcome !== "completed" || unchecked.size === 0 || nudged) return undefined;
      nudged = true;
      return [
        `Verification gate: these files changed after the last check command in this run: ${[...unchecked].join(", ")}.`,
        "Run the project's test or check command now and report the result.",
        "If no check applies to this change, say so in one sentence and why.",
      ].join(" ");
    },
  };
}
