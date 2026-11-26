import { describe, expect, test } from "bun:test";
import { type Actions, type Kit, Panel } from "./panel";
import { fold, type State } from "./state";

const KEYS: Record<string, string> = { enter: "\r", escape: "\x1b", tab: "\t", up: "\x1b[A", down: "\x1b[B", delete: "\x1b[3~", "ctrl+s": "\x13" };
class FakeInput {
  focused = false;
  private v = "";
  getValue() { return this.v; }
  setValue(v: string) { this.v = v; }
  handleInput(d: string) { if (d.length === 1 && d >= " ") this.v += d; }
  render() { return [this.v]; }
}
const kit: Kit = {
  matchesKey: (d, k) => (KEYS[k] ?? k) === d,
  truncateToWidth: (t, w, _e, pad) => (t.length > w ? t.slice(0, w) : pad ? t.padEnd(w) : t),
  wrapTextWithAnsi: (t, w) => t.match(new RegExp(`.{1,${w}}`, "g")) ?? [""],
  Input: FakeInput as unknown as Kit["Input"],
};
const theme = { fg: (_: string, t: string) => t, bold: (t: string) => t };

function setup(state: Partial<State> = {}) {
  const s: State = { ...fold([], []), ...state };
  const calls: string[] = [];
  const act: Actions = {
    keep: (t) => calls.push(`keep:${t}`), addMemory: (t) => calls.push(`add:${t}`), removeMemory: (i) => calls.push(`remove:${i}`),
    send: () => calls.push("send"), mark: (k, m) => calls.push(`mark:${k}:${m}`), forget: (at) => calls.push(`forget:${at}`),
    escape: () => calls.push("escape"), close: () => calls.push("close"),
  };
  const p = new Panel(kit, theme, () => s, act);
  p.focused = true;
  const type = (...keys: string[]) => keys.forEach((k) => p.handleInput(KEYS[k] ?? k));
  return { p, calls, type };
}
const note = { key: "n1", tag: "heads-up" as const, line: "Skipped test", details: "**Why**", evidence: "npm test was not run", agentKnows: false, at: 1, how: "steered into the run" as const, version: "observer-x" };

describe("panel keys", () => {
  test("enter keeps a thought; tab switches the field to Memory", () => {
    const { calls, type } = setup();
    type("h", "i", "enter", "tab", "m", "enter", "enter");
    expect(calls).toEqual(["keep:hi", "add:m"]);
  });
  test("esc on the field hands the keys back", () => {
    const { calls, type } = setup();
    type("escape");
    expect(calls).toEqual(["escape"]);
  });
  test("a full Memory takes no more lines", () => {
    const { calls, type } = setup({ draft: Array.from({ length: 20 }, (_, i) => `l${i}`) });
    type("tab", "z", "enter");
    expect(calls).toEqual([]);
  });
  test("up reaches items; x removes a Memory line; esc returns to the field", () => {
    const { calls, type } = setup({ draft: ["a", "b"], log: [{ text: "t", at: 7 }] });
    type("up", "x");
    expect(calls).toEqual(["forget:7"]);
    type("up", "x", "escape", "escape");
    expect(calls).toEqual(["forget:7", "remove:1", "escape"]);
  });
  test("on a note: enter opens it and marks it read, k and x mark it", () => {
    const { p, calls, type } = setup({ notes: [note] });
    type("up", "enter");
    expect(p.render(60).join("\n")).toContain("steered into the run");
    type("k", "w", "x");
    expect(calls).toEqual(["mark:n1:read", "mark:n1:known", "mark:n1:wrong", "mark:n1:dismissed"]);
  });
  test("ctrl+s asks first; enter sends, esc does not", () => {
    const a = setup({ draft: ["a"] });
    a.type("ctrl+s", "escape", "ctrl+s", "enter");
    expect(a.calls).toEqual(["send"]);
    const b = setup({ draft: ["a"], approved: { lines: ["a"], at: 1 } });
    b.type("ctrl+s", "enter");
    expect(b.calls).toEqual([]);
  });
});

test("every rendered line fits the width", () => {
  const { p } = setup({ draft: ["x".repeat(300)], notes: [note], log: [{ text: "y".repeat(300), at: 1 }] });
  for (const w of [30, 60, 120]) for (const l of p.render(w)) expect(l.length).toBe(w);
});
