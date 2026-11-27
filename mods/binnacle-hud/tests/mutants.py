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
    "start mints a 4.1.0 Memory": [("    if ((await read($, draft).catch(() => [])).some(s => typeof s === 'string')) await update($, draft, minted).catch(() => undefined)\n", "")],
    "start mints 4.1.0 failed keeps": [("    if ((await read($, failed).catch(() => [])).some(s => typeof s === 'string')) await update($, failed, minted).catch(() => undefined)\n", "")],
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
    "refusal hidden once lines match the snapshot": [("besideRefused && !sentThem", "besideRefused")],
    # A refusal is drawn only beside the lines it refused
    "refusal bound to its lines": [("!!st.refusedLines && same(lines, st.refusedLines)", "true")],
    "a refusal without lines is not drawn": [("!!st.refusedLines && same(lines, st.refusedLines)", "same(lines, st.refusedLines ?? [])")],
    "Send records the refused lines": [("refusedLines: lines }", "refusedLines: undefined }")],
    "a adds the drawn text": [("run: () => addLine($, now) }", "run: () => read($, typed).then(t => addLine($, t)) }")],
    # Memory in Claude's system prompt
    "the section joins only Claude Code's memory section": [("on('prompt.section', { name: 'memory' },", "on('prompt.section',")],
    "the section keeps the engine's text": [("[out.text, memoryText(snap)]", "[memoryText(snap)]")],
    "the section drops an absent engine text": [("[out.text, memoryText(snap)].filter(Boolean).join", "[out.text, memoryText(snap)].join")],
    "a changed section breaks the cache": [("breakPromptCache: true }", "breakPromptCache: false }")],
    "no Send leaves the section as the engine wrote it": [("if (!snap) return out", "if (!snap) return { ...out, breakPromptCache: true }")],
    # The hook's record of what the section carried
    "the hook records what it carried": [("    await update($, delivered,", "    if (false) await update($, delivered,")],
    "a failed record does not fail the hook": [("{ at: snap.at, since }).catch(() => undefined)", "{ at: snap.at, since })")],
    "the record names the Send it carried": [("{ at: snap.at, since })", "{ at: since, since })")],
    "a re-ask keeps the first time": [("now && now.at >= snap.at ? now :", "now && now.at > snap.at ? now :")],
    "a late ask keeps a newer record": [("now && now.at >= snap.at ? now :", "now && now.at === snap.at ? now :")],
    "the pane reads the record": [("statusOf(lines, snap, await read($, delivered))", "statusOf(lines, snap, null)")],
    "Send drops the cached section": [("  if (!refusal) $.ui.invalidate('prompt.section')\n", "")],
    "a refused Send leaves the cached section": [("if (!refusal) $.ui.invalidate('prompt.section')", "$.ui.invalidate('prompt.section')")],
    "Send drops prompt sections, not a drawing": [("$.ui.invalidate('prompt.section')", "$.ui.invalidate('ui.render')")],
    # The status line
    "nothing sent offers Send": [("tone: null, send: true", "tone: null, send: false")],
    "changed lines say Changed since Send": [("if (!same(lines, snap.lines)) return", "if (false) return")],
    "only the record says Claude has a Send": [("const arrived = seen?.at === snap.at", "const arrived = true")],
    "an earlier Send's record is not this Send's": [("const arrived = seen?.at === snap.at", "const arrived = !!seen")],
    "changed lines not yet carried never say Claude has them": [("if (!same(lines, snap.lines)) return arrived", "if (!same(lines, snap.lines)) return true")],
    "since is when the section carried it": [("since ${hhmm(seen.since)}", "since ${hhmm(snap.at)}")],
    "changed lines Claude has offer Send": [("version.`, tone: 'claude', send: true", "version.`, tone: 'claude', send: false")],
    "changed lines not yet carried offer Send": [("instructions.`, tone: 'claude', send: true", "instructions.`, tone: 'claude', send: false")],
    "lines Claude has offer no Send": [("tone: 'remember', send: false", "tone: 'remember', send: true")],
    "a pending Send is quiet": [("tone: null, send: false", "tone: 'remember', send: false")],
    "a pending Send offers no Send": [("tone: null, send: false", "tone: null, send: true")],
    "status colour comes from the status": [("color={said.tone ? TONE[said.tone] : undefined}", "color={snap ? TONE.remember : undefined}")],
    "a quiet status is dimmed": [("dimColor={!said.tone}", "dimColor={false}")],
    # The strip after Watch left
    "strip keys are m and l": [("toggle(2, 'l', 'log')", "toggle(2, 'w', 'log')")],
    # Heads-ups from the built-in side agent
    "only a built-in's store write counts": [("next.origin.tier !== 'builtin' || ", "")],
    "only the side agent's store write counts": [("next.origin.plugin !== SIDE || ", "")],
    "only this session's offer": [("s => isRecord(s) && s.id === sessionId", "s => isRecord(s)")],
    "a key must be a turn id": [("|| !KEY.test(row.offeredTurn)) return null", ") return null")],
    "only an offer view is taken": [("v.kind !== 'offer' || ", "")],
    "a listed note is taken once": [("if (now.list.some(n => n.key === found.key)) return now", "if (false) return now")],
    "one own turn until the person speaks": [("free: now.free && !own }", "free: now.free }")],
    "the person's message frees the turn": [("cur => ({ free: true, list:", "cur => ({ free: cur.free, list:")],
    "a slash command carries nothing": [(" || e.text.startsWith('/')) return next(e)", ") return next(e)")],
    "a refused turn leaves the note waiting": [("sent.drop === undefined ? 'own turn' : 'waiting'", "'own turn'")],
    "a pending turn has no receipt": [("how: own ? 'unconfirmed' : 'waiting'", "how: own ? 'own turn' : 'waiting'")],
    "waiting notes ride as context": [("...waiting.map(quoted)] } : e)", "] } : e)")],
    "only a listed note's row leaves the band": [("r.plugin === SIDE && lines.includes(headline(r.tree))", "r.plugin === SIDE")],
    "brackets and separators are escaped": [(r"/[<>&`\u0085\u2028\u2029]/g", "/[&]/g")],
    "details are cleaned": [("clean(v.explanation, 2000)", "v.explanation")],
    "an empty line is not taken": [("return line ? { key:", "return true ? { key:")],
    "the line is cut at 280": [("clean(v.line, 280)", "clean(v.line, 300)")],
    "only a side-agent row leaves the band": [("r.plugin === SIDE && lines.includes(", "lines.includes(")],
    "a row leaves only on an exact headline": [("lines.includes(headline(r.tree))", "lines.some(l => headline(r.tree).includes(l))")],
    "the headline skips buttons": [("tree.type === 'Button' || ", "")],
    "only the sessions key is read": [(" || e.key !== 'sessions') return result", ") return result")],
    "a phone message carries notes": [("(from !== 'composer' && from !== 'bridge')", "(from !== 'composer')")],
    "the list is capped": [(".slice(-MAX_NOTES)", "")],
    "a retried capture resets own": [("        own = false\n        if (now.list", "        if (now.list")],
    "the headline skips opened details": [(" || tree.type === 'Markdown') return ''", ") return ''")],
    "a failed submit counts as refused": [("quoted(found) }).catch(() => ({ drop: 'failed' }))", "quoted(found) })")],
    "details are cut at 2000": [("clean(v.explanation, 2000)", "clean(v.explanation, 2100)")],
    "a message that changes nothing writes nothing": [("if (!waiting.length && now.free) return next(e)", "if (false) return next(e)")],
    "a dropped message leaves notes waiting": [("    if (result.drop !== undefined) return result\n    const keys", "    const keys")],
    "only the carried notes are marked sent": [("keys.includes(n.key) && n.how === 'waiting'", "n.how === 'waiting'")],
    "a free turn with a note waiting still carries it": [("if (!waiting.length && now.free) return next(e)", "if (now.free) return next(e)")],
    "hidden characters go before NFKC": [(r"const once = text.replace(/\s/g, ' ').replace(HIDDEN, '')", r"const once = text.replace(/\s/g, ' ')")],
    "strip opens the Log at 2": [("st.expand === 2 ? log", "st.expand === 3 ? log")],
    "docked heads-up details stop at three lines": [("<Text wrap=\"wrap\" maxLines={inline ? undefined : rowLines}>{n.explanation}", "<Text wrap=\"wrap\">{n.explanation}")],
    "strip heads-up details are whole": [("maxLines={inline ? undefined : rowLines}>{n.explanation}", "maxLines={rowLines}>{n.explanation}")],
    # PR 688 verifier rows, and the migration reads before the registers
    "the pane redraws once the version is known": [("    if (rowLines) $.ui.invalidate('ui.render')\n", "")],
    "the release base decides maxLines": [("takesMaxLines(v.base ?? v.version)", "takesMaxLines(v.version)")],
    "strip Memory rows take no maxLines": [("maxLines={inline ? undefined : rowLines}><Text dimColor>{i + 1}", "maxLines={rowLines}><Text dimColor>{i + 1}")],
    "a failed long keep shows no cut toast": [("  if (saved !== 'kept') return\n  if (isLong(text))", "  if (isLong(text)) $.ui.toast('binnacle-hud kept the first 2000 characters. The rest was dropped.')\n  if (saved !== 'kept') return\n  if (false)")],
    "an unreadable Memory does not skip the registers": [("read($, draft).catch(() => [])", "read($, draft)")],
    "an unreadable failed list does not skip the registers": [("read($, failed).catch(() => [])", "read($, failed)")],
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
