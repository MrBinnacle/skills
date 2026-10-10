/** Packet format v1: manifest extraction and structure rules. Pure; no Pi imports, no I/O. */

export const START = "<!-- SESSION-PACKET-V1";
export const END = "SESSION-PACKET-V1 -->";

/** A packet-format violation that makes the whole packet unreadable. */
export class PacketError extends Error {}

// Manifest keys stay snake_case: packets must remain readable by validate_packet.py.
export type Manifest = Record<string, unknown>;

export function extract(text: string): Manifest {
  const start = text.indexOf(START);
  const end = text.indexOf(END);
  if (start < 0 || end < 0 || end <= start) throw new PacketError("packet markers are absent or out of order");
  const raw = text.slice(start + START.length, end).trim();
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    throw new PacketError(`manifest is not valid JSON: ${(e as Error).message}`);
  }
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new PacketError("manifest must be a JSON object");
  }
  return data as Manifest;
}

const REQUIRED = [
  "packet_version", "packet_id", "created_at", "repository", "tests",
  "skills_dispatched", "objective", "next_action", "scope", "blockers",
  "wake_conditions", "failed_approaches", "claims", "references",
];

const SECRET_PATTERNS = [
  /sk-[A-Za-z0-9_-]{16,}/,
  /gh[pousr]_[A-Za-z0-9]{20,}/,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
];
const SECTIONS = ["## Narrative", "## Decisions", "## What We Tried", "## Resume Bootstrap"];
const ISO_8601 = /^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$/;

function nonempty(value: unknown): boolean {
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value).length > 0;
  return true;
}

function obj(value: unknown): Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function list(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export const SCAFFOLD_MARKER = "__REQUIRED__";
const PLACEHOLDER_TOKENS = ["TODO", "TBD"];
const LIST_PREFIX = /^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s*)*/;

function stripChars(s: string, chars: string): string {
  let a = 0;
  let b = s.length;
  while (a < b && chars.includes(s[a]!)) a++;
  while (b > a && chars.includes(s[b - 1]!)) b--;
  return s.slice(a, b);
}

/** The bare token, if `s` is a placeholder token and nothing else. */
function asToken(s: string): string | undefined {
  const candidate = stripChars(s.trim(), ":.").trim().toUpperCase();
  return PLACEHOLDER_TOKENS.includes(candidate) ? candidate : undefined;
}

function* walkStrings(value: unknown): Generator<string> {
  if (typeof value === "string") yield value;
  else if (Array.isArray(value)) for (const v of value) yield* walkStrings(v);
  else if (typeof value === "object" && value !== null) for (const v of Object.values(value)) yield* walkStrings(v);
}

/**
 * Placeholder tokens that are genuinely placeholders: a line carrying only the token (after list
 * and emphasis markup), or a manifest value that is only the token. A TODO inside prose is content;
 * rejecting it teaches the producer to censor honest narrative.
 */
export function placeholderTokens(data: Manifest, text: string): Set<string> {
  const found = new Set<string>();
  for (const line of text.split(/\r?\n/)) {
    if (asToken(stripChars(line.replace(LIST_PREFIX, "").trim(), "*_`#").trim())) {
      const upper = line.toUpperCase();
      for (const token of PLACEHOLDER_TOKENS) if (upper.includes(token)) found.add(token);
    }
  }
  for (const value of walkStrings(data)) {
    const token = asToken(value);
    if (token) found.add(token);
  }
  return found;
}

export function validateStructure(data: Manifest, text: string): string[] {
  const errors: string[] = [];
  for (const key of REQUIRED) if (!(key in data)) errors.push(`missing field: ${key}`);
  for (const key of ["packet_id", "created_at", "objective"]) {
    if (key in data && !nonempty(data[key])) errors.push(`empty field: ${key}`);
  }
  if (data.packet_version !== "1") errors.push("packet_version must equal 1");
  const created = String(data.created_at ?? "");
  if (!ISO_8601.test(created) || Number.isNaN(Date.parse(created))) errors.push("created_at must be ISO-8601");
  const repo = obj(data.repository);
  for (const key of ["root", "branch", "head", "status_porcelain"]) {
    if (!(key in repo)) errors.push(`missing repository field: ${key}`);
  }
  const nextAction = obj(data.next_action);
  for (const key of ["task", "purpose"]) {
    if (!nonempty(nextAction[key])) errors.push(`empty next_action field: ${key}`);
  }
  const skills = obj(data.skills_dispatched);
  if (skills.source !== "telemetry" && skills.source !== "model-reported") {
    errors.push("skills_dispatched.source must be telemetry or model-reported");
  }
  if (!Array.isArray(skills.items)) errors.push("skills_dispatched.items must be an array");
  list(data.tests).forEach((raw, i) => {
    const test = obj(raw);
    for (const key of ["command", "exit_code", "observed_at", "head"]) {
      if (!(key in test)) errors.push(`tests[${i}] lacks ${key}`);
    }
    if (!Number.isInteger(test.exit_code)) errors.push(`tests[${i}].exit_code must be an integer`);
  });
  list(data.claims).forEach((raw, i) => {
    const claim = obj(raw);
    const status = claim.status;
    if (status !== "verified" && status !== "unverified") errors.push(`claims[${i}].status is invalid`);
    if (!nonempty(claim.id) || !nonempty(claim.text)) errors.push(`claims[${i}] lacks id or text`);
    if (status === "verified") {
      const probe = obj(claim.probe);
      if (typeof probe.kind !== "string" || !["path", "commit", "command"].includes(probe.kind) || !nonempty(probe.value)) {
        errors.push(`claims[${i}] lacks a typed probe`);
      }
      if (!nonempty(claim.evidence)) errors.push(`claims[${i}] lacks evidence`);
    }
    if (status === "unverified" && !nonempty(claim.evidence)) errors.push(`claims[${i}] lacks a source in evidence`);
  });
  if (text.includes(SCAFFOLD_MARKER)) errors.push(`unfinished marker present: ${SCAFFOLD_MARKER}`);
  for (const token of [...placeholderTokens(data, text)].sort()) errors.push(`unfinished marker present: ${token}`);
  for (const pattern of SECRET_PATTERNS) if (pattern.test(text)) errors.push("possible secret detected");
  for (const section of SECTIONS) if (!text.includes(section)) errors.push(`missing narrative section: ${section}`);
  return errors;
}

/**
 * Refuse a manifest whose own tests[] records a red receiver check. The producer refuses before
 * writing; this is the second line, for a packet written by another caller or edited by hand.
 */
export function validateRecordedChecks(data: Manifest): string[] {
  const errors: string[] = [];
  list(data.tests).forEach((raw, i) => {
    const test = obj(raw);
    const code = test.exit_code;
    if (Number.isInteger(code) && code !== 0) {
      errors.push(
        `recorded receiver check failed: tests[${i}] exited ${code}: ${test.command}. ` +
          "Fix the cause and produce the packet again.",
      );
    }
  });
  return errors;
}

export interface ReceiverCheck {
  name: string;
  command: string;
}

// Signals through stdout and always exits zero, so it cannot fail. Name the known instance.
const UNFAILABLE_CHECK = /^\s*git\s+status(\s+--porcelain(=\S+)?)*\s*$/;

export function lintReceiverChecks(checks: readonly ReceiverCheck[]): string[] {
  return checks
    .filter((check) => UNFAILABLE_CHECK.test(check.command))
    .map(
      (check) =>
        `receiver check '${check.name}' always exits zero, so it cannot fail and gates nothing: ${check.command}`,
    );
}
