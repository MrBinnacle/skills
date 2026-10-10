import { describe, expect, test } from "bun:test";
import { extract, lintReceiverChecks, validateRecordedChecks, validateStructure } from "./packet";
import { fixture, renderPacket } from "./testkit";

describe("extract", () => {
  test("reads the hidden manifest", () => {
    expect(extract(fixture("fixture-clean.md")).packet_id).toBe("clean-1");
  });

  test("absent or out-of-order markers are a packet error", () => {
    expect(() => extract("## Narrative only")).toThrow("markers are absent or out of order");
    expect(() => extract("SESSION-PACKET-V1 --> {} <!-- SESSION-PACKET-V1")).toThrow("out of order");
  });

  test("invalid JSON is a packet error", () => {
    expect(() => extract("<!-- SESSION-PACKET-V1\n{nope\nSESSION-PACKET-V1 -->")).toThrow("not valid JSON");
  });
});

describe("validateStructure", () => {
  const check = (text: string) => validateStructure(extract(text), text);

  test("the clean fixture has no structure errors", () => {
    expect(check(fixture("fixture-clean.md"))).toEqual([]);
  });

  test("a missing required field is named", () => {
    expect(check(fixture("fixture-missing-field.md"))).toContain("missing field: objective");
  });
});

describe("validateStructure field rules", () => {
  const clean = () => extract(fixture("fixture-clean.md"));
  const claim = (over: Record<string, unknown>) => (m: any) => {
    m.claims = [{ id: "C001", text: "t", status: "verified", probe: { kind: "path", value: "README.md" }, evidence: "e", ...over }];
  };
  const cases: [string, (m: any) => void, string][] = [
    ["empty objective", (m) => (m.objective = ""), "empty field: objective"],
    ["empty packet_id", (m) => (m.packet_id = ""), "empty field: packet_id"],
    ["wrong version", (m) => (m.packet_version = 1), "packet_version must equal 1"],
    ["bad timestamp", (m) => (m.created_at = "yesterday"), "created_at must be ISO-8601"],
    ["no repository head", (m) => delete m.repository.head, "missing repository field: head"],
    ["no porcelain field", (m) => delete m.repository.status_porcelain, "missing repository field: status_porcelain"],
    ["empty next_action task", (m) => (m.next_action.task = ""), "empty next_action field: task"],
    ["unlabelled skills source", (m) => (m.skills_dispatched.source = "memory"), "skills_dispatched.source must be telemetry or model-reported"],
    ["skills items not array", (m) => (m.skills_dispatched.items = "x"), "skills_dispatched.items must be an array"],
    ["test lacks head", (m) => delete m.tests[0].head, "tests[0] lacks head"],
    ["exit code not integer", (m) => (m.tests[0].exit_code = "0"), "tests[0].exit_code must be an integer"],
    ["exit code fractional", (m) => (m.tests[0].exit_code = 0.5), "tests[0].exit_code must be an integer"],
    ["claim status invalid", claim({ status: "probably" }), "claims[0].status is invalid"],
    ["claim lacks text", claim({ text: "" }), "claims[0] lacks id or text"],
    ["verified claim untyped probe", claim({ probe: { kind: "vibes", value: "x" } }), "claims[0] lacks a typed probe"],
    ["verified claim no evidence", claim({ evidence: "" }), "claims[0] lacks evidence"],
    ["unverified claim no source", claim({ status: "unverified", probe: undefined, evidence: "" }), "claims[0] lacks a source in evidence"],
  ];
  test.each(cases)("%s is rejected", (_name, mutate, expected) => {
    const m = clean();
    mutate(m);
    const text = renderPacket(m);
    expect(validateStructure(m, text)).toContain(expected);
  });

  test("an unverified claim with a source passes", () => {
    const m = clean();
    claim({ status: "unverified", probe: undefined, evidence: "operator said so" })(m);
    expect(validateStructure(m, renderPacket(m))).toEqual([]);
  });

  test("a missing narrative section is named", () => {
    const text = fixture("fixture-clean.md").replace("## What We Tried", "## Tried");
    expect(validateStructure(extract(text), text)).toContain("missing narrative section: ## What We Tried");
  });

  test("a possible secret is rejected", () => {
    const text = fixture("fixture-clean.md") + "\nkey ghp_abcdefghijklmnopqrstuvwxyz0123\n";
    expect(validateStructure(extract(text), text)).toContain("possible secret detected");
  });
});

describe("placeholder detection", () => {
  const text = fixture("fixture-clean.md");
  const errorsFor = (t: string, m = extract(t)) => validateStructure(m, t);

  test("a TODO mentioned inside prose is content, not a placeholder", () => {
    expect(errorsFor(text + "\nClosed the ticket titled 'sweep the remaining TODO comments'.\n")).toEqual([]);
  });

  test.each(["TODO", "  TBD  ", "- TODO:", "**TODO**", "1. TBD."])("a whole-line placeholder %p is rejected", (line) => {
    const errors = errorsFor(`${text}\n${line}\n`);
    expect(errors.some((e) => e.startsWith("unfinished marker present: T"))).toBe(true);
  });

  test("a manifest value that is only a placeholder token is rejected", () => {
    const m = extract(text);
    m.objective = "TBD";
    expect(validateStructure(m, text)).toContain("unfinished marker present: TBD");
  });

  test("the scaffold marker is rejected wherever it appears", () => {
    expect(errorsFor(text + "\nsee __REQUIRED__ here\n")).toContain("unfinished marker present: __REQUIRED__");
  });
});

describe("validateRecordedChecks", () => {
  test("a manifest recording a red receiver check names the failing entry", () => {
    const errors = validateRecordedChecks(extract(fixture("fixture-red-check.md")));
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain("recorded receiver check failed: tests[1] exited 1: python test_guard.py");
  });

  test("all-green tests[] passes", () => {
    expect(validateRecordedChecks(extract(fixture("fixture-clean.md")))).toEqual([]);
  });
});

describe("lintReceiverChecks", () => {
  test("a check that always exits zero is named as unfailable", () => {
    const notes = lintReceiverChecks([{ name: "git-status", command: "git status --porcelain" }]);
    expect(notes).toHaveLength(1);
    expect(notes[0]).toContain("receiver check 'git-status' always exits zero");
  });

  test("a check that can fail is not flagged", () => {
    expect(lintReceiverChecks([{ name: "clean-tree", command: "git diff --quiet && git diff --cached --quiet" }])).toEqual([]);
  });
});
