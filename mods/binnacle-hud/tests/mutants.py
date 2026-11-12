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
    # Memory across a compaction
    "replay skips a subagent's compaction": [("if (e.agentId || e.trigger", "if (e.trigger")],
    "replay skips a precompute": [("e.agentId || e.trigger === 'precompute' || ", "e.agentId || ")],
    "replay reads the snapshot after the summary": [
        ("    const out = await next(e)\n    if (e.agentId || e.trigger", "    const early = await read($, approved)\n    const out = await next(e)\n    if (e.agentId || e.trigger"),
        ("const snap = await read($, approved)\n    if (!snap ||", "const snap = early\n    if (!snap ||")],
    "replay row is built whole": [("text: memoryText(snap), toolUses: [] }", "text: memoryText(snap) }")],
    "replay skips a Send the HUD could not record": [("if (!snap || (await read($, view)).unrecorded) return out", "if (!snap) return out")],
    "watcher ignores subagent rows": [("if (e.agentId || !row) return out", "if (!row) return out")],
    "the boundary starts the check": [("state: 'checking' as const", "state: 'found' as const")],
    "only the boundary starts the check": [("row.name === 'compact_boundary'", "row.type === 'system'")],
    "the boundary clears the unrecorded notice": [("      await update($, view, v => ({ ...v, unrecorded: 0 })).catch(() => undefined)\n", "")],
    "the watcher reads the row as stored": [("const row = out.message\n", "const row = out.deny ? undefined : e.message\n")],
    "check moves only while checking": [("att.state !== 'checking' ? att", "false ? att")],
    "check finds the row by its text": [("textOf(row) === att.text", "false")],
    "check concludes missing on a prompt": [("door === 'prompt' || door === 'response'", "door === 'response'")],
    "check concludes missing on a response": [("door === 'prompt' || door === 'response'", "door === 'prompt'")],
    "replay speaks only for its Send": [("att.approvedAt === snap.at ? att :", "true ? att :")],
    "unchecked replay claims nothing": [("replay?.state === 'checking' ?", "false ?")],
    "unchecked replay is drawn quietly": [("Not checked after the compaction at ${at}.`, null)", "Not checked after the compaction at ${at}.`, 'remember')")],
    "Send offered when the replay was lost": [("const send = changed || replay?.state === 'missing'", "const send = changed")],
    "a lost replay is a warning": [("Send again to give Claude these lines.`, 'warning')", "Send again to give Claude these lines.`, 'claude')")],
    "changed lines beat a found replay": [("    : changed ? said(", "    : false ? said(")],
    "a later check that replayed an older Send speaks for this one": [("att.at >= snap.at ? { ...att, state: 'missing' } : null", "null")],
    "a same-millisecond check is not a check before the Send": [("att.at >= snap.at ?", "att.at > snap.at ?")],
    "an open check outranks changed lines": [
        ("    : replay?.state === 'checking' ? said(", "    : changed ? said(`Changed since Send. Claude has the ${hhmm(snap.at)} version.`, 'claude')\n    : replay?.state === 'checking' ? said(")],
    "status colour comes from the status": [("color={said.tone ? TONE[said.tone] : undefined}", "color={snap ? TONE.remember : undefined}")],
    "a quiet status is dimmed": [("dimColor={!said.tone}", "dimColor={false}")],
    "a refusal after a lost replay is drawn": [("const claudeHasThem = !said.send", "const claudeHasThem = !!snap && same(lines, snap.lines)")],
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
