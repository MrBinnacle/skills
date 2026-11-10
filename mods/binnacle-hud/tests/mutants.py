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
    # Draft shadow (#664)
    "late event ignored": [("  if (seen < applied) return\n", "")],
    "newer clear wins a retry": [("now => lossAt === seen ? rec : now", "() => rec")],
    "submit waits for the pending write": [("  await lossWrite\n  await update", "  await update")],
    "skip a clear the submit took": [("sentAt !== seen - 1 && sentAt !== seen && ", "sentAt !== seen - 1 && ")],
    "write assigned before any await": [("    lossWrite = keepLoss($, before, seen)\n",
                                         "    await $.clock.now()\n    lossWrite = keepLoss($, before, seen)\n")],
    "submit-then-clear check": [("sentAt !== seen - 1 && ", "")],
    "submit drops clear-first loss": [("now.load === LOAD && now.moves === at ? null : now", "now")],
    "copy reports refusal": [("out?.isCopied ? 'Copied.", "true ? 'Copied.")],
    "clear-only recording": [("kind === 'clear' && ", "")],
    "slash lines skipped": [("!before.startsWith('/') && ", "")],
    "stash back drops loss": [("now => sameLoss(now, restored) ? null : now", "now => now")],
    # Send record and failed keeps (#665)
    "snapshot write failure caught": [(".catch(() => { unrecorded = at })", "")],
    "refused Send keeps earlier notice": [("unrecorded: out.deny ? v.unrecorded : unrecorded", "unrecorded")],
    "dock shows notice beside refusal": [("!(st.failed && !snap && !st.unrecorded)", "!(st.failed && !snap)")],
    "dismiss drops only the drawn ids": [("without(unsaved.map(f => f.id))", "() => []")],
    "d shown only when something failed": [("...(unsaved.length ? [{ k: 'd'", "...(true ? [{ k: 'd'")],
    "entry id is minted, not its text": [("({ id: crypto.randomUUID(), text })", "({ id: text, text })")],
    "legacy id carries its text": [("`v1-${i}-${s}`", "`v1-${i}`")],
    "legacy line keeps its text": [("{ id: `v1-${i}-${s}`, text: s }", "{ id: `v1-${i}-${s}`, text: '' }")],
    "remove acts on the drawn entry": [("without([r.id])", "without([rows[0]!.id])")],
    "remove last acts on the drawn last": [("without([rows.at(-1)!.id])", "without([rows[0]!.id])")],
    "remove matches by id, not text": [("entries(saved).filter(e => !ids.includes(e.id))",
                                        "entries(saved).filter(e => !entries(saved).some(x => ids.includes(x.id) && x.text === e.text))")],
    "p copies the thought on screen": [("promote($, newest)", "read($, kept).then(k => promote($, k.at(-1)!.text))")],
    # Record identity, paste and wording (#666)
    "submit checks the load": [("now.load === LOAD && now.moves === at", "now.moves === at")],
    "record names its load": [("moves: seen, load: LOAD }", "moves: seen, load: '' }")],
    "paste of copied draft drops row": [("kind === 'edit' ? copiedLoss :", "kind === 'edit' ? null :")],
    "restore or paste drops only its record": [("now => sameLoss(now, restored) ? null : now", "now => now?.text === text ? null : now")],
    "restore needs the read text to match": [("if (restored?.text !== text) return\n", "if (!restored) return\n")],
    "identity checks the load": [("a.load === b.load && a.moves", "a.moves")],
    "identity checks the number": [("a.load === b.load && a.moves === b.moves", "a.load === b.load")],
    "forget checks identity": [("cur => sameLoss(cur, rec) ? null : cur", "() => null")],
    "copy marked only when copied": [("  if (out?.isCopied) copiedLoss = rec\n", "  copiedLoss = rec\n")],
    "only a composer submit drops a loss": [("if (e.origin.kind === 'composer') await submitted($)", "await submitted($)")],
    "copy remembers its record": [("  if (out?.isCopied) copiedLoss = rec\n", "")],
    "strip refusal wording": [("(st.unrecorded ? `${status} The later Send was refused: ${st.failed}` : `Not sent. ${st.failed}`)",
                               "`Not sent. ${st.failed}`")],
    "dock refusal wording": [("st.unrecorded ? `The later Send was refused: ${st.failed}` : `Not sent. ${st.failed}`",
                              "`Not sent. ${st.failed}`")],
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
