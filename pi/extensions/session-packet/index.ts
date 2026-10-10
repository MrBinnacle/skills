/**
 * Pi adapter for the session-boundary packet: wires commands and lifecycle events to the core.
 *
 * /packet-close <objective>  measure, refuse, write a scaffold, ask the agent to fill it; the fill
 *                            is validated in produce mode when the agent stops (agent_before_settle).
 * /packet-open [path]        validate the latest (or given) packet in receive mode; report the receipt.
 * session_start              same as /packet-open, only when the project declares `sessionPacket`.
 */
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { loadConfig } from "../shared/config";
import { fillInstructions, type Snapshot, snapshotPacket, validateFilled } from "./close";
import { type Exec, git, packetFiles } from "./repo";
import { type PacketConfig, parseSessionPacketConfig } from "./settings";
import { validatePacket } from "./validate";

/** Corrections the agent gets after its first fill before the extension gives up. */
const MAX_CORRECTIONS = 2;

type Level = "info" | "warning" | "error";

function report(ctx: ExtensionContext, message: string, level: Level): void {
  if (ctx.hasUI) ctx.ui.notify(message, level);
  else console.error(message);
}

type Loaded = { ok: true; config: PacketConfig; declared: boolean } | { ok: false; error: string };

function loadPacketConfig(cwd: string): Loaded {
  const file = loadConfig(cwd);
  if (!file.ok) return file;
  const parsed = parseSessionPacketConfig(file.config.sessionPacket);
  if (!parsed.ok) return { ok: false, error: `.pi/engineering-env.json: ${parsed.error}` };
  return { ok: true, config: parsed.config, declared: file.config.sessionPacket !== undefined };
}

interface Pending {
  snapshot: Snapshot;
  config: PacketConfig;
  repoRoot: string;
  corrections: number;
}

export default function (pi: ExtensionAPI) {
  const exec: Exec = (command, args, options) => pi.exec(command, args, options);
  let pending: Pending | undefined;

  async function receive(ctx: ExtensionContext, explicitPath: string | undefined): Promise<void> {
    const loaded = loadPacketConfig(ctx.cwd);
    if (!loaded.ok) return report(ctx, `session-packet: ${loaded.error}`, "error");
    const repoRoot = await git(exec, ctx.cwd, "rev-parse", "--show-toplevel");
    const packetPath = explicitPath
      ? resolve(ctx.cwd, explicitPath)
      : packetFiles(resolve(repoRoot, loaded.config.dir))[0];
    if (!packetPath) return report(ctx, `session-packet: no packet in ${loaded.config.dir}`, "warning");
    const receipt = await validatePacket({
      text: readFileSync(packetPath, "utf-8"),
      packetPath,
      mode: "receive",
      repoRoot,
      config: loaded.declared ? loaded.config : undefined,
      exec,
    });
    const json = JSON.stringify(receipt, null, 2);
    report(ctx, json, receipt.verdict === "ACCEPTED" ? "info" : "error");
    pi.sendMessage({ customType: "session-packet-receipt", content: `Session packet ${packetPath}\n${json}`, display: true });
  }

  pi.registerCommand("packet-close", {
    description: "Close the session: snapshot repo state into a packet scaffold for the agent to fill",
    handler: async (args, ctx) => {
      try {
        const loaded = loadPacketConfig(ctx.cwd);
        if (!loaded.ok) return report(ctx, `session-packet: ${loaded.error}`, "error");
        const repoRoot = await git(exec, ctx.cwd, "rev-parse", "--show-toplevel");
        const result = await snapshotPacket({ repoRoot, config: loaded.config, objective: args, exec });
        if (!result.ok) return report(ctx, JSON.stringify(result, null, 2), "error");
        pending = { snapshot: result, config: loaded.config, repoRoot, corrections: 0 };
        const message = fillInstructions(result);
        if (ctx.isIdle()) pi.sendUserMessage(message);
        else pi.sendUserMessage(message, { deliverAs: "followUp" });
      } catch (e) {
        report(ctx, `session-packet: /packet-close failed: ${(e as Error).message}`, "error");
      }
    },
  });

  pi.registerCommand("packet-open", {
    description: "Validate the latest (or given) session packet in receive mode and report the receipt",
    handler: async (args, ctx) => {
      try {
        await receive(ctx, args.trim() || undefined);
      } catch (e) {
        report(ctx, `session-packet: /packet-open failed: ${(e as Error).message}`, "error");
      }
    },
  });

  pi.on("agent_before_settle", async (event, ctx) => {
    if (!pending) return;
    const current = pending;
    try {
      if (event.outcome !== "completed") {
        pending = undefined;
        return report(ctx, `session-packet: run ${event.outcome}; packet not validated: ${current.snapshot.path}`, "warning");
      }
      const receipt = await validateFilled({ snapshot: current.snapshot, repoRoot: current.repoRoot, config: current.config, exec });
      const json = JSON.stringify(receipt, null, 2);
      if (receipt.verdict === "ACCEPTED") {
        pending = undefined;
        return report(ctx, `Session packet ${current.snapshot.path}\n${json}`, "info");
      }
      // Not gated on event.context.canContinue: on Pi 1.1.0 it read false while a requested
      // continuation still ran (see ../DESIGN.md).
      if (current.corrections < MAX_CORRECTIONS) {
        current.corrections++;
        return {
          continue: true,
          entries: [{
            type: "custom_message" as const,
            customType: "session-packet-receipt",
            display: true,
            content: `The packet at ${current.snapshot.path} was REJECTED in produce mode. Fix these errors in that file only:\n${json}`,
          }],
        };
      }
      pending = undefined;
      report(ctx, `Session packet REJECTED; not ready for handoff: ${current.snapshot.path}\n${json}`, "error");
    } catch (e) {
      pending = undefined;
      report(ctx, `session-packet: validation failed: ${(e as Error).message}`, "error");
    }
  });

  pi.on("session_start", async (event, ctx) => {
    if (event.reason === "reload" || event.reason === "fork") return;
    try {
      const loaded = loadPacketConfig(ctx.cwd);
      if (!loaded.ok) return report(ctx, `session-packet: ${loaded.error}`, "error");
      if (!loaded.declared) return;
      const repoRoot = await git(exec, ctx.cwd, "rev-parse", "--show-toplevel");
      if (!packetFiles(resolve(repoRoot, loaded.config.dir)).length) return;
      await receive(ctx, undefined);
    } catch (e) {
      report(ctx, `session-packet: startup check failed: ${(e as Error).message}`, "error");
    }
  });
}
