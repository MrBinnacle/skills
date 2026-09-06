# gotchas — anti-slop-frontend-secure

Append-only. Each entry is dated and states what happened, then the rule that follows.
Entries below were recorded while building the oracle; none of them is an origin
occurrence for the card, and `EVIDENCE.md` says why that distinction matters here.

---

## [2026-09-06] A sink guard that refused every real call

The blocked-sink pattern was written as `(?<![\w$.])innerHTML(?![\w$])`. The dot in the
lookbehind was meant to refuse `obj.innerHTMLish`. It refuses `node.innerHTML` as well,
which is how the sink is reached in practice, so Gate C passed a document that assigns
straight through it. The failing fixture reported `document.write` and stayed silent
about the `innerHTML` on the line above.

**Rule.** A boundary added to exclude a near-miss has to be checked against the ordinary
case it was not aimed at. The right-hand `(?![\w$])` was already refusing the suffix the
left-hand dot was added for, so the dot bought nothing and cost the gate.

**How it surfaced.** `test_each_fixture_gets_its_stated_verdict` on
`C-fail-sink-in-script`, through `expect_issue_contains`. The fixture failed the gate for
the wrong reason and would have passed a check that only asked whether the gate went red.
Assert which issue, not just that there was one.

---

## [2026-09-06] A parser control that could not see the parser stop working

`test_regex_probe_disagrees_with_the_oracle` compared each probe's naive verdict against
the fixture's DECLARED expectation. A mutation that widened Gate C to read inert
`<script type="text/template">` bodies — turning the gate into a byte scan in everything
but name — left that test green. Only the verdict test caught it.

**Rule.** A control that compares a probe with a declaration is a statement about the
fixture. The claim being made is about the oracle, so the comparison has to reach the
oracle's OBSERVED verdict. Both comparisons are kept now: the declaration catches a
fixture that drifted, the observation catches a gate that stopped parsing.

**Verification.** Five mutations were run by hand against a copy of this folder, and each
was killed by a named assertion rather than by an exit code: the lookbehind above (5
failures), the Gate C scope widening (2), Gate F skipping comments (1), the receipt
claiming an advisory note moved a verdict (2), and the out-of-scope refusal removed (3).

---

## [2026-09-06] A local restatement of a repository gate that cried wolf

`test_every_shipped_file_is_a_declared_readable_format` restates obligation O1 inside the
card. The first edition walked the folder and judged every file. An editor left a
`.mypy_cache/` in the folder and the test went red on a tree the repository gate calls
clean, because `scripts/validate_skill_formats.py` puts the ignore question to git first.

**Rule.** When a card restates a repository check, it restates the whole predicate, git
question included. That script's own docstring records the same failure from the other
side: a guard that cries wolf locally trains its reader to route around the family.

---

## [2026-09-06] The fixtures cannot be HTML files, and that is not a workaround

`SECURITY.md` commitment 3 declares a closed format vocabulary for everything inside a
skill folder: `.md`, `.txt`, `.py`, `.json`. An `.html` fixture is outside it. The bodies
are held as strings in `fixtures.json` and `test_oracle.py` writes each one to a
temporary path before the oracle opens it.

**Rule.** The oracle still parses a real file from a real path, so nothing about the
check is weakened; only the delivery changed. Reach for this shape before reaching for a
relocation or a widened allowlist. An earlier build of this card put eleven `.html`
fixtures and one `.mjs` runner inside the folder and was held at the gate for it.

---

## [2026-09-06] Character references are the whole reason to parse

`html.parser` decodes character references in attribute values whatever
`convert_charrefs` is set to. That is what lets the oracle see a host written
`https:&#x2F;&#x2F;host`, a sink written `inner&#72;TML`, and a key written
`sk_live_&#48;...`, all of which a scan of the file's bytes misses.

**Rule.** Every gate reads decoded values. A gate that reads the raw source loses this
and gains nothing, which is what `fixtures.json`'s `regex_probe` entries measure. Three
of the six gates have a failing fixture that exists only because of this decoding.

---

## [2026-09-06] Void elements and the open-element stack

The tree builder must not push a void element onto the open-element stack. Pushing
`<img>` or `<meta>` reparents everything after it, and the structural gate then reports
shell elements as missing that are present. `VOID_ELEMENTS` in `audit_frontend.py` is the
list; a stray `</p>` is recorded in `parse_errors` and surfaced by Gate A rather than
silently rebalanced.

---

## [2026-09-06] Refusal needs its own exit code

"This is not an HTML artifact" and "this HTML artifact is unsafe" are different answers.
Collapsing both onto exit 1 means a caller reads a refusal as a defect; collapsing
refusal onto 0 means a caller reads it as a clean bill. `audit_frontend.py` exits 3 on
refusal, and the receipt states `verdict: REFUSED` with `gates_run: 0` so a reader can
tell that no gate was evaluated.

---

## [2026-09-06] Gate D and the ranges that are not emoji

The pictograph pattern deliberately omits the dingbat and geometric ranges. Those carry
characters a document may legitimately use as punctuation or as a bullet, and including
them turns Gate D into a source of findings a reader learns to wave through. The cost is
stated rather than hidden: a document using a dingbat as an icon passes Gate D.
