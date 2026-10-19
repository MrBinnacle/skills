#!/usr/bin/env python3
"""Contract tests for the release gate's CI-state check, G11 (issue #475).

G11 reads ``actions/runs?head_sha=<HEAD>`` and passes only when every required
workflow's newest run at that commit completed with success. The incident
behind it: on 2026-10-05 a ``?branch=main`` query returned runs from 2026-09-14
as the newest, while a ``head_sha`` query for the same commit showed a failing
same-day run. A gate that read the branch filter would have passed.

Every case drives the shipped script as a subprocess against a seeded git tree
(``--root``) whose ``origin`` names this repository, and points the gate at a
local fake API through ``RELEASE_GATE_GITHUB_API_URL``. The fake answers a
branch-filtered query with stale green runs and a ``head_sha`` query with the
scenario under test, so a gate that read the wrong filter is caught.

``GITHUB_ACTIONS`` is removed from every subprocess env except the case that
sets it: G11 skips inside an Actions run, and this suite runs inside one in CI.
Without the removal every case would skip there and pass by construction.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from test_release_gate import GATE, git_repo_with_base  # noqa: E402

SLUG = "MrBinnacle/skills"
REQUIRED = (
    ".github/workflows/tests.yml",
    ".github/workflows/links.yml",
    ".github/workflows/depersonalization-gate.yml",
)
STALE_SHA = "0" * 40

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def wf_run(
    run_id: int,
    path: str,
    sha: str,
    *,
    status: str = "completed",
    conclusion: str | None = "success",
    created: str = "2026-10-19T10:00:00Z",
) -> dict:
    return {
        "id": run_id,
        "path": path,
        "head_sha": sha,
        "status": status,
        "conclusion": conclusion,
        "created_at": created,
        "html_url": f"https://github.com/{SLUG}/actions/runs/{run_id}",
    }


def green(sha: str, start: int = 1) -> list[dict]:
    return [wf_run(start + i, path, sha) for i, path in enumerate(REQUIRED)]


class FakeApi:
    """A local GitHub API that serves `pages` for a head_sha query.

    A query carrying `branch` gets stale green runs at another commit, which
    is what the 2026-10-05 incident returned. Any other query gets a 404, so a
    gate asking for something unexpected fails rather than passes.
    """

    def __init__(
        self, pages: list[list[dict]], *, status: int = 200, next_link: str | None = None
    ) -> None:
        self.pages = pages
        self.status = status
        self.next_link = next_link
        self.auth: list[str | None] = []
        self.queries: list[dict[str, list[str]]] = []
        api = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - http.server API
                url = urlparse(self.path)
                query = parse_qs(url.query)
                api.queries.append(query)
                api.auth.append(self.headers.get("Authorization"))
                if url.path != f"/repos/{SLUG}/actions/runs":
                    self._send(404, {"message": "Not Found"})
                elif api.status != 200:
                    self._send(api.status, {"message": "fake failure"})
                elif "branch" in query:
                    self._send(200, {"total_count": 3, "workflow_runs": green(STALE_SHA, 900)})
                elif "head_sha" in query:
                    page = int(query.get("page", ["1"])[0])
                    runs = api.pages[page - 1] if page <= len(api.pages) else []
                    link = api.next_link
                    if link is None and page < len(api.pages):
                        link = f'<{api.base}/repos/{SLUG}/actions/runs?head_sha={query["head_sha"][0]}&per_page=100&page={page + 1}>; rel="next"'
                    total = sum(len(p) for p in api.pages)
                    self._send(200, {"total_count": total, "workflow_runs": runs}, link)
                else:
                    self._send(404, {"message": "unexpected query"})

            def _send(self, code: int, body: dict, link: str | None = None) -> None:
                data = json.dumps(body).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                if link:
                    self.send_header("Link", link)
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - base signature
                del format, args

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def __enter__(self) -> FakeApi:
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()


def release_tree(root: Path, *, origin: bool = True) -> str:
    """A release ref (version bumped) with a GitHub origin; returns HEAD's SHA."""
    git_repo_with_base(root, "1.2.0", "1.3.0")
    if origin:
        subprocess.run(
            ["git", "-C", str(root), "remote", "add", "origin", f"https://github.com/{SLUG}.git"],
            check=True,
            capture_output=True,
        )
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def run_gate(root: Path, api: FakeApi | None, **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_ACTIONS", "GITHUB_TOKEN")}
    if api is not None:
        env["RELEASE_GATE_GITHUB_API_URL"] = api.base
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(GATE), "--release", "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def g11_lines(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [line for line in result.stdout.splitlines() if "G11" in line]


# ------------------------------------------------------------------- cases


def case_sha_failure_blocks_although_branch_filter_is_green() -> None:
    """AC-1: the branch-filtered answer is stale green; the SHA answer fails."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = green(sha)
        runs[1] = wf_run(2, REQUIRED[1], sha, conclusion="failure")
        with FakeApi([runs]) as api:
            result = run_gate(root, api)
        check(
            "AC-1: a failing required run at HEAD blocks while ?branch= is stale green",
            result.returncode == 1
            and any("links.yml" in line and "failure" in line for line in g11_lines(result)),
            result.stdout + result.stderr,
        )
        check(
            "AC-1: the gate never reads state through a branch filter",
            bool(api.queries) and all("branch" not in q for q in api.queries),
            repr(api.queries),
        )


def case_missing_required_workflow_blocks() -> None:
    """AC-2: a required workflow with no run at HEAD is a refusal, not a pass."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = [run for run in green(sha) if run["path"] != REQUIRED[1]]
        with FakeApi([runs]) as api:
            result = run_gate(root, api)
        check(
            "AC-2: a required workflow with no run at HEAD blocks",
            result.returncode == 1
            and any("links.yml has no run at" in line for line in g11_lines(result)),
            result.stdout + result.stderr,
        )


def case_all_required_green_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        with FakeApi([green(sha)]) as api:
            result = run_gate(root, api)
        check(
            "every required workflow green at HEAD passes, and the summary names CI state",
            result.returncode == 0
            and "required workflows green at HEAD" in result.stdout
            and not g11_lines(result),
            result.stdout + result.stderr,
        )


def case_unfinished_run_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = green(sha)
        runs[0] = wf_run(1, REQUIRED[0], sha, status="in_progress", conclusion=None)
        with FakeApi([runs]) as api:
            result = run_gate(root, api)
        check(
            "a required run still in progress blocks",
            result.returncode == 1
            and any("tests.yml has not finished" in line for line in g11_lines(result)),
            result.stdout + result.stderr,
        )


def case_newest_run_per_workflow_decides() -> None:
    """A re-run that went green after a failure passes; a newer failure after
    a green run blocks. The newest run of the workflow governs, both ways."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        old_fail = wf_run(50, REQUIRED[0], sha, conclusion="failure", created="2026-10-19T09:00:00Z")
        with FakeApi([green(sha) + [old_fail]]) as api:
            recovered = run_gate(root, api)
        new_fail = wf_run(60, REQUIRED[0], sha, conclusion="failure", created="2026-10-19T11:00:00Z")
        with FakeApi([green(sha) + [new_fail]]) as api:
            regressed = run_gate(root, api)
        check(
            "an older failure superseded by a newer green run passes",
            recovered.returncode == 0,
            recovered.stdout + recovered.stderr,
        )
        check(
            "a newer failure after a green run blocks",
            regressed.returncode == 1
            and any("tests.yml concluded failure" in line for line in g11_lines(regressed)),
            regressed.stdout + regressed.stderr,
        )


def case_runs_on_a_later_page_are_read() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = green(sha)
        with FakeApi([runs[:2], runs[2:]]) as api:
            result = run_gate(root, api)
        check(
            "a required run on page 2 is found by following Link rel=next",
            result.returncode == 0 and len(api.queries) == 2,
            f"queries={api.queries}\n{result.stdout}{result.stderr}",
        )


def case_unreadable_api_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        release_tree(root)
        with FakeApi([], status=500) as api:
            result = run_gate(root, api)
        check(
            "an API error is a refusal, never a skip or a pass",
            result.returncode == 1
            and any("could not be read" in line for line in g11_lines(result)),
            result.stdout + result.stderr,
        )


def case_non_github_origin_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        release_tree(root, origin=False)
        subprocess.run(
            ["git", "-C", str(root), "remote", "add", "origin", "https://example.invalid/x.git"],
            check=True,
            capture_output=True,
        )
        result = run_gate(root, None)
        check(
            "an origin that is not a GitHub repository blocks",
            result.returncode == 1
            and any("is not a GitHub repository" in line for line in g11_lines(result)),
            result.stdout + result.stderr,
        )


def case_skips_are_printed() -> None:
    """Inside Actions and without an origin, G11 says it did not run."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = green(sha)
        runs[0] = wf_run(1, REQUIRED[0], sha, conclusion="failure")
        with FakeApi([runs]) as api:
            inside = run_gate(root, api, GITHUB_ACTIONS="true")
        check(
            "inside an Actions run G11 prints its skip and reads nothing",
            inside.returncode == 0
            and "G11: SKIPPED, inside a GitHub Actions run" in inside.stdout
            and not api.queries
            and "not run: G11" in inside.stdout,
            inside.stdout + inside.stderr,
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        release_tree(root, origin=False)
        result = run_gate(root, None)
        check(
            "without an origin remote G11 prints its skip",
            result.returncode == 0
            and "G11: SKIPPED, no origin remote" in result.stdout
            and "not run: G11" in result.stdout,
            result.stdout + result.stderr,
        )


def case_hostile_responses_fail_closed() -> None:
    """A run id that is not a number, a Link header that leaves the API
    origin, and a Link header that never ends are each a listed refusal,
    never a traceback, a leaked token or a hang."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sha = release_tree(root)
        runs = green(sha)
        runs.append(dict(wf_run(0, REQUIRED[0], sha), id="not-a-number"))
        with FakeApi([runs]) as api:
            odd_id = run_gate(root, api)
        check(
            "a non-numeric run id does not crash the gate",
            "Traceback" not in odd_id.stderr and "RELEASE GATE:" in odd_id.stdout,
            odd_id.stdout + odd_id.stderr,
        )
        away = "http://example.invalid/repos/x/actions/runs?page=2"
        with FakeApi([green(sha)], next_link=f'<{away}>; rel="next"') as api:
            leaked = run_gate(root, api, GITHUB_TOKEN="fixture-token")
        check(
            "a next link to another origin is refused, and the token is sent only to the API",
            leaked.returncode == 1
            and any("leaves the API origin" in line for line in g11_lines(leaked))
            and api.auth == ["Bearer fixture-token"],
            f"auth={api.auth}\n{leaked.stdout}{leaked.stderr}",
        )
        with FakeApi([green(sha)]) as api:
            api.next_link = f'<{api.base}/repos/{SLUG}/actions/runs?head_sha={sha}&page=1>; rel="next"'
            endless = run_gate(root, api)
        check(
            "an endless next link stops at the page cap and refuses",
            endless.returncode == 1
            and any("more than" in line and "pages" in line for line in g11_lines(endless)),
            endless.stdout[-600:] + endless.stderr[-600:],
        )


def case_empty_required_set_fails_closed() -> None:
    """The spec: an empty required set fails the gate. REQUIRED_WORKFLOWS is a
    module constant, so this case empties it in process."""
    import release_gate as gate  # noqa: E402

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        release_tree(root)
        saved, gate.REQUIRED_WORKFLOWS = gate.REQUIRED_WORKFLOWS, ()
        saved_env = os.environ.pop("GITHUB_ACTIONS", None)
        errors: list[str] = []
        try:
            gate.gate_ci_state(root, errors)
        finally:
            gate.REQUIRED_WORKFLOWS = saved
            if saved_env is not None:
                os.environ["GITHUB_ACTIONS"] = saved_env
        check(
            "an empty required-workflow set is a refusal",
            any("no required workflow is declared" in e for e in errors),
            repr(errors),
        )


def main() -> None:
    cases = (
        case_sha_failure_blocks_although_branch_filter_is_green,
        case_missing_required_workflow_blocks,
        case_all_required_green_passes,
        case_unfinished_run_blocks,
        case_newest_run_per_workflow_decides,
        case_runs_on_a_later_page_are_read,
        case_unreadable_api_fails_closed,
        case_non_github_origin_fails_closed,
        case_skips_are_printed,
        case_hostile_responses_fail_closed,
        case_empty_required_set_fails_closed,
    )
    for case in cases:
        case()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: G11 verified across {len(cases)} case(s) - it reads CI state at "
        "HEAD's SHA, never through a branch filter, and fails closed."
    )


if __name__ == "__main__":
    main()
