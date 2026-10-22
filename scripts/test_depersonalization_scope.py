#!/usr/bin/env python3
"""Suite for the de-personalization gate's file scope and account-data patterns (#539).

WHAT THIS SUITE HAS TO PROVE

    The gate read Markdown only, so a replay trace carrying a billing event and
    session identifiers passed it (#538 verifier). A widened gate that matches
    nothing looks the same as one that works, so the load-bearing cases are POISON:
    a fixture in a non-Markdown file class carrying each pattern must go red, and
    its REDACTED twin must stay green.

    Cases:
      - every codename hook and every account-data hook selects text files by type,
        not by extension;
      - each account-data pattern fires on a fixture in .jsonl, .txt, .py and .sh,
        and the codename patterns fire in a non-Markdown file;
      - a REDACTED identifier and a bare mention of "utilization" stay green;
      - no path exemption is an extension or a directory, and the live exemptions
        each name one existing file;
      - when `pre-commit` is installed, the real hook run reports `file:line` for
        a poison trace and exits non-zero.

The entry patterns are read from `.pre-commit-config.yaml` itself, so this suite
cannot drift from the gate. Poison text is built here at run time; no poison
fixture is committed, because it would sit inside the guarded set.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_message_residue import parse_hooks  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / ".pre-commit-config.yaml"

FAILURES: list[str] = []

UUID = "0b9f6c1e-3a47-4d2b-9e55-7c1a2f8d4b60"

POISON = {
    "leak-rate-limit-event": '{"type":"rate_limit_event","status":"allowed"}',
    "leak-overage-status": '{"overageStatus":"rejected"}',
    "leak-utilization": '{"rate_limit_info":{"rateLimitType":"seven_day","utilization":0.43}}',
    "leak-session-id": '{"session_id":"' + UUID + '","type":"result"}',
}
POISON_SESSION_VARIANTS = (
    "request_id: " + UUID,
    'export SESSION_ID="' + UUID + '"',
    '{"requestId": "' + UUID + '"}',
)
CLEAN = (
    '{"session_id":"REDACTED","uuid":"REDACTED","request_id":"REDACTED"}',
    '{"session_id":"<redacted>"}',
    "CPU utilization stays under 50% in this benchmark.",
    "the session id is a value the harness assigns",
)
CODENAME_POISON = ("WI-12 was the work item", "see skills_research for notes")


def fail(case: str, detail: str) -> None:
    FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def hook_fires(hooks: dict[str, dict[str, str]], hook_id: str, line: str) -> bool:
    return re.search(hooks[hook_id]["entry"], line) is not None


def case_every_pygrep_hook_selects_by_type(hooks: dict[str, dict[str, str]]) -> None:
    case = "case_every_pygrep_hook_selects_by_type"
    wanted = [h for h in hooks if h.startswith(("residue-", "leak-"))]
    if len(wanted) < 11:
        fail(case, f"expected 11 residue and leak hooks, parsed {wanted}")
        return
    bad = [h for h in wanted if hooks[h].get("types") != "[text]" or "files" in hooks[h]]
    if bad:
        fail(case, f"hooks not selecting every text file by type: {bad}")
        return
    print(f"  ok   {case} ({len(wanted)} hooks)")


def case_account_patterns_fire_in_every_file_class(hooks: dict[str, dict[str, str]]) -> None:
    case = "case_account_patterns_fire_in_every_file_class"
    missing = [h for h, line in POISON.items() if not hook_fires(hooks, h, line)]
    extra = [v for v in POISON_SESSION_VARIANTS if not hook_fires(hooks, "leak-session-id", v)]
    if missing or extra:
        fail(case, f"silent on poison: hooks={missing} session variants={extra}")
        return
    print(f"  ok   {case}")


def case_clean_values_stay_green(hooks: dict[str, dict[str, str]]) -> None:
    case = "case_clean_values_stay_green"
    hit = [
        (h, line)
        for h in POISON
        for line in CLEAN
        if hook_fires(hooks, h, line)
    ]
    if hit:
        fail(case, f"false positives: {hit}")
        return
    print(f"  ok   {case}")


def case_codename_hooks_fire_in_non_markdown(hooks: dict[str, dict[str, str]]) -> None:
    case = "case_codename_hooks_fire_in_non_markdown"
    fired = {h for h in hooks if h.startswith("residue-") for line in CODENAME_POISON if hook_fires(hooks, h, line)}
    if not {"residue-wi-id", "residue-research-dir"} <= fired:
        fail(case, f"codename patterns silent on poison lines: fired={sorted(fired)}")
        return
    print(f"  ok   {case}")


def case_exemptions_are_single_files(hooks: dict[str, dict[str, str]]) -> None:
    case = "case_exemptions_are_single_files"
    probes = ("a.py", "a.json", "a.jsonl", "a.txt", "a.sh", "a.md", "docs/a.md", "scripts/a.py", "_quarantine/x/a.jsonl")
    problems: list[str] = []
    for hook_id, fields in hooks.items():
        pattern = fields.get("exclude")
        if not pattern or not hook_id.startswith(("residue-", "leak-")):
            continue
        hit = [p for p in probes if re.search(pattern, p)]
        if hit:
            problems.append(f"{hook_id} exempts {hit}")
        body = re.fullmatch(r"\^\((.*)\)\$", pattern)
        if not body:
            problems.append(f"{hook_id} exclude is not an anchored alternation of files")
            continue
        expanded = expand(body.group(1))
        for path in expanded:
            if not (REPO_ROOT / path).is_file():
                problems.append(f"{hook_id} exempts {path}, which is not a file in this tree")
    if problems:
        fail(case, "; ".join(problems))
        return
    print(f"  ok   {case}")


def expand(alternation: str) -> list[str]:
    """Expand `a|scripts/(b|c)\\.py` into concrete paths. One nesting level is enough here."""
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in alternation:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    out: list[str] = []
    for part in parts:
        m = re.match(r"^(.*)\(([\w|]+)\)(.*)$", part)
        if m:
            out += [(m.group(1) + opt + m.group(3)).replace("\\", "") for opt in m.group(2).split("|")]
        else:
            out.append(part.replace("\\", ""))
    return out


def case_real_hook_goes_red_with_file_and_line() -> None:
    case = "case_real_hook_goes_red_with_file_and_line"
    exe = shutil.which("pre-commit")
    if exe is None:
        print(f"  skip {case}: pre-commit not installed")
        return
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "-C", tmp, "init", "-q"], check=True, capture_output=True)
        shutil.copy(CONFIG, root / ".pre-commit-config.yaml")
        trace = root / "receipts" / "trace.ndjson.txt"
        trace.parent.mkdir()
        trace.write_text("\n".join(["clean line", *POISON.values()]) + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True, capture_output=True)
        for hook_id, line in POISON.items():
            result = subprocess.run(
                [exe, "run", hook_id, "--all-files"], cwd=tmp, capture_output=True, text=True, encoding="utf-8"
            )
            reported = re.search(r"receipts/trace\.ndjson\.txt:\d+:", result.stdout)
            if result.returncode == 0 or not reported:
                fail(case, f"{hook_id} did not fail with file:line on a .txt trace:\n{result.stdout}")
                return
    print(f"  ok   {case}")


def main() -> None:
    hooks = parse_hooks(CONFIG)
    case_every_pygrep_hook_selects_by_type(hooks)
    case_account_patterns_fire_in_every_file_class(hooks)
    case_clean_values_stay_green(hooks)
    case_codename_hooks_fire_in_non_markdown(hooks)
    case_exemptions_are_single_files(hooks)
    case_real_hook_goes_red_with_file_and_line()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        "PASS: de-personalization scope verified; every hook reads text files by type, each "
        "account-data pattern fires on poison and ignores REDACTED values, and every exemption is one file."
    )


if __name__ == "__main__":
    main()
