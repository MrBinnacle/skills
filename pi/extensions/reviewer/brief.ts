export const DEFAULT_MAX_DIFF_CHARS = 400_000;

export interface BriefInput {
  task: string;
  base: string;
  head: string;
  diff: string;
  untracked: readonly string[];
  /** Evidence, measurements, or prior advice the caller wants the reviewer to see, verbatim. */
  context?: string;
  maxDiffChars?: number;
}

/** The reviewer's system prompt: its role, tools, and output contract. */
export const REVIEWER_SYSTEM_PROMPT = `You are a code reviewer in a fresh context. You did not write this change.

Tools: read, grep, find, ls. They are read-only; you cannot run commands or edit files.

Find defects the change introduces or fails to handle relative to its task: wrong behavior, missed cases, broken callers, tests that cannot fail, unsafe operations. Verify each finding by reading the code; quote the exact line in "evidence". Do not report style preferences as defects.

Finish by calling submit_review exactly once. A review that does not call submit_review is lost. Report "filesRead" honestly: list only files you actually opened. If you could not do the review properly (missing context, unreadable files), say so with status "degraded" or "blocked" and a reason instead of guessing.`;

/** The first user message: the six things a reviewer needs, so the brief does not decide the answer. */
export function buildBrief(input: BriefInput): string {
  const cap = input.maxDiffChars ?? DEFAULT_MAX_DIFF_CHARS;
  const cut = input.diff.length > cap;
  const diff = cut ? input.diff.slice(0, cap) : input.diff;

  const sections = [
    "## Decision and authority",
    "Decide what in this change should be fixed before it lands. You may recommend; you may not change the task's scope or edit files. Recommend a scope change as a finding with disposition \"needs-decision\". Constraints in the task are revisable if you can show they are wrong.",
    "",
    "## Task, verbatim",
    input.task,
    "",
    "## Operating environment",
    `Your working directory is the repository root. The change is the working tree against ${input.base} (HEAD ${input.head}). Read any file you need, including callers and tests the diff does not show.`,
  ];
  if (input.untracked.length) {
    sections.push(`Untracked new files (not in the diff below; read them): ${input.untracked.join(", ")}`);
  }
  if (input.context) {
    sections.push("", "## Caller context, verbatim", input.context);
  }
  sections.push("", "## The change", "```diff", diff, "```");
  if (cut) {
    sections.push(
      `Diff truncated: showing the first ${cap} of ${input.diff.length} characters; ${input.diff.length - cap} characters were cut. Read the changed files directly for the rest.`,
    );
  }
  sections.push(
    "",
    "## Close",
    "Call submit_review with every finding, the files you read, and your status.",
  );
  return sections.join("\n");
}
