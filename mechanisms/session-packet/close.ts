/**
 * The producer: measure the repository, refuse what the receiver would reject, write a scaffold
 * carrying only measured facts, and validate the agent's fill against those facts.
 * Mirrors snapshot_state.py plus the refusals of close_session.py; makes no commit.
 */
import { randomUUID } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { END, extract, type Manifest, SCAFFOLD_MARKER, START } from "./packet";
import { type Exec, git, statusPorcelain, validateCloseCommit, validateUnclaimedHead } from "./repo";
import type { PacketConfig } from "./settings";
import { type Receipt, rerunChecks, type UnreadableReceipt, validatePacket } from "./validate";

export interface Snapshot {
  ok: true;
  path: string;
  packetId: string;
  head: string;
  /** The manifest fields the extension measured; the fill must leave them as written. */
  measured: Pick<Manifest, "packet_id" | "created_at" | "repository" | "tests">;
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
  const dir = resolve(repoRoot, config.dir);
  const path = join(dir, `${fileStamp(now)}-${packetId.slice(0, 8)}.md`);

  // Produce-mode refusals that need no narrative: refuse before the agent spends a turn filling.
  const ordering = [
    ...(await validateCloseCommit({ closeCommit: config.closeCommit, repoRoot, exec })),
    ...(await validateUnclaimedHead({ repoRoot, packetDir: config.dir, packetPath: path, exec })),
  ];
  if (ordering.length) return { ok: false, error: `refusing to write a packet: ${ordering.join(" ")}` };

  const head = await git(exec, repoRoot, "rev-parse", "HEAD");
  const measured = {
    packet_id: packetId,
    created_at: utcIso(now),
    repository: {
      root: repoRoot,
      branch: await git(exec, repoRoot, "branch", "--show-current"),
      head,
      status_porcelain: await statusPorcelain(exec, repoRoot, config.dir),
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
  return { ok: true, path, packetId, head, measured };
}

/** The user message that asks the agent to fill the scaffold. */
export function fillInstructions(snapshot: Snapshot): string {
  return [
    `Fill the session packet at ${snapshot.path} (packet format v1). The extension measured the repository and wrote it.`,
    "",
    `1. Replace every ${SCAFFOLD_MARKER} marker: next_action.task (one exact action), next_action.purpose, and the four narrative sections.`,
    "2. Record failed approaches and null results in time order in failed_approaches and What We Tried; record decisions with their reasons.",
    "3. Add each claim the work rests on. `verified` needs a typed probe (`path`, `commit`, or `command`) and evidence; a `command` probe counts only when the project config lists that exact command, otherwise use `unverified` with a source in evidence. When in doubt, write `unverified`.",
    "4. Fill scope, blockers and references (reference artifacts; do not copy them). Keep skills_dispatched.source `model-reported`.",
    "5. Do not edit packet_id, created_at, repository or tests: they are measured facts and the validator refuses a packet whose measured facts changed.",
    "6. Do not commit, and do not change any other file: a commit or a tree change after this snapshot makes the packet stale.",
    "7. Write from this conversation and this repository only. Do not search outside the repository root for context; if the conversation holds little, say so in the narrative and keep claims few.",
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
}): Promise<Receipt | UnreadableReceipt> {
  const { snapshot, repoRoot, config, exec } = args;
  const text = readFileSync(snapshot.path, "utf-8");
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
