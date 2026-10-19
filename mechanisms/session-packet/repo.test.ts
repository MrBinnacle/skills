import { describe, expect, test } from "bun:test";
import { extract } from "./packet";
import { type Exec, validateCloseCommit, validateRepository, validateUnclaimedHead } from "./repo";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fixture, makeRepo, nodeExec } from "./testkit";

async function cleanAt(root: string, head: string) {
  const m = extract(fixture("fixture-clean.md"));
  m.repository = { ...m.repository, root, head, branch: "main" };
  return m;
}

describe("validateRepository (real git repo)", () => {
  test("a packet matching branch, HEAD and its path probe holds", async () => {
    const { root, head } = await makeRepo();
    const result = await validateRepository({ data: await cleanAt(root, head), repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual([]);
  });

  test("a stale HEAD is rejected", async () => {
    const { root } = await makeRepo();
    const result = await validateRepository({ data: extract(fixture("fixture-stale.md")), repoRoot: root, exec: nodeExec });
    expect(result.errors.some((e) => e.startsWith("stale HEAD: packet=deadbeef"))).toBe(true);
  });

  test("branch drift is rejected", async () => {
    const { root, head } = await makeRepo();
    const m = await cleanAt(root, head);
    m.repository.branch = "feature";
    const result = await validateRepository({ data: m, repoRoot: root, exec: nodeExec });
    expect(result.errors).toContain("branch drift: packet=feature current=main");
  });

  test("a verified path probe for a missing path is rejected", async () => {
    const { root, head } = await makeRepo();
    const m = extract(fixture("fixture-failed-probe.md"));
    m.repository = { ...m.repository, head };
    const result = await validateRepository({ data: m, repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual(["claim C001 path probe failed: does-not-exist"]);
  });

  test("a verified commit probe must name a commit in the repository", async () => {
    const { root, head } = await makeRepo();
    const m = await cleanAt(root, head);
    const commitClaim = (id: string, value: string) => ({ id, text: "t", status: "verified", probe: { kind: "commit", value }, evidence: "e" });
    m.claims = [commitClaim("C001", head), commitClaim("C002", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")];
    const result = await validateRepository({ data: m, repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual(["claim C002 commit probe failed: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"]);
  });

  test("an unverified claim's probe is not run", async () => {
    const { root, head } = await makeRepo();
    const m = await cleanAt(root, head);
    m.claims = [{ id: "C001", text: "t", status: "unverified", probe: { kind: "path", value: "nope" }, evidence: "hearsay" }];
    expect((await validateRepository({ data: m, repoRoot: root, exec: nodeExec })).errors).toEqual([]);
  });

  describe("command probes", () => {
    const withProbe = async (command: string) => {
      const { root, head } = await makeRepo();
      const m = await cleanAt(root, head);
      m.claims = [{ id: "C001", text: "the suite passes", status: "verified", probe: { kind: "command", value: command }, evidence: "observed" }];
      return { root, m };
    };
    const recording = () => {
      const calls: string[][] = [];
      const exec: Exec = (cmd, args, opts) => {
        calls.push([cmd, ...args]);
        return nodeExec(cmd, args, opts);
      };
      return { calls, exec };
    };

    test("a command that reaches the receiver only through the packet is rejected and never executed", async () => {
      const { root, m } = await withProbe("echo pwned > pwned.txt");
      const { calls, exec } = recording();
      const result = await validateRepository({ data: m, repoRoot: root, exec });
      expect(result.errors.some((e) => e.includes("absent from the trusted config allowlist"))).toBe(true);
      expect(calls.some((c) => c.join(" ").includes("pwned"))).toBe(false);
      expect(existsSync(join(root, "pwned.txt"))).toBe(false);
    });

    test("an allowlisted command probe that fails is rejected with its exit code", async () => {
      const { root, m } = await withProbe("exit 3");
      const result = await validateRepository({ data: m, repoRoot: root, exec: nodeExec, allowedCommands: ["exit 3"] });
      expect(result.errors).toEqual(["claim C001 command probe failed (exit 3): exit 3"]);
    });

    test("an allowlisted command probe that passes is noted", async () => {
      const { root, m } = await withProbe("git rev-parse HEAD");
      const result = await validateRepository({ data: m, repoRoot: root, exec: nodeExec, allowedCommands: ["git rev-parse HEAD"] });
      expect(result.errors).toEqual([]);
      expect(result.notes).toEqual(["claim C001 command probe passed: git rev-parse HEAD"]);
    });
  });

  describe("status_porcelain", () => {
    test("an uncommitted change the packet did not record is status drift", async () => {
      const { root, head } = await makeRepo();
      writeFileSync(join(root, "README.md"), "edited after the close");
      const result = await validateRepository({ data: await cleanAt(root, head), repoRoot: root, exec: nodeExec });
      expect(result.errors).toEqual(["status drift: packet='' current='M README.md'"]);
    });

    test("files under the packet directory are not drift: the packet cannot record itself", async () => {
      const { root, head } = await makeRepo();
      mkdirSync(join(root, ".pi", "session-packets"), { recursive: true });
      writeFileSync(join(root, ".pi", "session-packets", "p.md"), "x");
      const result = await validateRepository({
        data: await cleanAt(root, head), repoRoot: root, exec: nodeExec, packetDir: ".pi/session-packets",
      });
      expect(result.errors).toEqual([]);
    });
  });
});

describe("validateCloseCommit", () => {
  test("HEAD without the configured marker is not the close commit", async () => {
    const { root } = await makeRepo("ordinary work, no ritual line");
    const errors = await validateCloseCommit({ closeCommit: { contains: "RITUAL:" }, repoRoot: root, exec: nodeExec });
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain("HEAD is not the close commit");
  });

  test("`contains` is a literal substring, not a regex", async () => {
    const { root } = await makeRepo("chore(state): close\n\nRITUAL: retro+1");
    expect(await validateCloseCommit({ closeCommit: { contains: "^RITUAL:" }, repoRoot: root, exec: nodeExec })).toHaveLength(1);
    expect(await validateCloseCommit({ closeCommit: { contains: "RITUAL:" }, repoRoot: root, exec: nodeExec })).toEqual([]);
  });

  test("no closeCommit configured: the check is off", async () => {
    const { root } = await makeRepo("ordinary");
    expect(await validateCloseCommit({ closeCommit: undefined, repoRoot: root, exec: nodeExec })).toEqual([]);
  });
});

describe("validateUnclaimedHead", () => {
  const prior = (dir: string, name: string, head: string) => {
    writeFileSync(join(dir, name), `<!-- SESSION-PACKET-V1\n${JSON.stringify({ repository: { head } })}\nSESSION-PACKET-V1 -->\n`);
    return name;
  };
  const setup = async () => {
    const { root, head } = await makeRepo();
    const dir = join(root, "packets");
    mkdirSync(dir);
    const own = join(root, "new-packet.md");
    const check = (packetPath = own) => validateUnclaimedHead({ repoRoot: root, packetDir: "packets", packetPath, exec: nodeExec });
    return { root, head, dir, check };
  };

  test("an empty or missing packet directory lets the first packet through", async () => {
    const { check } = await setup();
    expect(await check()).toEqual([]);
  });

  test("a HEAD the newest prior packet claims is refused, naming the HEAD and the packet", async () => {
    const { head, dir, check } = await setup();
    const name = prior(dir, "20260101T000000Z-aaaa.md", head);
    const errors = await check();
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain(`HEAD ${head} is already claimed by prior packet ${name}`);
  });

  test("stray, non-object and headless files are walked past to the newest real prior", async () => {
    const { head, dir, check } = await setup();
    const name = prior(dir, "20260102T000000Z-bbbb.md", head);
    writeFileSync(join(dir, "README.md"), "no markers here");
    writeFileSync(join(dir, "20260103T000000Z-cccc.md"), "<!-- SESSION-PACKET-V1\n[1, 2]\nSESSION-PACKET-V1 -->\n");
    writeFileSync(join(dir, "20260104T000000Z-dddd.md"), '<!-- SESSION-PACKET-V1\n{"repository": {}}\nSESSION-PACKET-V1 -->\n');
    expect((await check())[0]).toContain(name);
  });

  test("an older prior claiming HEAD does not refuse once a newer prior claims another HEAD", async () => {
    const { head, dir, check } = await setup();
    prior(dir, "20260101T000000Z-aaaa.md", head);
    prior(dir, "20260102T000000Z-bbbb.md", "0".repeat(40));
    expect(await check()).toEqual([]);
  });

  test("the packet under validation does not refuse itself", async () => {
    const { head, dir, check } = await setup();
    const own = join(dir, prior(dir, "20260105T000000Z-eeee.md", head));
    expect(await check(own)).toEqual([]);
  });
});
