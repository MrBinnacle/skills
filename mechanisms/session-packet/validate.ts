/** The validator entrypoint: one packet in, one receipt out (PACKET-FORMAT.md "Receipt"). */
import { chainNotes } from "./chain";
import { ghSquashMergeProbe, type SquashMergeProbe } from "./head";
import { extract, lintReceiverChecks, publishScan, validateRecordedChecks, validateStructure, type ReceiverCheck } from "./packet";
import { verifyParked } from "./parked";
import {
  type Exec, shell, type StoredPacket, unclaimedHeadErrors, validateCloseCommit, validateRepository, validateUnclaimedHead,
} from "./repo";
import type { PacketConfig } from "./settings";
import { listPackets, type PacketListing, resolveStore, statusExcludes } from "./store";

export type Mode = "produce" | "receive";

export interface CheckResult {
  name: string;
  command: string;
  exit_code: number;
  status: "passed" | "failed";
  duration_ms: number;
  output?: string;
  stdout?: string;
  stderr?: string;
}

export interface Receipt {
  verdict: "ACCEPTED" | "REJECTED";
  packet_id: unknown;
  errors: string[];
  notes: string[];
  checks: CheckResult[];
  /** REJECTED receive receipts only; `summary` is always the last key. */
  packet_assertions_held?: boolean;
  failed_receiver_checks?: string[];
  summary?: string;
}

/** The packet could not be read at all (no markers, bad JSON, git failure). */
export interface UnreadableReceipt {
  verdict: "REJECTED";
  errors: string[];
}

const PASSED_OUTPUT = "omitted: check passed, exit code is the verdict";

/**
 * Run every receiver check. A passing check's output is decoration and is omitted (recorded as
 * omitted, not dropped silently); a failing check keeps the tail of its output as the diagnostic.
 */
export async function rerunChecks(checks: readonly ReceiverCheck[], repoRoot: string, exec: Exec): Promise<CheckResult[]> {
  const results: CheckResult[] = [];
  for (const check of checks) {
    const started = performance.now();
    const result = await shell(exec, repoRoot, check.command);
    const base = { name: check.name, command: check.command, exit_code: result.code };
    const duration_ms = Math.round(performance.now() - started);
    results.push(
      result.code === 0
        ? { ...base, status: "passed", duration_ms, output: PASSED_OUTPUT }
        : { ...base, status: "failed", duration_ms, stdout: result.stdout.slice(-2000), stderr: result.stderr.slice(-2000) },
    );
  }
  return results;
}

export async function validatePacket(args: {
  text: string;
  packetPath: string;
  mode: Mode;
  repoRoot: string;
  /** The project's `sessionPacket` section; `undefined` when the project declares none. */
  config: PacketConfig | undefined;
  exec: Exec;
  /** The store listing the caller already made; listed here when needed and absent. */
  listing?: PacketListing;
  /** The ancestor policy's squash-merge probe; defaults to asking `gh`. */
  squashMerged?: SquashMergeProbe;
}): Promise<Receipt | UnreadableReceipt> {
  const { text, packetPath, mode, repoRoot, config, exec } = args;
  try {
    const data = extract(text);
    const errors = validateStructure(data, text);
    const notes: string[] = [];
    let checks: CheckResult[] = [];
    if (config) notes.push(...lintReceiverChecks(config.receiverChecks));
    if (mode === "produce") errors.push(...validateRecordedChecks(data));

    const repo = await validateRepository({
      data,
      repoRoot,
      exec,
      packetDir: config ? statusExcludes(config) : undefined,
      allowedCommands: config ? [...config.receiverChecks.map((c) => c.command), ...config.trustedProbeCommands] : [],
      // Produce mode records the HEAD it measured, so a moved HEAD there is always stale.
      headPolicy: mode === "receive" ? config?.headPolicy : undefined,
      squashMerged: args.squashMerged ?? ghSquashMergeProbe(exec),
    });
    errors.push(...repo.errors);
    notes.push(...repo.notes);
    if (mode === "receive") {
      const parked = await verifyParked({ data, repoRoot, exec });
      errors.push(...parked.errors);
      notes.push(...parked.notes);
    }

    const branchStore = config ? resolveStore(repoRoot, config).kind === "branch" : false;
    const needsListing = config && (config.chain || (mode === "produce" && branchStore));
    const listing = args.listing ?? (needsListing ? await listPackets({ repoRoot, config, exec }) : undefined);
    if (mode === "receive" && listing) notes.push(...listing.notes);
    // A packet path is a file path or `<ref>:<name>`; either way the name is the last segment.
    const own = packetPath.split(/[\\/:]/).at(-1) ?? packetPath;
    if (mode === "produce") {
      // A branch store pushes the packet to origin. Its publish scan runs here too, so a leak is a
      // produce-mode error the agent gets a turn to correct, not a refusal after the run ended.
      if (branchStore) errors.push(...publishScan(text));
      errors.push(...(await validateCloseCommit({ closeCommit: config?.closeCommit, repoRoot, exec })));
      // The chain replaces the unclaimed-HEAD refusal: a close without a new commit is allowed.
      if (config && !config.chain) {
        errors.push(...(branchStore
          ? await unclaimedHeadErrors({ priors: (listing?.packets ?? []).filter((p) => p.name !== own), repoRoot, exec })
          : await validateUnclaimedHead({ repoRoot, packetDir: config.dir, packetPath, exec })));
      }
    }
    if (config?.chain && listing) {
      const packets: StoredPacket[] = listing.packets.some((p) => p.name === own)
        ? listing.packets
        : [...listing.packets, { name: own, source: packetPath, read: async () => text }];
      notes.push(...(await chainNotes(packets)));
    }

    // Above: assertions the PACKET made. Below: checks the RECEIVER runs. The split is what a
    // REJECTED receipt reports, so a reader can tell a packet defect from a gate defect.
    const packetErrors = errors.length;
    const failedReceiverChecks: string[] = [];
    if (mode === "receive") {
      if (!config) {
        // A verification that omitting the config switches off is not a verification.
        errors.push("receive mode requires a sessionPacket config");
      } else {
        checks = await rerunChecks(config.receiverChecks, repoRoot, exec);
        for (const check of checks) {
          if (check.exit_code !== 0) {
            failedReceiverChecks.push(check.name);
            errors.push(`receiver check failed: ${check.name}`);
          }
        }
      }
    }

    const receipt: Receipt = {
      verdict: errors.length ? "REJECTED" : "ACCEPTED",
      packet_id: data.packet_id,
      errors,
      notes,
      checks,
    };
    if (errors.length && mode === "receive") {
      const held = packetErrors === 0;
      receipt.packet_assertions_held = held;
      receipt.failed_receiver_checks = failedReceiverChecks;
      receipt.summary = held
        ? "Every assertion the packet made was verified against this tree: structure, branch, HEAD and every " +
          `claim probe held. The rejection rests on the named receiver checks alone: ${failedReceiverChecks.join(", ")}.`
        : "The packet's own assertions did not all hold, or were not verified; the rejection is not " +
          "attributable to the receiver checks alone.";
    }
    return receipt;
  } catch (e) {
    return { verdict: "REJECTED", errors: [e instanceof Error ? e.message : String(e)] };
  }
}
