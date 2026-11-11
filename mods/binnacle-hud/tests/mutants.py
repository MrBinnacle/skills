"""Break each guard in hooks/register.tsx once and require the plugin tests to go red.

Run: python mods/binnacle-hud/tests/mutants.py [name ...]
Exit 0 only when every named mutant applies exactly once and turns the suite red.
Exit 3, before any mutant, when the unmutated suite is already red.
A mutant whose text no longer matches the source fails too: fix its row when the code moves.
The source file is restored after every run, also on error or Ctrl+C.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "hooks" / "register.tsx"

# name -> list of (find, replace); each find must occur exactly once.
MUTANTS = {
    # Send record and failed keeps (#665)
    "snapshot write failure caught": [(".catch(() => { unrecorded = at })", "")],
    "refused Send keeps earlier notice": [("unrecorded: out.deny ? v.unrecorded : unrecorded", "unrecorded")],
    "dismiss drops only the drawn ids": [("without(unsaved.flatMap(f => f.id ?? []))", "() => []")],
    "d shown only when something failed": [("...(unsaved.some(f => f.id) ? [{ k: 'd'", "...(true ? [{ k: 'd'")],
    "d needs an entry with an id": [("...(unsaved.some(f => f.id) ? [{ k: 'd'", "...(unsaved.length ? [{ k: 'd'")],
    "entry id is minted, not its text": [("({ id: crypto.randomUUID(), text })", "({ id: text, text })")],
    "bare string gets no id": [("{ id: null, text: s }", "{ id: s, text: s }")],
    "bare string keeps its text": [("{ id: null, text: s }", "{ id: null, text: '' }")],
    "start mints a 4.1.0 Memory": [("    if ((await read($, draft)).some(s => typeof s === 'string')) await update($, draft, minted).catch(() => undefined)\n", "")],
    "start mints 4.1.0 failed keeps": [("    if ((await read($, failed)).some(s => typeof s === 'string')) await update($, failed, minted).catch(() => undefined)\n", "")],
    "remove acts on the drawn entry": [("without([id])", "without([rows[0]!.id!])")],
    "remove matches by id, not text": [("saved.filter(s => typeof s === 'string' || !ids.includes(s.id))",
                                        "saved.filter(s => typeof s === 'string' || !saved.some(x => typeof x !== 'string' && ids.includes(x.id) && x.text === s.text))")],
    "p copies the thought on screen": [("promote($, newest)", "read($, kept).then(k => promote($, k.at(-1)!.text))")],
    "remove last acts on the drawn last": [("without([last])", "without([rows[0]!.id!])")],
    "0 targets the line shown last": [("rows.at(-1)?.id", "rows.findLast(r => r.id)?.id")],
    # Refusal wording and the stale-refusal draw (#666)
    "dock shows notice beside refusal": [("!(refused && !snap && !st.unrecorded)", "!(refused && !snap)")],
    "strip refusal wording": [("(st.unrecorded ? `${status} The later Send was refused: ${refused}` : `Not sent. ${refused}`)",
                               "`Not sent. ${refused}`")],
    "dock refusal wording": [("st.unrecorded ? `The later Send was refused: ${refused}` : `Not sent. ${refused}`",
                              "`Not sent. ${refused}`")],
    "refusal hidden once lines match the snapshot": [("besideRefused && !claudeHasThem", "besideRefused")],
    # A refusal is drawn only beside the lines it refused
    "refusal bound to its lines": [("!!st.refusedLines && same(lines, st.refusedLines)", "true")],
    "a refusal without lines is not drawn": [("!!st.refusedLines && same(lines, st.refusedLines)", "same(lines, st.refusedLines ?? [])")],
    "Send records the refused lines": [("refusedLines: lines,", "refusedLines: undefined,")],
    "a adds the drawn text": [("run: () => addLine($, now) }", "run: () => read($, typed).then(t => addLine($, t)) }")],
    # Memory across a compaction (M2)
    "replay skips a subagent's compaction": [("if (e.agentId || e.trigger", "if (e.trigger")],
    "replay skips a precompute": [("e.agentId || e.trigger === 'precompute' || ", "e.agentId || ")],
    "replay skips a skipped compaction": [(" || !out.messages) return out", ") return out")],
    "replay reads the snapshot after the summary": [
        ("    const out = await next(e)\n    if (e.agentId || e.trigger", "    const early = await read($, approved)\n    const out = await next(e)\n    if (e.agentId || e.trigger"),
        ("const snap = await read($, approved)\n    if (!snap) return out", "const snap = early\n    if (!snap) return out")],
    "replay adds no second row": [("out.messages.some(m => m.text === text)", "false")],
    "replay row is built whole": [("text, toolUses: [] }", "text }")],
    "watcher ignores subagent rows": [("e.agentId ? null : ", "")],
    "check starts at the boundary": [("row.message.name === 'compact_boundary'", "true")],
    "check moves only while checking": [("att.state !== 'checking' ? att", "false ? att")],
    "check finds the row by its text": [("textOf(row) === att.text", "false")],
    "check concludes missing on a prompt or response": [("row.door === 'prompt' || row.door === 'response'", "false")],
    "replay speaks only for its Send": [("att?.approvedAt === snap.at ? att : null", "att")],
    "unchecked replay claims nothing": [("replay && replay.state !== 'found' ?", "false ?")],
    "Send offered when the replay was lost": [("(lost || !(snap && same(lines, snap.lines)))", "(!(snap && same(lines, snap.lines)))")],
}


def run_tests() -> tuple[int, list[str]]:
    out = subprocess.run("claude plugin test .", cwd=ROOT, shell=True, capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    fails = [line[7:70] for line in (out.stdout + out.stderr).splitlines() if line.startswith("(fail)")]
    return out.returncode, fails


def main(names: list[str]) -> int:
    unknown = [n for n in names if n not in MUTANTS]
    if unknown:
        print("unknown mutant(s):", ", ".join(unknown))
        return 2
    original = SOURCE.read_text(encoding="utf-8")
    code, fails = run_tests()
    if code:
        print("baseline is red, no mutant run:", "; ".join(fails[:3]))
        return 3
    bad = 0
    try:
        for name in names or list(MUTANTS):
            source = original
            for find, replace in MUTANTS[name]:
                if source.count(find) != 1:
                    print(f"MISSING {name}: found {source.count(find)} times: {find[:50]!r}")
                    bad += 1
                    break
                source = source.replace(find, replace)
            else:
                SOURCE.write_text(source, encoding="utf-8", newline="\n")
                code, fails = run_tests()
                print(("RED  " if code else "ALIVE"), name, "|", "; ".join(fails[:2]), flush=True)
                bad += code == 0
    finally:
        SOURCE.write_text(original, encoding="utf-8", newline="\n")
    print("survivors or missing:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
