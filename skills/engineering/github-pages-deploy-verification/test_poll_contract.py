import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
SKILL = ROOT / "SKILL.md"


def poll_function():
    text = SKILL.read_text()
    match = re.search(r"```bash\n(poll_deploy\(\) \{.*?\n\})\n```", text, re.DOTALL)
    assert match, "SKILL.md must publish the canonical poll_deploy function"
    return match.group(1)


def run_poll(tmp_path, curl_results, build_result="failure", attempts=3):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    state = tmp_path / "curl-state"
    status_calls = tmp_path / "status-calls"
    (bin_dir / "curl").write_text(
        "#!/bin/sh\n"
        f"state={state!s}\n"
        "n=$(($(cat \"$state\" 2>/dev/null || printf 0) + 1))\n"
        "printf '%s' \"$n\" >\"$state\"\n"
        f"case $n in {' '.join(f'{i}) printf %s {value[0]!r};;' for i, value in enumerate(curl_results, 1))} *) printf %s {curl_results[-1][0]!r};; esac\n"
        "case $n in "
        + " ".join(
            f"{i}) exit {code};;" for i, (_, code) in enumerate(curl_results, 1)
        )
        + f" *) exit {curl_results[-1][1]};; esac\n"
    )
    (bin_dir / "deploy_status").write_text(
        "#!/bin/sh\n"
        f"printf x >>{status_calls!s}\n"
        f"printf '%s\\n' {build_result!r}\n"
    )
    (bin_dir / "sleep").write_text("#!/bin/sh\nexit 0\n")
    for command in bin_dir.iterdir():
        command.chmod(0o755)

    script = f'{poll_function()}\npoll_deploy "https://example.invalid" "fresh" {attempts}'
    result = subprocess.run(
        ["bash", "-c", script],
        text=True,
        capture_output=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
    )
    calls = int(state.read_text())
    return result, calls, status_calls.exists()


def test_success_is_zero_and_skips_build_status(tmp_path):
    result, calls, status_called = run_poll(tmp_path, [("fresh", 0)])
    assert result.returncode == 0
    assert "LIVE" in result.stdout
    assert calls == 1
    assert not status_called


def test_http_failure_is_nonzero_after_bound(tmp_path):
    result, calls, status_called = run_poll(tmp_path, [("missing", 22)])
    assert result.returncode != 0
    assert "HTTP FAILURE" in result.stderr
    assert calls == 3
    assert status_called


def test_timeout_is_nonzero_after_bound(tmp_path):
    result, calls, status_called = run_poll(
        tmp_path, [("old", 0)], build_result="building"
    )
    assert result.returncode != 0
    assert "TIMEOUT" in result.stderr
    assert calls == 3
    assert status_called


def test_stale_content_is_nonzero_after_bound(tmp_path):
    result, calls, status_called = run_poll(
        tmp_path, [("old", 0)], build_result="built"
    )
    assert result.returncode != 0
    assert "STALE CONTENT" in result.stderr
    assert calls == 3
    assert status_called


def test_all_published_polls_use_the_bounded_function():
    text = SKILL.read_text()
    shell_blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
    assert all("until curl" not in block for block in shell_blocks)
    assert text.count("poll_deploy ") >= 5
    assert "git diff HEAD~1 -- ." in text
    assert "git diff HEAD~1 -- index.html" not in text
