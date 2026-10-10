import {
  createAgentSession,
  createExtensionRuntime,
  defineTool,
  type ExtensionAPI,
  type ExtensionContext,
  type ResourceLoader,
  SessionManager,
  SettingsManager,
} from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { buildBrief, REVIEWER_SYSTEM_PROMPT } from "./brief";
import {
  DISPOSITIONS,
  finalizeReview,
  newReviewId,
  renderReview,
  type Review,
  SEVERITIES,
  STATUSES,
  type Submission,
} from "./review";

const REVIEWER_MODEL = { provider: "anthropic", id: "claude-opus-5-5" } as const;
// `tools` is an allowlist that also governs custom tools, so submit_review must be named here.
const REVIEWER_TOOLS = ["read", "grep", "find", "ls", "submit_review"];

const literals = <T extends readonly string[]>(values: T) => Type.Union(values.map((v) => Type.Literal(v)));

const FindingSchema = Type.Object({
  severity: literals(SEVERITIES),
  file: Type.String({ description: "Repository-relative path" }),
  line: Type.Union([Type.Integer({ minimum: 1 }), Type.Null()], { description: "1-based line, or null for a whole-file finding" }),
  evidence: Type.String({ description: "The exact line(s) quoted from the file, or the observed fact" }),
  disposition: literals(DISPOSITIONS),
  reasoning: Type.String({ description: "At most three sentences" }),
  whatWouldChangeIt: Type.String({ description: "The fact that, if different, would change this disposition" }),
});

const SubmissionSchema = Type.Object({
  findings: Type.Array(FindingSchema),
  status: literals(STATUSES),
  statusReason: Type.Optional(Type.String()),
  filesRead: Type.Array(Type.String(), { description: "Only files you actually opened" }),
});

const ReviewSchema = Type.Object({
  reviewId: Type.String(),
  model: Type.String(),
  base: Type.String(),
  head: Type.String(),
  status: literals(STATUSES),
  statusReason: Type.String(),
  filesRead: Type.Array(Type.String()),
  findings: Type.Array(Type.Intersect([Type.Object({ id: Type.String() }), FindingSchema])),
});

function bareResourceLoader(): ResourceLoader {
  return {
    getExtensions: () => ({ extensions: [], errors: [], runtime: createExtensionRuntime() }),
    getSkills: () => ({ skills: [], diagnostics: [] }),
    getPrompts: () => ({ prompts: [], diagnostics: [] }),
    getThemes: () => ({ themes: [], diagnostics: [] }),
    getAgentsFiles: () => ({ agentsFiles: [] }),
    getSystemPrompt: () => REVIEWER_SYSTEM_PROMPT,
    getSystemPromptSource: () => undefined,
    getAppendSystemPrompt: () => [],
    getAppendSystemPromptSources: () => [],
    extendResources: () => {},
    reload: async () => {},
  };
}

function report(ctx: ExtensionContext, message: string): void {
  if (ctx.hasUI) ctx.ui.notify(message, "error");
  else console.error(message);
}

async function git(pi: ExtensionAPI, cwd: string, args: string[]): Promise<string> {
  const result = await pi.exec("git", ["-C", cwd, ...args]);
  if (result.code !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr.trim()}`);
  return result.stdout;
}

interface ReviewRequest {
  task: string;
  base?: string;
  context?: string;
}

async function runReview(
  pi: ExtensionAPI,
  ctx: ExtensionContext,
  request: ReviewRequest,
  signal: AbortSignal | undefined,
): Promise<{ review: Review; cost: number }> {
  const base = request.base?.trim() || "HEAD";
  const root = (await git(pi, ctx.cwd, ["rev-parse", "--show-toplevel"])).trim();
  const head = (await git(pi, root, ["rev-parse", "--short", "HEAD"])).trim();
  const diff = await git(pi, root, ["diff", base]);
  const untracked = (await git(pi, root, ["ls-files", "--others", "--exclude-standard"]))
    .split("\n")
    .filter(Boolean);
  if (!diff.trim() && untracked.length === 0) {
    throw new Error(`Nothing to review: no changes against ${base} and no untracked files.`);
  }

  const model = ctx.modelRegistry.find(REVIEWER_MODEL.provider, REVIEWER_MODEL.id);
  if (!model) throw new Error(`Reviewer model ${REVIEWER_MODEL.provider}/${REVIEWER_MODEL.id} is not available.`);

  let submission: Submission | undefined;
  const submitTool = defineTool({
    name: "submit_review",
    label: "Submit review",
    description: "Submit the complete review. Call exactly once, at the end.",
    parameters: SubmissionSchema,
    async execute(_id, params) {
      submission = params as Submission;
      return { content: [{ type: "text", text: "Review recorded." }], details: undefined, terminate: true };
    },
  });

  const { session } = await createAgentSession({
    cwd: root,
    model,
    thinkingLevel: "high",
    resourceLoader: bareResourceLoader(),
    tools: REVIEWER_TOOLS,
    customTools: [submitTool],
    sessionManager: SessionManager.inMemory(root),
    settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  });
  const onAbort = () => void session.abort();
  signal?.addEventListener("abort", onAbort);
  try {
    await session.prompt(buildBrief({ task: request.task, base, head, diff, untracked, context: request.context }));
    if (!submission && !signal?.aborted) {
      await session.prompt("You have not called submit_review. Call it now with your findings, filesRead and status.");
    }
    const meta = { reviewId: newReviewId(), model: `${model.provider}/${model.id}`, base, head };
    const diagnostics = submission
      ? undefined
      : `Active tools: ${session.getActiveToolNames().join(", ")}. Last reviewer text: ${(session.getLastAssistantText() ?? "(none)").slice(0, 600)}`;
    return { review: finalizeReview(meta, submission, diagnostics), cost: session.getSessionStats().cost };
  } finally {
    signal?.removeEventListener("abort", onAbort);
    session.dispose();
  }
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "review_diff",
    label: "Review diff",
    description:
      "Have a different model review the working-tree change against a git base in a fresh, read-only context. Returns typed findings with collision-free ids.",
    promptSnippet: "review_diff: independent read-only review of the current git change by another model",
    parameters: Type.Object({
      task: Type.String({ description: "The task statement the change is meant to satisfy, verbatim" }),
      base: Type.Optional(Type.String({ description: "Git ref to diff against (default HEAD)" })),
      context: Type.Optional(Type.String({ description: "Evidence or prior advice the reviewer should see, verbatim" })),
    }),
    outputSchema: ReviewSchema,
    async execute(_id, params, signal, _onUpdate, ctx) {
      const { review, cost } = await runReview(pi, ctx, params, signal);
      return {
        content: [{ type: "text", text: `${renderReview(review)}\nreviewer cost: $${cost.toFixed(4)}` }],
        details: review,
        structuredContent: review as unknown as Record<string, unknown>,
      };
    },
  });

  pi.registerCommand("review", {
    description: "Independent review of the working-tree change: /review <task statement>",
    handler: async (args, ctx) => {
      const task = args.trim();
      if (!task) {
        report(ctx, "Usage: /review <task statement the change should satisfy>");
        return;
      }
      try {
        const { review, cost } = await runReview(pi, ctx, { task }, ctx.signal);
        pi.sendMessage({
          customType: "review",
          content: `${renderReview(review)}\nreviewer cost: $${cost.toFixed(4)}`,
          display: true,
          details: review,
        });
      } catch (e) {
        report(ctx, `review failed: ${(e as Error).message}`);
      }
    },
  });
}
