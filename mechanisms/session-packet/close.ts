/**
 * The producer: measure the repository, refuse what the receiver would reject, write a scaffold
 * carrying only measured facts, and validate the agent's fill against those facts.
 * Mirrors snapshot_state.py plus the refusals of close_session.py; makes no commit.
 */
import { randomUUID } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { latestPacketId } from "./chain";
import { END, extract, type Manifest, SCAFFOLD_MARKER, START } from "./packet";
import { type Exec, git, statusPorcelain, unclaimedHeadErrors, validateCloseCommit, validateUnclaimedHead } from "./repo";
import type { PacketConfig } from "./settings";
import { ensureStoreWorktree, listPackets, resolveStore, statusExcludes } from "./store";
import { type Receipt, rerunChecks, type UnreadableReceipt, validatePacket } from "./validate";

export interface Snapshot {
  ok: true;
  path: string;
  packetId: string;
  head: string;
  /**
   * The manifest fields the extension measured, in manifest order; the fill must leave them as
   * written. packet_id, created_at, repository and tests, plus previous_packet_id with the chain.
   */
  measured: Manifest;
  /** The chain was on: the fill instructions also cover previous_packet_id and parked[]. */
  chain: boolean;
}

export interface SnapshotRefusal {
  ok: false;
  error: string;
  failed_receiver_checks?: { name: string; command: string; exit_code: number; output: string }[];
}

function utcIso(now: Date): string {
  return now.toISOString().replace(/\.\d{3}Z$/, "Z");
}

function fileStamp(now: Date): string {
  return utcIso(now).replace(/[-:]/g, "");
}

export async function snapshotPacket(args: {
  repoRoot: string;
  config: PacketConfig;
  objective: string;
  exec: Exec;
  now?: Date;
}): Promise<Snapshot | SnapshotRefusal> {
  const { repoRoot, config, exec } = args;
  const objective = args.objective.trim();
  if (!objective) return { ok: false, error: "refusing to write a packet: the objective is empty" };

  // The receiver re-runs these and rejects on a red one. That is known here, one session earlier,
  // while the cause is still in context, so no packet is written.
  const observedAt = utcIso(new Date());
  const results = await rerunChecks(config.receiverChecks, repoRoot, exec);
  const red = results.filter((r) => r.exit_code !== 0);
  if (red.length) {
    return {
      ok: false,
      error: "refusing to write a packet: a receiver check is red",
      failed_receiver_checks: red.map((r) => ({
        name: r.name, command: r.command, exit_code: r.exit_code, output: `${r.stdout ?? ""}${r.stderr ?? ""}`.slice(-2000),
      })),
    };
  }

  const now = args.now ?? new Date();
  const packetId = randomUUID();
  const store = resolveStore(repoRoot, config);
  const dir = store.kind === "branch" ? store.worktree : store.dir;
  const path = join(dir, `${fileStamp(now)}-${packetId.slice(0, 8)}.md`);
  const chain = config.chain === true;
  const listing = chain || store.kind === "branch" ? await listPackets({ repoRoot, config, exec }) : undefined;

  // Produce-mode refusals that need no narrative: refuse before the agent spends a turn filling.
  // The chain replaces the unclaimed-HEAD refusal: a close without a new commit is allowed.
  const ordering = [
    ...(await validateCloseCommit({ closeCommit: config.closeCommit, repoRoot, exec })),
    ...(chain
      ? []
      : store.kind === "branch"
        ? await unclaimedHeadErrors({ priors: listing?.packets ?? [], repoRoot, exec })
        : await validateUnclaimedHead({ repoRoot, packetDir: config.dir, packetPath: path, exec })),
  ];
  if (ordering.length) return { ok: false, error: `refusing to write a packet: ${ordering.join(" ")}` };
  if (store.kind === "branch") {
    try {
      await ensureStoreWorktree({ repoRoot, store, exec });
    } catch (e) {
      return { ok: false, error: `refusing to write a packet: ${(e as Error).message}` };
    }
  }

  const head = await git(exec, repoRoot, "rev-parse", "HEAD");
  const measured = {
    packet_id: packetId,
    created_at: utcIso(now),
    ...(chain ? { previous_packet_id: await latestPacketId(listing?.packets ?? []) } : {}),
    repository: {
      root: repoRoot,
      branch: await git(exec, repoRoot, "branch", "--show-current"),
      head,
      status_porcelain: await statusPorcelain(exec, repoRoot, statusExcludes(config)),
    },
    tests: results.map((r) => ({ command: r.command, exit_code: r.exit_code, status: r.status, observed_at: observedAt, head })),
  };
  const manifest = {
    packet_version: "1",
    ...measured,
    skills_dispatched: { source: "model-reported", items: [] },
    objective,
    next_action: { task: SCAFFOLD_MARKER, purpose: SCAFFOLD_MARKER },
    scope: { include: [], exclude: [] },
    blockers: [],
    wake_conditions: config.wakeConditions,
    failed_approaches: [],
    claims: [],
    references: [],
    ...(chain ? { parked: [] } : {}),
  };
  const body = [
    START, JSON.stringify(manifest, null, 2), END, "",
    "## Narrative", "", SCAFFOLD_MARKER, "",
    "## Decisions", "", SCAFFOLD_MARKER, "",
    "## What We Tried", "", SCAFFOLD_MARKER, "",
    "## Resume Bootstrap", "", SCAFFOLD_MARKER, "",
  ].join("\n");
  mkdirSync(dir, { recursive: true });
  writeFileSync(path, body, "utf-8");
  return { ok: true, path, packetId, head, measured, chain };
}

/** The user message that asks the agent to fill the scaffold. */
export function fillInstructions(snapshot: Snapshot): string {
  const keys = Object.keys(snapshot.measured);
  const measuredList = `${keys.slice(0, -1).join(", ")} or ${keys.at(-1)}`;
  return [
    `Fill the session packet at ${snapshot.path} (packet format v1). The extension measured the repository and wrote it.`,
    "",
    `1. Replace every ${SCAFFOLD_MARKER} marker: next_action.task (one exact action), next_action.purpose, and the four narrative sections.`,
    "2. Record failed approaches and null results in time order in failed_approaches and What We Tried; record decisions with their reasons.",
    "3. Add each claim the work rests on. `verified` needs a typed probe (`path`, `commit`, or `command`) and evidence; a `command` probe counts only when the project config lists that exact command, otherwise use `unverified` with a source in evidence. When in doubt, write `unverified`.",
    "4. Fill scope, blockers and references (reference artifacts; do not copy them). Keep skills_dispatched.source `model-reported`.",
    `5. Do not edit ${measuredList}: they are measured facts and the validator refuses a packet whose measured facts changed.`,
    "6. Do not commit, and do not change any other file: a commit or a tree change after this snapshot makes the packet stale.",
    "7. Write from this conversation and this repository only. Do not search outside the repository root for context; if the conversation holds little, say so in the narrative and keep claims few.",
    ...(snapshot.chain
      ? [
          "8. Record work set aside for later in parked[], one entry per item: {\"kind\", \"ref\", \"reason\"}. kind is branch-exists or remote-branch-exists (ref = the branch name; remote means origin), stash-exists (ref = the stash commit SHA from `git rev-parse stash@{n}`, never `stash@{n}`, which renumbers), or worktree-exists (ref = its path relative to the repository root). The next open probes every entry.",
        ]
      : []),
    "",
    "Edit only that file. When you stop, the extension validates it in produce mode and reports the receipt.",
  ].join("\n");
}

/** Produce-mode validation of the filled scaffold, plus: the measured facts are as measured. */
export async function validateFilled(args: {
  snapshot: Snapshot;
  repoRoot: string;
  config: PacketConfig;
  exec: Exec;
  /** The packet text to validate; read from the snapshot path when absent. */
  text?: string;
}): Promise<Receipt | UnreadableReceipt> {
  const { snapshot, repoRoot, config, exec } = args;
  const text = args.text ?? readFileSync(snapshot.path, "utf-8");
  const receipt = await validatePacket({ text, packetPath: snapshot.path, mode: "produce", repoRoot, config, exec });
  if (!("packet_id" in receipt)) return receipt;
  const data = extract(text);
  for (const key of Object.keys(snapshot.measured) as (keyof Snapshot["measured"])[]) {
    if (JSON.stringify(data[key]) !== JSON.stringify(snapshot.measured[key])) {
      receipt.errors.push(`measured facts edited: ${key} differs from what /packet-close measured`);
    }
  }
  if (receipt.errors.length) receipt.verdict = "REJECTED";
  return receipt;
}
