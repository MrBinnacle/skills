/** The `sessionPacket` section of `.pi/engineering-env.json`, parsed into a domain type. Pure. */
import type { ReceiverCheck } from "./packet";

export const DEFAULT_DIR = ".pi/session-packets";

export interface PacketConfig {
  /** Packet directory, relative to the repository root unless absolute. */
  dir: string;
  receiverChecks: ReceiverCheck[];
  trustedProbeCommands: string[];
  /** Literal substring HEAD's commit message must carry in produce mode. Opt-in. */
  closeCommit?: { contains: string };
  wakeConditions: string[];
}

export type PacketConfigResult = { ok: true; config: PacketConfig } | { ok: false; error: string };

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function parseSessionPacketConfig(raw: Record<string, unknown> | undefined): PacketConfigResult {
  const fail = (key: string, why: string): PacketConfigResult => ({ ok: false, error: `sessionPacket.${key} ${why}` });
  const section = raw ?? {};
  const config: PacketConfig = { dir: DEFAULT_DIR, receiverChecks: [], trustedProbeCommands: [], wakeConditions: [] };

  if (section.dir !== undefined) {
    if (typeof section.dir !== "string" || section.dir === "") return fail("dir", "must be a non-empty string");
    config.dir = section.dir;
  }
  if (section.receiverChecks !== undefined) {
    if (!Array.isArray(section.receiverChecks)) return fail("receiverChecks", "must be an array");
    for (const [i, check] of section.receiverChecks.entries()) {
      if (!isRecord(check) || typeof check.command !== "string" || check.command === "") {
        return fail(`receiverChecks[${i}].command`, "must be a non-empty string");
      }
      if (check.name !== undefined && typeof check.name !== "string") return fail(`receiverChecks[${i}].name`, "must be a string");
      config.receiverChecks.push({ name: check.name || check.command, command: check.command });
    }
  }
  if (section.trustedProbeCommands !== undefined) {
    if (!isStringArray(section.trustedProbeCommands)) return fail("trustedProbeCommands", "must be an array of strings");
    config.trustedProbeCommands = section.trustedProbeCommands;
  }
  if (section.closeCommit !== undefined) {
    const contains = isRecord(section.closeCommit) ? section.closeCommit.contains : undefined;
    if (typeof contains !== "string" || contains === "") return fail("closeCommit.contains", "must be a non-empty string");
    config.closeCommit = { contains };
  }
  if (section.wakeConditions !== undefined) {
    if (!isStringArray(section.wakeConditions)) return fail("wakeConditions", "must be an array of strings");
    config.wakeConditions = section.wakeConditions;
  }
  return { ok: true, config };
}
