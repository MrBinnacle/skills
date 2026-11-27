// The panel: a Pi overlay that only displays. It never takes the keys, so the prompt is the one
// place to type; alt+h opens a menu to act on a heads-up (index.ts). The TUI kit is passed in,
// so this file has no Pi runtime import and bun tests drive it.
import { CLOSED, MEMORY_MAX, type Note, type State, statusOf } from "./state";

export type Kit = {
  truncateToWidth(text: string, width: number, ellipsis?: string, pad?: boolean): string;
  wrapTextWithAnsi(text: string, width: number): string[];
};
export type ThemeLike = { fg(color: string, text: string): string; bold(text: string): string };

const SHOWN_THOUGHTS = 3;
const SHOWN_NOTES = 4;
const hhmm = (at: number) => new Date(at).toTimeString().slice(0, 5);

/** Open heads-ups, newest first: the ones the panel shows and the alt+h menu offers. */
export const openNotes = (s: Pick<State, "notes">): Note[] => s.notes.filter((n) => !CLOSED.has(n.mark)).slice(-SHOWN_NOTES).reverse();

export class Panel {
  constructor(
    private kit: Kit,
    private theme: ThemeLike,
    private state: () => State,
    private observerStatus: () => string,
  ) {}

  render(width: number): string[] {
    const { theme: t, kit } = this;
    const w = Math.max(10, width - 2);
    const s = this.state();
    const out: string[] = [];
    // Every line wraps inside the panel, so nothing runs off its edge.
    const put = (text: string, indent = "") => {
      for (const l of kit.wrapTextWithAnsi(text, Math.max(4, w - indent.length))) out.push(indent + l);
    };
    const head = (label: string, right: string) => {
      out.push("");
      out.push(`${t.bold(label)}${right ? t.fg("dim", ` · ${right}`) : ""}`);
    };

    const notes = openNotes(s);
    out.push(`${t.fg("accent", "◆")} ${t.bold("Binnacle")}${t.fg("dim", notes.length ? "  alt+h act on a heads-up" : "  alt+h menu")}`);

    head("Heads-ups", this.observerStatus());
    for (const n of notes) put(`${n.mark === "read" ? t.fg("dim", "◇") : t.fg("warning", "◆")} ${n.line}`);
    head("Log", s.log.length ? `${s.log.length} kept` : "empty");
    if (!s.log.length) put(t.fg("dim", "/log keeps a thought beside this session."));
    for (const th of s.log.slice(-SHOWN_THOUGHTS).reverse()) put(`${t.fg("dim", hhmm(th.at))} ${th.text}`, "  ");

    const status = statusOf(s);
    head("Memory", s.draft.length ? `${s.draft.length} of ${MEMORY_MAX} lines` : "");
    put(status.tone ? t.fg(status.tone, status.text) : t.fg("dim", status.text));
    s.draft.forEach((text, n) => put(`${t.fg("dim", `${n + 1}`)} ${text}`, "  "));

    return out.map((l) => kit.truncateToWidth(` ${l}`, width, "…", true));
  }

  invalidate(): void {}
}
