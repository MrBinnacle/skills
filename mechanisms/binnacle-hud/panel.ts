// The panel: a Pi overlay anchored top-right that stays visible without taking the keys, so the
// prompt keeps its half-typed text. alt+h or /hud gives it the keys; Esc hands them back.
// The TUI kit is passed in, so this file has no Pi runtime import and bun tests drive it.
import { statusOf, type State, MEMORY_MAX } from "./state";
import { CLOSED, type Mark, type Note } from "./state";

export type Kit = {
  matchesKey(data: string, key: string): boolean;
  truncateToWidth(text: string, width: number, ellipsis?: string, pad?: boolean): string;
  wrapTextWithAnsi(text: string, width: number): string[];
  Input: new (options?: { prompt?: string; placeholder?: string; placeholderStyle?: (t: string) => string }) => {
    focused: boolean;
    getValue(): string;
    setValue(v: string): void;
    handleInput(data: string): void;
    render(width: number): readonly string[];
    onSubmit?: (v: string) => void;
    onEscape?: () => void;
  };
};
export type ThemeLike = { fg(color: string, text: string): string; bold(text: string): string };
export type KeysLike = { matches(data: string, id: string): boolean };

export type Actions = {
  keep(text: string): void;
  addMemory(text: string): void;
  removeMemory(index: number): void;
  send(): void;
  mark(key: string, mark: Mark): void;
  forget(at: number): void;
  escape(): void;
  close(): void;
};

type Item = { kind: "memory"; index: number } | { kind: "note"; note: Note } | { kind: "thought"; at: number };
const SHOWN_THOUGHTS = 5;
const SHOWN_NOTES = 4;

const hhmm = (at: number) => new Date(at).toTimeString().slice(0, 5);
export class Panel {
  target: "log" | "memory" = "log";
  private sel = -1; // -1 the field; otherwise an index into items()
  private open: string | null = null; // the note whose details show
  private confirming = false;
  private input: InstanceType<Kit["Input"]>;
  private _focused = false;

  constructor(
    private kit: Kit,
    private theme: ThemeLike,
    private state: () => State,
    private act: Actions,
  ) {
    this.input = new kit.Input({ prompt: "", placeholder: "a thought…", placeholderStyle: (t) => theme.fg("dim", t) });
  }

  get focused() {
    return this._focused;
  }
  set focused(v: boolean) {
    this._focused = v;
    this.input.focused = v && this.sel === -1 && !this.confirming;
  }

  private items(): Item[] {
    const s = this.state();
    return [
      ...s.draft.map((_, index) => ({ kind: "memory" as const, index })),
      ...this.notes().map((note) => ({ kind: "note" as const, note })),
      ...s.log.slice(-SHOWN_THOUGHTS).reverse().map((t) => ({ kind: "thought" as const, at: t.at })),
    ];
  }

  private notes(): Note[] {
    return this.state().notes.filter((n) => !CLOSED.has(n.mark)).slice(-SHOWN_NOTES).reverse();
  }

  private selected(): Item | undefined {
    return this.sel >= 0 ? this.items()[this.sel] : undefined;
  }

  private move(by: number) {
    const n = this.items().length;
    this.sel = n === 0 ? -1 : Math.max(-1, Math.min(n - 1, this.sel + by));
    this.input.focused = this._focused && this.sel === -1;
  }

  handleInput(data: string): void {
    const is = (key: string) => this.kit.matchesKey(data, key);
    if (this.confirming) {
      if (is("enter") || is("y")) this.act.send();
      if (is("enter") || is("y") || is("escape") || is("n")) this.confirming = false;
      this.input.focused = this._focused && this.sel === -1;
      return;
    }
    if (is("ctrl+s")) {
      if (statusOf(this.state()).send) {
        this.confirming = true;
        this.input.focused = false;
      }
      return;
    }
    const item = this.selected();
    if (item) return this.onItem(item, data);
    if (is("escape")) return this.act.escape();
    if (is("tab")) {
      this.target = this.target === "log" ? "memory" : "log";
      return;
    }
    if (is("up") && this.input.getValue() === "") return this.move(this.items().length);
    if (is("enter")) {
      const text = this.input.getValue();
      if (!text.trim()) return;
      if (this.target === "memory" && this.state().draft.length >= MEMORY_MAX) return;
      this.target === "log" ? this.act.keep(text) : this.act.addMemory(text);
      this.input.setValue("");
      return;
    }
    this.input.handleInput(data);
  }

  private onItem(item: Item, data: string) {
    const is = (key: string) => this.kit.matchesKey(data, key);
    if (is("escape")) return this.move(-this.items().length - 1);
    if (is("up")) return this.move(-1);
    if (is("down")) return this.sel === this.items().length - 1 ? this.move(-this.items().length - 1) : this.move(1);
    const remove = is("x") || is("delete");
    if (item.kind === "memory" && remove) this.act.removeMemory(item.index);
    else if (item.kind === "thought" && remove) this.act.forget(item.at);
    else if (item.kind === "note") {
      if (is("enter")) {
        this.open = this.open === item.note.key ? null : item.note.key;
        if (this.open) this.act.mark(item.note.key, "read");
      } else if (is("k")) this.act.mark(item.note.key, "known");
      else if (is("w")) this.act.mark(item.note.key, "wrong");
      else if (remove) this.act.mark(item.note.key, "dismissed");
      else return;
    } else return;
    this.move(0);
  }

  render(width: number): string[] {
    const { theme: t, kit } = this;
    const w = Math.max(10, width - 2);
    const s = this.state();
    const item = this.selected();
    const out: string[] = [];
    const line = (text = "") => out.push(text);
    const pick = (i: number, text: string) => (this.sel === i ? t.fg("accent", "▸ ") : "  ") + text;
    const head = (label: string, right: string) => {
      line();
      line(`${t.bold(label)}${right ? t.fg("dim", ` · ${right}`) : ""}`);
    };
    let i = 0;

    line(`${t.fg("accent", "◆")} ${t.bold("Binnacle")}${t.fg("dim", this._focused ? "  esc back to the prompt" : "  alt+h")}`);

    const status = statusOf(s);
    head("Memory", s.draft.length ? `${s.draft.length} of ${MEMORY_MAX} lines` : "");
    for (const l of kit.wrapTextWithAnsi(status.tone ? t.fg(status.tone, status.text) : t.fg("dim", status.text), w)) line(l);
    s.draft.forEach((text, n) => line(pick(i++, `${t.fg("dim", `${n + 1}`)} ${text}`)));

    const notes = this.notes();
    if (notes.length) {
      head("Heads-ups", `${notes.length}`);
      for (const n of notes) {
        const mark = n.mark === "read" ? t.fg("dim", "◇ ") : t.fg("warning", "◆ ");
        line(pick(i++, mark + n.line));
        if (this.open === n.key) {
          for (const l of kit.wrapTextWithAnsi(n.details || "(no details)", w - 4)) line(`    ${l}`);
          if (n.evidence) for (const l of kit.wrapTextWithAnsi(t.fg("dim", `From the record: “${n.evidence}”`), w - 4)) line(`    ${l}`);
          line(`    ${t.fg("dim", `${n.how}${n.version ? ` · ${n.version}` : ""}`)}`);
        }
      }
    }

    if (s.log.length) {
      head("Log", `${s.log.length} kept`);
      for (const th of s.log.slice(-SHOWN_THOUGHTS).reverse()) line(pick(i++, `${t.fg("dim", hhmm(th.at))} ${th.text}`));
    }

    line();
    if (this.confirming) {
      line(t.fg("warning", `Send ${s.draft.length} Memory lines to the agent's instructions? It keeps them until you send again.`));
      line(t.fg("dim", "enter yes · esc no"));
    } else {
      const prompt = this.target === "log" ? t.fg("accent", "log › ") : t.fg("success", "memory › ");
      const field = this.input.render(Math.max(4, w - 10))[0] ?? "";
      line(prompt + field);
      line(t.fg("dim", this.keys(item)));
    }
    return out.map((l) => kit.truncateToWidth(` ${l}`, width, "…", true));
  }

  private keys(item: Item | undefined): string {
    if (!this._focused) return "alt+h to type here";
    if (item?.kind === "memory") return "x remove · ↑↓ move · esc field";
    if (item?.kind === "thought") return "x forget · ↑↓ move · esc field";
    if (item?.kind === "note") return "enter details · k I knew this · w wrong · x dismiss · esc field";
    const keep = this.target === "log" ? "enter keep" : "enter add to Memory";
    const send = statusOf(this.state()).send ? " · ctrl+s send Memory" : "";
    return `${keep} · tab ${this.target === "log" ? "Memory" : "Log"} · ↑ items${send} · esc prompt`;
  }

  invalidate(): void {}
}
