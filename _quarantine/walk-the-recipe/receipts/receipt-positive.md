# Receipt: positive

| Field | Value |
|---|---|
| Started (UTC) | 2026-10-21T00:17:33Z |
| claude --version | 2.1.305 (Claude Code) |
| OS | Microsoft Windows [Version 10.0.26300.9711] |
| Recipe | `v3.0.1:README.md`, git blob `cdfb4fdd25fc375222fdf91ac62006e469cc0198`, sha256 `06512d735baf1c04d98c3f59300b6593695a93f1a901a02a6e59a2884bab0d59` |
| Card loaded | `SKILL.md` sha256 `112ea463265bec0a199818c0d6a780047dafd43beaf4721ea4a6bb904a201636` |
| Step runner | `replay/run_step.py` sha256 `9d273954e7e12f3de8ccd3e6712910043eeb5d5f203d68622fb005c8f074850a` |
| Target CLAUDE_CONFIG_DIR length | 171 characters |
| Agent exit code | 0 |
| Recipe steps executed (STEP lines in trace) | 10 |
| Trace | `trace-positive.jsonl`, sha256 `3e82e0478017f3dd9aec9993b95ead1f74fc93a98557fe382a5a4b68ef54513f` |
| Transcript | `transcript-positive.txt`, sha256 `10349962d9e2af92db2926068a9bf28e182f815011f7f38334a94b7315c2bcec` |

Command (system prompt elided; it is the text in replay.sh plus the card):

```text
claude -p --strict-mcp-config --tools Bash Read --allowedTools "Bash(python -I <replay>/run_step.py:*)" Read --permission-mode dontAsk --output-format stream-json --verbose --system-prompt <...> "<target-user prompt>"
```
