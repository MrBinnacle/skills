"""Drive one Pi RPC session: send prompts in order, each after the previous run settles.

Usage: python pi/scripts/rpc_drive.py OUT.jsonl [pi args...] -- PROMPT [PROMPT...]
Writes every RPC event to OUT.jsonl and prints a compact trace. Exits when the last
prompt's run settles, or after a timeout. Exists because `pi -p` exits as soon as a
slash command's handler returns, so work a command queues for the agent never runs.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import queue

TIMEOUT_S = 600


def main() -> int:
    out_path = sys.argv[1]
    split = sys.argv.index("--")
    pi_args, prompts = sys.argv[2:split], sys.argv[split + 1:]
    for prompt in prompts:
        # Git Bash rewrites a leading `/command` into a Windows path before Python sees it.
        # A model given the mangled text treats it as a task and wanders (observed 2026-10-10).
        if prompt.startswith("C:/Program Files/Git/"):
            print(f"REFUSED: prompt was path-mangled by Git Bash: {prompt[:60]!r}. Re-run with MSYS_NO_PATHCONV=1.")
            return 2
    proc = subprocess.Popen(
        ["pi", "--mode", "rpc", "--no-session", *pi_args], shell=False,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
    ) if sys.platform != "win32" else subprocess.Popen(
        " ".join(["pi", "--mode", "rpc", "--no-session", *pi_args]), shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def pump() -> None:
        for line in proc.stdout:
            lines.put(line)
        lines.put(None)

    threading.Thread(target=pump, daemon=True).start()
    with open(out_path, "w", encoding="utf-8") as out:
        for i, prompt in enumerate(prompts):
            proc.stdin.write(json.dumps({"type": "prompt", "id": f"p{i}", "message": prompt}) + "\n")
            proc.stdin.flush()
            settled = False
            responded = started = False
            while not settled:
                # A slash command that starts no agent run never emits agent_settled: once Pi has
                # answered the prompt and nothing started within a few seconds, the prompt is done.
                wait = 5 if responded and not started else TIMEOUT_S
                try:
                    line = lines.get(timeout=wait)
                except queue.Empty:
                    if responded and not started:
                        break
                    print("TIMEOUT waiting for agent_settled")
                    proc.kill()
                    return 1
                if line is None:
                    print("pi exited early")
                    return 1
                out.write(line)
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                kind = msg.get("type")
                if kind == "tool_execution_start":
                    print(f"  tool {msg.get('toolName')} {json.dumps(msg.get('args'))[:90]}")
                elif kind == "entry_appended":
                    print(f"  ENTRY {json.dumps(msg.get('entry'))[:300]}")
                elif kind == "message_end" and msg["message"].get("role") == "custom":
                    print(f"  CUSTOM {str(msg['message'].get('content'))[:600]}")
                elif kind == "response" and not msg.get("success", True):
                    print(f"  RESPONSE ERROR {msg}")
                elif kind in ("agent_start", "agent_end"):
                    started = True
                    print(f"  {kind}")
                elif kind == "extension_ui_request" and msg.get("method") == "notify":
                    print(f"  NOTIFY {str(msg.get('message'))[:600]}")
                elif kind == "agent_settled":
                    settled = True
                if kind == "response" and msg.get("id") == f"p{i}":
                    responded = True
            print(f"settled after prompt {i}")
    proc.stdin.close()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
    err = proc.stderr.read()
    if err.strip():
        print("STDERR:", err.strip()[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
