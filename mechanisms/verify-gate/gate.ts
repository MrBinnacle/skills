export type RunOutcome = "completed" | "aborted" | "error";

export interface Gate {
  /** A user prompt started a run. Continuations the gate requested are part of the same run. */
  runStarted(): void;
  toolFinished(toolName: string, input: Record<string, unknown>, isError: boolean): void;
  /** The continuation prompt to send, or undefined to let the run settle. */
  beforeSettle(outcome: RunOutcome): string | undefined;
}

/**
 * Tracks files the `edit` and `write` tools changed since the last check command in the
 * current run. Only those two tools are observed: a file changed by a shell command is not
 * seen.
 */
export function createGate(checkCommands: readonly string[]): Gate {
  const patterns = checkCommands.map((p) => new RegExp(p));
  const unchecked = new Set<string>();
  let nudged = false;

  return {
    runStarted() {
      unchecked.clear();
      nudged = false;
    },
    toolFinished(toolName, input, isError) {
      if ((toolName === "edit" || toolName === "write") && !isError) unchecked.add(String(input.path));
      if (toolName === "bash" && patterns.some((p) => p.test(String(input.command)))) unchecked.clear();
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
