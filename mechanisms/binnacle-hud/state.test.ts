import { describe, expect, test } from "bun:test";
import { fold, LOG_MAX, records, statusOf, TYPE } from "./state";

const e = (data: unknown, customType = TYPE) => ({ type: "custom", customType, data });

describe("fold", () => {
  test("Log and notes come from every entry; Memory only from the branch", () => {
    const all = [e({ k: "thought", text: "t1", at: 1 }), e({ k: "draft", lines: ["off-branch"] }), e({ k: "note", note: { key: "n", line: "L", how: "for you only" } })];
    const s = fold(all, []);
    expect(s.log.map((t) => t.text)).toEqual(["t1"]);
    expect(s.notes.map((n) => n.key)).toEqual(["n"]);
    expect(s.draft).toEqual([]);
    expect(fold(all, all).draft).toEqual(["off-branch"]);
  });
  test("forget removes a thought; the Log keeps the newest LOG_MAX", () => {
    const many = Array.from({ length: LOG_MAX + 3 }, (_, i) => e({ k: "thought", text: `t${i}`, at: i }));
    const s = fold([...many, e({ k: "forget", at: LOG_MAX + 2 })], []);
    expect(s.log.length).toBe(LOG_MAX - 1);
    expect(s.log[0]!.text).toBe("t3");
  });
  test("how and mark update a note", () => {
    const all = [e({ k: "note", note: { key: "n", line: "L", how: "waits for your next message" } }), e({ k: "how", key: "n", how: "sent with your message" }), e({ k: "mark", key: "n", mark: "read" })];
    expect(fold(all, []).notes[0]).toMatchObject({ how: "sent with your message", mark: "read" });
  });
  test("an empty Send withdraws Memory", () => {
    const branch = [e({ k: "approve", lines: ["a"], at: 1 }), e({ k: "approve", lines: [], at: 2 })];
    expect(fold([], branch).approved).toBeNull();
    expect(fold([], branch.slice(0, 1)).approved).toEqual({ lines: ["a"], at: 1 });
  });
  test("records skip other types and malformed data", () => {
    expect(records([e({ k: "thought", text: 3, at: 1 }), e({ k: "draft", lines: [1] }), e({ k: "thought", text: "x", at: 1 }, "other"), { type: "message" }, e({ k: "nope" })])).toEqual([]);
  });
});

describe("statusOf", () => {
  test("no Send", () => {
    expect(statusOf({ draft: [], approved: null, delivered: null })).toMatchObject({ text: "Empty.", send: false });
    expect(statusOf({ draft: ["a"], approved: null, delivered: null })).toMatchObject({ text: "Not sent.", send: true });
  });
  test("sent but no request has carried it yet", () => {
    expect(statusOf({ draft: ["a"], approved: { lines: ["a"], at: 1 }, delivered: null })).toMatchObject({ tone: null, send: false });
  });
  test("a request carried it", () => {
    const s = statusOf({ draft: ["a"], approved: { lines: ["a"], at: 1 }, delivered: { at: 1, since: 2 } });
    expect(s).toMatchObject({ tone: "success", send: false });
    expect(s.text).toStartWith("In the agent's instructions");
  });
  test("a carried delivery of an older Send does not count", () => {
    expect(statusOf({ draft: ["a"], approved: { lines: ["a"], at: 5 }, delivered: { at: 1, since: 2 } }).tone).toBeNull();
  });
  test("edited after Send", () => {
    expect(statusOf({ draft: ["b"], approved: { lines: ["a"], at: 1 }, delivered: { at: 1, since: 2 } }).text).toStartWith("Changed since Send. The agent has");
    expect(statusOf({ draft: ["b"], approved: { lines: ["a"], at: 1 }, delivered: null }).text).toContain("has not reached the agent");
  });
});
