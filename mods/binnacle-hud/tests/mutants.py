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
    "a refused snapshot write is reported": [(".then(() => '', (err: unknown) => err instanceof Error ? err.message : String(err))", ".then(() => '')")],
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
    "status stays beside a refusal when a Send stands": [("!(refused && !snap)", "!refused")],
    "a refusal with no Send says Not sent once": [("!(refused && !snap)", "true")],
    "strip refusal wording": [("`memory ${refused ? `Not sent. ${refused}` : status}`", "`memory ${status}`")],
    "dock refusal wording": [("{`Not sent. ${refused}`}", "{refused}")],
    "refusal hidden once lines match the snapshot": [("besideRefused && !claudeHasThem", "besideRefused")],
    # A refusal is drawn only beside the lines it refused
    "refusal bound to its lines": [("!!st.refusedLines && same(lines, st.refusedLines)", "true")],
    "a refusal without lines is not drawn": [("!!st.refusedLines && same(lines, st.refusedLines)", "same(lines, st.refusedLines ?? [])")],
    "Send records the refused lines": [("refusedLines: lines }", "refusedLines: undefined }")],
    "a adds the drawn text": [("run: () => addLine($, now) }", "run: () => read($, typed).then(t => addLine($, t)) }")],
    # Memory in Claude's system prompt
    "the section joins only Claude Code's memory section": [("on('prompt.section', { name: 'memory' },", "on('prompt.section',")],
    "the section keeps the engine's text": [("[out.text, memoryText(snap)]", "[memoryText(snap)]")],
    "the section drops an absent engine text": [("[out.text, memoryText(snap)].filter(Boolean).join", "[out.text, memoryText(snap)].join")],
    "a changed section breaks the cache": [("breakPromptCache: true } : out", "breakPromptCache: false } : out")],
    "no Send leaves the section as the engine wrote it": [("breakPromptCache: true } : out", "breakPromptCache: true } : { ...out, breakPromptCache: true }")],
    "Send drops the cached section": [("  if (!refusal) $.ui.invalidate('prompt.section')\n", "")],
    "a refused Send leaves the cached section": [("if (!refusal) $.ui.invalidate('prompt.section')", "$.ui.invalidate('prompt.section')")],
    "Send drops prompt sections, not a drawing": [("$.ui.invalidate('prompt.section')", "$.ui.invalidate('ui.render')")],
    # The status line
    "nothing sent offers Send": [("tone: null, send: true", "tone: null, send: false")],
    "changed lines say Changed since Send": [("!same(lines, snap.lines) ?", "false ?")],
    "changed lines offer Send": [("tone: 'claude', send: true", "tone: 'claude', send: false")],
    "lines Claude has offer no Send": [("tone: 'remember', send: false", "tone: 'remember', send: true")],
    "status colour comes from the status": [("color={said.tone ? TONE[said.tone] : undefined}", "color={snap ? TONE.remember : undefined}")],
    "a quiet status is dimmed": [("dimColor={!said.tone}", "dimColor={false}")],
    # The strip after Watch left
    "strip keys are m and l": [("k: 'ml'[n - 1]!", "k: 'mw'[n - 1]!")],
    "strip opens the Log at 2": [("st.expand === 2 ? log", "st.expand === 3 ? log")],
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
