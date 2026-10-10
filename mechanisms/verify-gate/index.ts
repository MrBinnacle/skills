import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { loadConfig } from "../shared/config";
import { createGate, type Gate } from "./gate";

function report(ctx: ExtensionContext, message: string): void {
  if (ctx.hasUI) ctx.ui.notify(message, "error");
  else console.error(message);
}

export default function (pi: ExtensionAPI) {
  let gate: Gate | undefined;

  pi.on("session_start", async (_event, ctx) => {
    const result = loadConfig(ctx.cwd);
    if (result.ok) {
      gate = createGate(result.config.checkCommands, ctx.cwd);
    } else {
      gate = undefined;
      report(ctx, `verify-gate disabled: ${result.error}`);
    }
  });

  // Fires once per user prompt; a continuation the gate requests does not fire it again
  // (observed on Pi 1.1.0), so the one-nudge-per-run guard holds across the continuation.
  pi.on("before_agent_start", async () => {
    gate?.runStarted();
  });

  pi.on("tool_result", async (event) => {
    gate?.toolFinished(event.toolName, event.input, event.isError);
  });

  pi.on("agent_before_settle", async (event) => {
    const nudge = gate?.beforeSettle(event.outcome);
    if (!nudge) return undefined;
    return {
      entries: [{ type: "custom_message", customType: "verify-gate", content: nudge, display: true }],
      continue: true,
    };
  });
}
