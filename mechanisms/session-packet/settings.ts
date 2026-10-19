/** The `sessionPacket` section of `.pi/engineering-env.json`, parsed into a domain type. Pure. */
import type { ReceiverCheck } from "./packet";

export const DEFAULT_DIR = ".pi/session-packets";
/** Private worktree of the branch store, relative to the repository root unless absolute. */
export const DEFAULT_STORE_WORKTREE = "var/session-log-worktree";

/** How a receiver judges a packet HEAD that differs from the current HEAD. */
export type HeadPolicy = "exact" | "ancestor";

/** Where packets live: files in `dir`, or commits on an orphan branch pushed to origin. */
export type PacketStore = { kind: "dir" } | { kind: "branch"; ref: string; worktree: string };

export interface PacketConfig {
  /** Packet directory, relative to the repository root unless absolute. */
  dir: string;
  receiverChecks: ReceiverCheck[];
  trustedProbeCommands: string[];
  /** Literal substring HEAD's commit message must carry in produce mode. Opt-in. */
  closeCommit?: { contains: string };
  wakeConditions: string[];
  /** Opt-in; absent means "exact". Applies to receive mode only. */
  headPolicy?: HeadPolicy;
  /** Opt-in: record previous_packet_id and replace the unclaimed-HEAD refusal with chain checks. */
  chain?: boolean;
  /** Opt-in; absent means `{ kind: "dir" }`. */
  store?: PacketStore;
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
  if (section.headPolicy !== undefined) {
    if (section.headPolicy !== "exact" && section.headPolicy !== "ancestor") return fail("headPolicy", 'must be "exact" or "ancestor"');
    config.headPolicy = section.headPolicy;
  }
  if (section.chain !== undefined) {
    if (typeof section.chain !== "boolean") return fail("chain", "must be a boolean");
    config.chain = section.chain;
  }
  if (section.store !== undefined) {
    const store = section.store;
    if (!isRecord(store)) return fail("store", "must be an object");
    if (store.kind === "dir") config.store = { kind: "dir" };
    else if (store.kind === "branch") {
      if (typeof store.ref !== "string" || store.ref === "") return fail("store.ref", "must be a non-empty string");
      const worktree = store.worktree ?? DEFAULT_STORE_WORKTREE;
      if (typeof worktree !== "string" || worktree === "") return fail("store.worktree", "must be a non-empty string");
      config.store = { kind: "branch", ref: store.ref, worktree };
    } else return fail("store.kind", 'must be "dir" or "branch"');
  }
  return { ok: true, config };
}
