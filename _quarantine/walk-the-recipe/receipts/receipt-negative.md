# Receipt: negative

| Field | Value |
|---|---|
| Started (UTC) | 2026-10-21T00:06:39Z |
| claude --version | 2.1.305 (Claude Code) |
| OS | Microsoft Windows [Version 10.0.26300.9711] |
| Recipe | `v3.1.0:README.md`, git blob `d2899ec582c1df65f5222e5e4147be984543a150`, sha256 `42ae3bfe3dbbbaf95ca0facc149661e6154d02287431f223b99d141124ea2723` |
| Card loaded | `SKILL.md` sha256 `112ea463265bec0a199818c0d6a780047dafd43beaf4721ea4a6bb904a201636` |
| Replay runner (produced this receipt) | `replay/replay.sh` sha256 `94bdaab0cc54dbc01c5e895705713bf26d4bc5f1862e0f7035de0e06d728771c`, since removed |
| Replay runner successor | `replay/replay.py`, unexecuted for this receipt |
| Step runner | `replay/run_step.py` sha256 `9d273954e7e12f3de8ccd3e6712910043eeb5d5f203d68622fb005c8f074850a` |
| Target CLAUDE_CONFIG_DIR length | 171 characters |
| Agent exit code | 0 |
| Recipe steps executed | 5 (10 STEP lines in trace; each tool result is serialized twice) |
| Trace | `trace-negative.ndjson.txt`, sha256 `d815008bb097f60240d0d33909922ced4149a2ba70fc9f895223572865f22c9e`, hash of the file after the widened `strip_system.py`; the earlier strip gave `8e5a7b5743c8dd2d04bf47718ab1f53aac04e77d0233fe28b93e9df61ad987e9` as `trace-negative.jsonl` |
| Transcript | `transcript-negative.txt`, sha256 `b7d12142885c67b889406e0318f119346589775cb4a89842ee4d98f4647746cb` |

Command (system prompt elided; it is the text in replay.sh, now replay.py, plus the card):

```text
claude -p --strict-mcp-config --tools Bash Read --allowedTools "Bash(python -I <replay>/run_step.py:*)" Read --permission-mode dontAsk --output-format stream-json --verbose --system-prompt <...> "<target-user prompt>"
```
