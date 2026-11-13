import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

export const CONFIG_PATH = join(".pi", "engineering-env.json");

/** Regexes (as strings) for shell commands that count as running the project's checks. */
export const DEFAULT_CHECK_COMMANDS: readonly string[] = [
  "\\b(npm|pnpm|yarn|bun)( run)? (test|check|lint|typecheck)\\b",
  "\\bbun test\\b",
  "\\b(npx )?(vitest|jest|tsc|eslint|biome)\\b",
  "\\b(python -m )?(pytest|unittest|mypy|ruff)\\b",
  "\\bcargo (test|check|clippy)\\b",
  "\\bgo (test|vet)\\b",
  "\\b(make|just) (test|check|lint)\\b",
  "\\bpre-commit run\\b",
];

export interface Config {
  checkCommands: readonly string[];
  /** Owned and validated by the session-packet extension. */
  sessionPacket?: Record<string, unknown>;
}

/** `ignored` says why a present file was not honoured; the config is then the defaults. */
export type ConfigResult = { ok: true; config: Config; ignored?: string } | { ok: false; error: string };

/**
 * `trusted` is Pi's `ctx.isProjectTrusted()`. Pi also reports true for a project whose `.pi`
 * holds nothing Pi gates, without asking (Pi 1.5.0), so the file is honoured only when
 * `.pi/settings.json` exists as well: then the trust is a decision someone made.
 */
export function loadConfig(projectRoot: string, trusted: boolean): ConfigResult {
  const path = join(projectRoot, CONFIG_PATH);
  const defaults = { checkCommands: DEFAULT_CHECK_COMMANDS };
  if (!existsSync(path)) return { ok: true, config: defaults };
  if (!existsSync(join(projectRoot, ".pi", "settings.json"))) {
    return { ok: true, config: defaults, ignored: `${CONFIG_PATH} ignored: the project has no .pi/settings.json, so Pi never asked whether to trust it. Add .pi/settings.json ({} is enough), then trust the project with /trust or run pi with -a.` };
  }
  if (!trusted) {
    return { ok: true, config: defaults, ignored: `${CONFIG_PATH} ignored: Pi does not trust this project. Trust it with /trust, or run pi with -a to trust it for one command.` };
  }
  const fail = (why: string): ConfigResult => ({ ok: false, error: `${CONFIG_PATH}: ${why}` });

  let raw: unknown;
  try {
    raw = JSON.parse(readFileSync(path, "utf-8"));
  } catch (e) {
    return fail(`not valid JSON (${(e as Error).message})`);
  }
  if (typeof raw !== "object" || raw === null || Array.isArray(raw)) return fail("must be a JSON object");
  const obj = raw as Record<string, unknown>;

  let checkCommands: readonly string[] = DEFAULT_CHECK_COMMANDS;
  if (obj.checkCommands !== undefined) {
    if (!Array.isArray(obj.checkCommands)) return fail("checkCommands must be an array of regex strings");
    for (const [i, pattern] of obj.checkCommands.entries()) {
      if (typeof pattern !== "string") return fail(`checkCommands[${i}] must be a string`);
      try {
        new RegExp(pattern);
      } catch (e) {
        return fail(`checkCommands[${i}] is not a valid regex (${(e as Error).message})`);
      }
    }
    checkCommands = obj.checkCommands as string[];
  }

  const config: Config = { checkCommands };
  if (obj.sessionPacket !== undefined) {
    const sp = obj.sessionPacket;
    if (typeof sp !== "object" || sp === null || Array.isArray(sp)) return fail("sessionPacket must be an object");
    config.sessionPacket = sp as Record<string, unknown>;
  }
  return { ok: true, config };
}
