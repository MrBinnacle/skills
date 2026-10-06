# probes — dead-predicate

Scripts for `SKILL.md` § Solution, steps 2 to 4. Each assumes the rule shape `SKILL.md` defines:
a JSON file whose `rules` list holds entries with a `skill` name and a `patterns` list. Set
`RULES` to your router's rule file and rename the keys if yours differ.

## Step 2. Scan the decoded patterns for control characters

Load the JSON and scan the decoded strings. A byte scan of the file misses the defect: a JSON
writer stores the backspace as the two characters `\b`, so the raw byte 0x08 never reaches disk.

```sh
python -c "
import json,os
CTRL={'\x08':r'\b','\x0c':r'\f','\x0b':r'\v','\x07':r'\a'}
for i,r in enumerate(json.load(open(os.environ['RULES'],encoding='utf-8'))['rules']):
    for j,p in enumerate(r.get('patterns',[])):
        for ch,esc in CTRL.items():
            if ch in p: print('rule[%d] pattern[%d] holds literal %r, meant %s' % (i,j,ch,esc))
"
```

## Step 3. Read the patterns, the order and the names

Print every rule that matches a prompt, in file order. If your router stops at the first match,
only the first rule printed fires; a rule that never appears first for its own prompts is
shadowed. An invalid regex is tried as a plain substring; match your router's own fallback.

```sh
python -c "
import json,os,re,sys
for r in json.load(open(os.environ['RULES'],encoding='utf-8'))['rules']:
    def m(p):
        try: return re.search(p,sys.argv[1],re.I)
        except re.error: return p.lower() in sys.argv[1].lower()
    hits=[p for p in r.get('patterns',[]) if m(p)]
    if hits: print(r['skill'],hits)
" "write me a plan for issue 18"
```

Then check that every `skill` name still resolves to an installed card. Look under
`~/.claude/skills/<name>/` for a personal skill, and under `~/.claude/plugins/` for a plugin
skill. A plugin skill's name is `<plugin>:<name>` (Claude Code plugin docs, checked 2026-10-05),
so moving a skill into a plugin changes the name the rule must carry.

## Step 4. Add patterns that target authoring, not mention

Match the verb plus the noun, so talk about the thing stays silent and a request to produce one
fires. Inside a JSON string, write every regex backslash twice:

```json
"\\b(writ(e|ing)|draft(ing)?|creat(e|ing)|produc(e|ing)|author(ing)?|updat(e|ing)|need|want|give me)\\b.{0,30}\\bplans?\\b",
"\\b(implementation|execution|migration|rollout|remediation|tooling|project|build)\\s+plans?\\b",
"\\bplans?\\b.{0,20}\\bfor\\b.{0,25}(#\\d+|issue|ticket)"
```

Then validate the file:
`python -c "import json,os;json.load(open(os.environ['RULES'],encoding='utf-8'));print('JSON valid')"`.
