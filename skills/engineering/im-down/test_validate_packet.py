#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validator", HERE / "validate_packet.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

PASSING_COMMAND = "git rev-parse HEAD"
FAILING_COMMAND = "exit 1"
# Cross-platform side-effect commands: record that the check actually ran.
COUNTER_PASS = "python -c \"open('run-count.txt','a').write('pass\\n')\""
COUNTER_FAIL = (
    "python -c \"open('run-count.txt','a').write('fail\\n'); raise SystemExit(1)\""
)
FLAG_CHECK = (
    "python -c \"import os,sys; sys.exit(0 if os.path.exists('flag-ok') else 1)\""
)


def expect_structure(name: str, valid: bool):
    data, text = validator.extract(HERE / name)
    errors = validator.validate_structure(data, text)
    assert (not errors) == valid, (name, errors)


def placeholder_cases():
    """TODO in prose is content. TODO alone on a line is unfinished work."""
    data, text = validator.extract(HERE / "fixture-clean.md")

    prose = text + "\nClosed the ticket titled 'sweep the remaining TODO comments'.\n"
    assert not validator.placeholder_tokens(data, prose), "prose mention must pass"
    assert not validator.validate_structure(data, prose)

    for line in ("TODO", "  TBD  ", "- TODO:", "**TODO**"):
        candidate = text + f"\n{line}\n"
        assert validator.placeholder_tokens(data, candidate), f"must reject: {line!r}"

    unfinished = copy.deepcopy(data)
    unfinished["objective"] = "TBD"
    assert "TBD" in validator.placeholder_tokens(unfinished, text), "manifest value must reject"

    assert validator.validate_structure(data, text + "\n__REQUIRED__\n")


def lint_cases():
    """A check that always exits zero must be named as unfailable."""
    vacuous = {"receiver_checks": [{"name": "git-status", "command": "git status --porcelain"}]}
    assert validator.lint_receiver_checks(vacuous), "always-zero check must be flagged"

    failable = {"receiver_checks": [
        {"name": "clean-tree", "command": "git diff --quiet && git diff --cached --quiet"}
    ]}
    assert not validator.lint_receiver_checks(failable), "fail-able check must not be flagged"


def repository_cases():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("fixture", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
        head = validator.git(repo, "rev-parse", "HEAD")
        branch = validator.git(repo, "branch", "--show-current")

        clean, _ = validator.extract(HERE / "fixture-clean.md")
        clean["repository"]["head"] = head
        clean["repository"]["branch"] = branch
        errors, _ = validator.validate_repository(clean, repo)
        assert not errors, errors

        stale, _ = validator.extract(HERE / "fixture-stale.md")
        errors, _ = validator.validate_repository(stale, repo)
        assert any("stale HEAD" in e for e in errors), errors

        failed, _ = validator.extract(HERE / "fixture-failed-probe.md")
        failed["repository"]["head"] = head
        failed["repository"]["branch"] = branch
        errors, _ = validator.validate_repository(failed, repo)
        assert any("path probe failed" in e for e in errors), errors

        command_probe_cases(clean, repo)


def command_probe_cases(clean: dict, repo: Path):
    """A command probe supports 'verified' only when the owner authorised it."""
    def with_probe(command: str) -> dict:
        packet = copy.deepcopy(clean)
        packet["claims"] = [{
            "id": "C001", "text": "the suite passes", "status": "verified",
            "probe": {"kind": "command", "value": command},
            "evidence": "observed",
        }]
        return packet

    errors, _ = validator.validate_repository(with_probe(FAILING_COMMAND), repo)
    assert any("absent from the trusted" in e for e in errors), errors

    allowed = {FAILING_COMMAND}
    errors, _ = validator.validate_repository(with_probe(FAILING_COMMAND), repo, allowed)
    assert any("command probe failed" in e for e in errors), errors

    allowed = {PASSING_COMMAND}
    errors, notes = validator.validate_repository(with_probe(PASSING_COMMAND), repo, allowed)
    assert not errors, errors
    assert any("command probe passed" in n for n in notes), notes


def close_commit_cases():
    """Produce mode refuses a packet whose HEAD is not the doctrine close commit.

    The ordering constraint is the defect: the close must commit BEFORE the
    packet records HEAD, and until now nothing enforced it but prose.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("fixture", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "ordinary work, no ritual line"],
                       cwd=repo, check=True, capture_output=True)

        required = {"close_commit": {"contains": "RITUAL:"}}
        errors = validator.validate_close_commit(required, repo)
        assert any("close commit" in e for e in errors), errors

        # `contains` is a literal substring test. A project that writes a regex
        # gets no match and refuses every packet, so the name must not invite one.
        assert validator.validate_close_commit({"close_commit": {"contains": "^RITUAL:"}}, repo)

        # Opt-in: a project declaring no close ritual is unaffected.
        assert not validator.validate_close_commit({}, repo)
        assert not validator.validate_close_commit(None, repo)

        # The close commit itself passes.
        (repo / "STATE.md").write_text("closed", encoding="utf-8")
        subprocess.run(["git", "add", "STATE.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "chore(state): close\n\nRITUAL: retro+1"],
                       cwd=repo, check=True, capture_output=True)
        assert not validator.validate_close_commit(required, repo)

        # Called here, not from __main__, because it needs this temp repo. Named
        # in the PASS roster so it is not a case that runs invisibly.
        cli_close_commit_case(repo)


def cli_close_commit_case(repo: Path):
    """Produce mode must RUN the check, not merely define it."""
    subprocess.run(["git", "commit", "--allow-empty", "-m", "later work, no ritual line"],
                   cwd=repo, check=True, capture_output=True)
    config = repo / "boundary.json"
    config.write_text('{"close_commit": {"contains": "RITUAL:"}}', encoding="utf-8")

    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(HERE / "fixture-clean.md"),
         "--mode", "produce", "--repo-root", str(repo), "--config", str(config)],
        text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout
    assert "is not the close commit" in result.stdout, result.stdout


def write_prior_packet(directory: Path, name: str, head: str) -> Path:
    """A minimal prior packet: markers plus a manifest recording one head."""
    manifest = json.dumps({"repository": {"head": head}})
    path = directory / name
    path.write_text(
        f"<!-- SESSION-PACKET-V1\n{manifest}\nSESSION-PACKET-V1 -->\n",
        encoding="utf-8",
    )
    return path


def claimed_head_cases():
    """Produce mode refuses a HEAD the most recent prior packet already claimed.

    This is the session boundary validate_close_commit cannot see: a session
    that committed nothing still sits on the previous close, and the marker
    test passes there. The packet directory knows better -- the previous close
    already claimed that HEAD.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("fixture", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "chore(state): close\n\nRITUAL: retro+1"],
                       cwd=repo, check=True, capture_output=True)
        head = validator.git(repo, "rev-parse", "HEAD")
        packet_dir = repo / "packets"
        packet_dir.mkdir()
        config = {"packet_dir": "packets"}
        own = repo / "new-packet.md"

        # Nothing to compare against: an empty packet directory degrades to
        # today's behaviour. A fresh clone must be able to produce packet one.
        assert not validator.validate_unclaimed_head(config, repo, own)

        # No packet_dir declared: the check is opt-in and returns nothing.
        assert not validator.validate_unclaimed_head({}, repo, own)
        assert not validator.validate_unclaimed_head(None, repo, own)

        # The most recent prior packet claims this HEAD: refused, and the
        # message names both the HEAD and the packet that claimed it.
        prior = write_prior_packet(packet_dir, "20260101T000000Z-aaaa.md", head)
        errors = validator.validate_unclaimed_head(config, repo, own)
        assert any("already claimed" in e for e in errors), errors
        assert any(prior.name in e for e in errors), errors
        assert any(head in e for e in errors), errors

        # A fresh close moved HEAD: no prior packet claims it, so it passes.
        subprocess.run(["git", "commit", "--allow-empty",
                        "-m", "chore(state): close again\n\nRITUAL: retro+1"],
                       cwd=repo, check=True, capture_output=True)
        assert not validator.validate_unclaimed_head(config, repo, own)
        new_head = validator.git(repo, "rev-parse", "HEAD")

        # A stray unreadable file cannot disable the guard: the scan walks
        # past it, newest-first, to the first prior that parses and records a
        # head. README sorts lexicographically after digit-led timestamps, so
        # treating the raw maximum as "the" prior packet would make one stray
        # file reopen the hole this check closes -- permanently and silently.
        claiming = write_prior_packet(packet_dir, "20260102T000000Z-bbbb.md", new_head)
        (packet_dir / "README.md").write_text("no markers here", encoding="utf-8")
        errors = validator.validate_unclaimed_head(config, repo, own)
        assert any(claiming.name in e for e in errors), errors

        # A manifest that is valid JSON but not an object is skipped, not
        # crashed on: the receipt contract is 0/2, never a raw traceback.
        (packet_dir / "20260103T000000Z-cccc.md").write_text(
            "<!-- SESSION-PACKET-V1\n[1, 2]\nSESSION-PACKET-V1 -->\n",
            encoding="utf-8",
        )
        errors = validator.validate_unclaimed_head(config, repo, own)
        assert any(claiming.name in e for e in errors), errors

        # A manifest without repository.head is walked past the same way.
        (packet_dir / "20260104T000000Z-dddd.md").write_text(
            '<!-- SESSION-PACKET-V1\n{"repository": {}}\nSESSION-PACKET-V1 -->\n',
            encoding="utf-8",
        )
        errors = validator.validate_unclaimed_head(config, repo, own)
        assert any(claiming.name in e for e in errors), errors

        # With no usable prior at all -- every file unreadable or headless --
        # the check degrades to today's behaviour rather than refusing.
        claiming.unlink()
        assert not validator.validate_unclaimed_head(config, repo, own)

        # The packet under validation may already sit in the directory as the
        # newest file, correctly recording the current HEAD. It is not a PRIOR
        # packet and must not refuse itself.
        own_in_dir = write_prior_packet(packet_dir, "20260105T000000Z-eeee.md", new_head)
        assert not validator.validate_unclaimed_head(config, repo, own_in_dir)

        # But any OTHER producer at that same HEAD is refused by that entry.
        errors = validator.validate_unclaimed_head(config, repo, own)
        assert any(own_in_dir.name in e for e in errors), errors

        cli_claimed_head_case(repo, packet_dir)


def cli_claimed_head_case(repo: Path, packet_dir: Path):
    """Produce mode runs BOTH refusals: the new check did not replace the old.

    HEAD here lacks the ritual marker AND is claimed by the newest prior
    packet, so both messages must appear in one receipt.
    """
    subprocess.run(["git", "commit", "--allow-empty", "-m", "later work, no ritual line"],
                   cwd=repo, check=True, capture_output=True)
    head = validator.git(repo, "rev-parse", "HEAD")
    write_prior_packet(packet_dir, "20260106T000000Z-ffff.md", head)
    config = repo / "boundary.json"
    config.write_text(
        '{"close_commit": {"contains": "RITUAL:"}, "packet_dir": "packets"}',
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(HERE / "fixture-clean.md"),
         "--mode", "produce", "--repo-root", str(repo), "--config", str(config)],
        text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout
    assert "is not the close commit" in result.stdout, result.stdout
    assert "already claimed" in result.stdout, result.stdout


def cli_cases():
    """Receive mode must not degrade to silent acceptance without a config."""
    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(HERE / "fixture-clean.md"),
         "--mode", "receive"],
        text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout
    assert "requires --config and --repo-root" in result.stdout, result.stdout


def _boundary_config(repo: Path, name: str, check_command: str) -> Path:
    config = repo / name
    config.write_text(json.dumps({
        "state_file": ".claude/session-state.json",
        "close_commit": {"contains": "RITUAL:"},
        "packet_dir": "packets",
        "receiver_checks": [{"name": "under-test", "command": check_command}],
    }), encoding="utf-8")
    return config


def red_check_cases():
    """A producer that has measured a receiver check red writes no packet.

    skills#238: snapshot_state.py recorded exit_code 1 in tests[] and still
    wrote the packet, so the next session paid for a failure the closing
    session had already observed. Three surfaces refuse now: both producer
    scripts before the file exists, and produce mode on a manifest that
    already carries a red entry (a packet written by another caller).
    """
    red, _ = validator.extract(HERE / "fixture-red-check.md")
    errors = validator.validate_recorded_checks(red)
    assert any("recorded receiver check failed" in e for e in errors), errors
    assert any("tests[1]" in e for e in errors), errors
    clean, _ = validator.extract(HERE / "fixture-clean.md")
    assert not validator.validate_recorded_checks(clean)

    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(HERE / "fixture-red-check.md"),
         "--mode", "produce"],
        text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout
    assert "recorded receiver check failed" in result.stdout, result.stdout

    snapshot_py = _pair_script("snapshot_state.py")
    close_py = _pair_script("close_session.py")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _init_repo(repo)
        packet_dir = repo / "packets"
        args = ["--repo-root", str(repo), "--objective", "x",
                "--next-action", "y", "--purpose", "z"]

        red_config = _boundary_config(repo, "red.json", FAILING_COMMAND)
        result = subprocess.run(
            ["python", str(snapshot_py), "--config", str(red_config), *args],
            text=True, capture_output=True,
        )
        assert result.returncode != 0, "snapshot wrote a packet after a red check"
        assert FAILING_COMMAND in result.stderr, result.stderr
        assert not packet_dir.exists() or not list(packet_dir.glob("*.md")), \
            "snapshot refused but a packet file exists"

        green_config = _boundary_config(repo, "green.json", PASSING_COMMAND)
        result = subprocess.run(
            ["python", str(snapshot_py), "--config", str(green_config), *args],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert Path(result.stdout.strip()).is_file(), "green snapshot wrote no packet"

        # close_session.py carries its own snapshot stage and must refuse the
        # same way. The close commit stands; only the packet is withheld.
        before = sorted(packet_dir.glob("*.md"))
        result = subprocess.run(
            ["python", str(close_py), "--config", str(red_config), *args],
            text=True, capture_output=True,
        )
        assert result.returncode != 0, "close wrote a packet after a red check"
        payload = json.loads(result.stdout)
        assert payload["failed_receiver_checks"][0]["name"] == "under-test", payload
        assert sorted(packet_dir.glob("*.md")) == before, "close refused but a packet appeared"


def assertions_held_cases():
    """A REJECTED receive receipt says whether every packet assertion held.

    Ruled S411 (skills_research#153, direction D): the verdict vocabulary
    stays ACCEPTED / REJECTED. A defective receiver check on a sound packet
    still rejects, but the receipt now states that the packet's own
    assertions held and names the failing checks, so the reader can tell a
    packet defect from a gate defect. Both directions are controlled here.
    """
    close_py = _pair_script("close_session.py")
    open_py = _pair_script("open_session.py")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _init_repo(repo)
        green_config = _boundary_config(repo, "green.json", PASSING_COMMAND)
        closed = subprocess.run(
            ["python", str(close_py), "--config", str(green_config),
             "--repo-root", str(repo), "--objective", "x",
             "--next-action", "y", "--purpose", "z"],
            text=True, capture_output=True,
        )
        assert closed.returncode == 0, closed.stdout + closed.stderr
        out = json.loads(closed.stdout)
        head = out["head"]
        sound = _fill_packet(Path(out["packet_path"]), head)

        # The receiver's check is defective; the packet is sound.
        red_config = _boundary_config(repo, "red.json", FAILING_COMMAND)
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(sound),
             "--mode", "receive", "--repo-root", str(repo), "--config", str(red_config)],
            text=True, capture_output=True,
        )
        assert result.returncode == 2, result.stdout
        receipt = json.loads(result.stdout)
        assert receipt["verdict"] == "REJECTED", receipt
        assert receipt["packet_assertions_held"] is True, receipt
        assert receipt["failed_receiver_checks"] == ["under-test"], receipt
        assert list(receipt)[-1] == "summary", "the plain-words line must be last"
        assert "under-test" in receipt["summary"], receipt
        assert "receiver checks alone" in receipt["summary"], receipt

        # open_session.py passes the classification through unchanged.
        result = subprocess.run(
            ["python", str(open_py), str(sound),
             "--config", str(red_config), "--repo-root", str(repo)],
            text=True, capture_output=True,
        )
        assert result.returncode != 0, result.stdout
        receipt = json.loads(result.stdout)
        assert receipt["verdict"] == "REJECTED", receipt
        assert receipt["packet_assertions_held"] is True, receipt
        assert list(receipt)[-1] == "summary", receipt

        # Red control: a failing claim probe under the same defective check
        # rejects with the field false. The rejection is the packet's.
        failed, _ = validator.extract(HERE / "fixture-failed-probe.md")
        failed["repository"]["head"] = head
        failed["repository"]["branch"] = "main"
        broken = repo / "broken.md"
        broken.write_text(
            f"<!-- SESSION-PACKET-V1\n{json.dumps(failed)}\nSESSION-PACKET-V1 -->\n"
            "## Narrative\nx\n## Decisions\nx\n## What We Tried\nx\n## Resume Bootstrap\nx\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(broken),
             "--mode", "receive", "--repo-root", str(repo), "--config", str(red_config)],
            text=True, capture_output=True,
        )
        assert result.returncode == 2, result.stdout
        receipt = json.loads(result.stdout)
        assert receipt["packet_assertions_held"] is False, receipt
        assert any("path probe failed" in e for e in receipt["errors"]), receipt

        # An ACCEPTED receipt carries no classification: there is nothing to
        # classify, and an always-present field would read as a verdict.
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(sound),
             "--mode", "receive", "--repo-root", str(repo), "--config", str(green_config)],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout
        assert "packet_assertions_held" not in json.loads(result.stdout)


def _cache_config(
    repo: Path,
    name: str,
    checks: list[dict],
    cache_path: Path | None,
    extra: dict | None = None,
) -> Path:
    config = repo / name
    payload: dict = {
        "state_file": ".claude/session-state.json",
        "packet_dir": "packets",
        "receiver_checks": checks,
    }
    if cache_path is not None:
        payload["receiver_check_cache"] = str(cache_path)
    if extra:
        payload.update(extra)
    config.write_text(json.dumps(payload), encoding="utf-8")
    return config


def _receive_receipt(repo: Path, config_path: Path, packet: Path) -> tuple[int, dict]:
    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(packet),
         "--mode", "receive", "--repo-root", str(repo), "--config", str(config_path)],
        text=True, capture_output=True,
    )
    return result.returncode, json.loads(result.stdout)


def _open_receipt(repo: Path, config_path: Path, packet: Path) -> tuple[int, dict]:
    open_py = _pair_script("open_session.py")
    result = subprocess.run(
        ["python", str(open_py), str(packet),
         "--config", str(config_path), "--repo-root", str(repo)],
        text=True, capture_output=True,
    )
    return result.returncode, json.loads(result.stdout)


def _count_runs(repo: Path) -> int:
    path = repo / "run-count.txt"
    if not path.is_file():
        return 0
    return len([ln for ln in path.read_text(encoding="utf-8").splitlines() if ln])


def _age_cache(cache_path: Path, days: int = 8) -> None:
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    then = datetime.now(timezone.utc) - timedelta(days=days)
    data["last_full_run_at"] = then.isoformat().replace("+00:00", "Z")
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _prepared_repo(tmp: str, checks: list[dict], cache_path: Path | None):
    """Init a repo with inputs, a packet at HEAD, and a boundary config."""
    repo = Path(tmp) / "repo"
    repo.mkdir(parents=True)
    _init_repo(repo)
    inputs = repo / "inputs"
    inputs.mkdir()
    (inputs / "locked.txt").write_text("locked-v1\n", encoding="utf-8")
    (inputs / "other.txt").write_text("other\n", encoding="utf-8")
    (repo / "outside.txt").write_text("outside\n", encoding="utf-8")
    head = validator.git(repo, "rev-parse", "HEAD")
    packet = _fill_packet(repo / "packet.md", head)
    config = _cache_config(repo, "boundary.json", checks, cache_path)
    return repo, packet, config


def cache_hit_and_input_change_cases():
    """A byte change under cache_inputs re-runs the check; a hit does not.

    The key covers the sha256 of the bytes on disk of cache_inputs, the Python
    version, `git --version` and the command string. One byte under a declared input
    changes the key, so the last passing run is no longer the answer.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "counter",
            "command": COUNTER_PASS,
            "cache_inputs": ["inputs/locked.txt"],
        }], cache_path)

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        first = receipt["checks"][0]
        assert first["status"] == "passed", first
        assert first["exit_code"] == 0, first
        assert _count_runs(repo) == 1, "first open must execute the check"
        assert cache_path.is_file(), "a passing cacheable check must be cached"

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        second = receipt["checks"][0]
        assert second["status"] == "cached", second
        assert second["exit_code"] == 0, second
        assert second.get("cache_key"), second
        assert second.get("cached_at"), second
        assert _count_runs(repo) == 1, "unchanged inputs must not re-run the check"

        check = json.loads(config.read_text(encoding="utf-8"))["receiver_checks"][0]
        key_before = validator.check_cache_key(check, repo)
        assert second["cache_key"] == key_before, (second, key_before)

        locked = repo / "inputs" / "locked.txt"
        locked.write_text("locked-v2\n", encoding="utf-8")
        key_after = validator.check_cache_key(check, repo)
        # A passed entry carries no cache_key, so the key is computed, not read
        # off the receipt: comparing against an absent field always differs.
        assert key_after != key_before, "one byte under cache_inputs must change the key"
        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        third = receipt["checks"][0]
        assert third["status"] == "passed", third
        assert third["exit_code"] == 0, third
        stored = json.loads(cache_path.read_text(encoding="utf-8"))["checks"]
        assert key_after in stored, "the re-run must be cached under the new key"
        assert _count_runs(repo) == 2, "a byte change under cache_inputs must re-run"


def cache_outside_change_cases():
    """A change outside every cache_inputs re-runs no cached check."""
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "counter",
            "command": COUNTER_PASS,
            "cache_inputs": ["inputs/locked.txt"],
        }], cache_path)

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        assert receipt["checks"][0]["status"] == "passed"
        assert _count_runs(repo) == 1

        (repo / "inputs" / "other.txt").write_text("other-changed\n", encoding="utf-8")
        (repo / "outside.txt").write_text("outside-changed\n", encoding="utf-8")
        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        check = receipt["checks"][0]
        assert check["status"] == "cached", check
        assert _count_runs(repo) == 1, (
            "a change outside cache_inputs must not re-run a cached check"
        )


def cache_directory_inputs_cases():
    """A directory in cache_inputs covers every file under it."""
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "counter",
            "command": COUNTER_PASS,
            "cache_inputs": ["inputs/"],
        }], cache_path)

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        assert receipt["checks"][0]["status"] == "passed"
        assert _count_runs(repo) == 1

        code, receipt = _receive_receipt(repo, config, packet)
        assert receipt["checks"][0]["status"] == "cached"
        assert _count_runs(repo) == 1

        # other.txt sits under the declared directory, so a byte there re-runs.
        (repo / "inputs" / "other.txt").write_text("other-v2\n", encoding="utf-8")
        code, receipt = _receive_receipt(repo, config, packet)
        assert receipt["checks"][0]["status"] == "passed", receipt["checks"][0]
        assert _count_runs(repo) == 2


def cache_failing_never_cached_cases():
    """A failing check is never served from cache.

    Run it failing twice with no change: the second run must execute again
    and fail. Only passing runs are cached.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "counter-fail",
            "command": COUNTER_FAIL,
            "cache_inputs": ["inputs/locked.txt"],
        }], cache_path)

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 2, receipt
        first = receipt["checks"][0]
        assert first["status"] == "failed", first
        assert first["exit_code"] != 0, first
        assert _count_runs(repo) == 1
        assert not cache_path.is_file() or not json.loads(
            cache_path.read_text(encoding="utf-8")
        ).get("checks"), "a failing check must not be cached"

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 2, receipt
        second = receipt["checks"][0]
        assert second["status"] == "failed", second
        assert second["exit_code"] != 0, second
        assert _count_runs(repo) == 2, (
            "a failing check must execute again, never be served from cache"
        )


def cache_weekly_disagreement_cases():
    """A planted disagreement is caught by the weekly full run and fails the open.

    The cache records a pass under the current key. The check's real outcome
    then changes without any cache_inputs byte changing — the flag the command
    tests is outside the key. Once a week the full run executes every check
    uncached, compares against the cached verdict, and refuses the open on a
    disagreement while clearing that check's cache entry.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        checks = [{
            "name": "flagged",
            "command": FLAG_CHECK,
            "cache_inputs": ["inputs/locked.txt"],
        }]
        repo, packet, config = _prepared_repo(tmp, checks, cache_path)
        (repo / "flag-ok").write_text("ok\n", encoding="utf-8")

        # close_session writes durable state the open requires. It shares the
        # open's cache, so its passing run is the verdict the open serves.
        closed = _close(repo, config)
        assert closed.returncode == 0, closed.stdout + closed.stderr
        closed_out = json.loads(closed.stdout)
        packet = _fill_packet(Path(closed_out["packet_path"]), closed_out["head"])

        code, receipt = _open_receipt(repo, config, packet)
        assert code == 0, receipt
        assert receipt["verdict"] == "ACCEPTED", receipt
        assert receipt["checks"][0]["status"] == "cached", receipt["checks"][0]
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        assert cached.get("checks"), "the close must have populated the cache"

        _age_cache(cache_path)
        (repo / "flag-ok").unlink()

        code, receipt = _open_receipt(repo, config, packet)
        assert code == 2, receipt
        assert receipt["verdict"] == "REJECTED", receipt
        errors = receipt["errors"]
        assert any("cache disagreement" in e for e in errors), errors
        assert any("flagged" in e for e in errors), errors
        after = json.loads(cache_path.read_text(encoding="utf-8"))
        assert not after.get("checks"), (
            "a weekly disagreement must clear that check's cache entry"
        )



def _close(repo: Path, config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python", str(_pair_script("close_session.py")), "--config", str(config),
         "--repo-root", str(repo), "--objective", "x",
         "--next-action", "y", "--purpose", "z"],
        text=True, capture_output=True,
    )


def cache_close_shares_cases():
    """The close and the open share one cache under one key rule (issue #371).

    A close runs every receiver check; an open on the unchanged tree right
    after it must serve each cacheable check from the close's run rather than
    execute it a second time. A check with no cache_inputs still runs.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, _, config = _prepared_repo(tmp, [
            {"name": "counter", "command": COUNTER_PASS,
             "cache_inputs": ["inputs/locked.txt"]},
            {"name": "uncached", "command": PASSING_COMMAND},
        ], cache_path)

        closed = _close(repo, config)
        assert closed.returncode == 0, closed.stdout + closed.stderr
        assert _count_runs(repo) == 1, "the close must execute the check"
        assert cache_path.is_file(), "the close must write the shared cache"
        closed_out = json.loads(closed.stdout)
        packet = _fill_packet(Path(closed_out["packet_path"]), closed_out["head"])

        code, receipt = _open_receipt(repo, config, packet)
        assert code == 0, receipt
        by_name = {c["name"]: c for c in receipt["checks"]}
        assert by_name["counter"]["status"] == "cached", by_name["counter"]
        assert by_name["uncached"]["status"] == "passed", by_name["uncached"]
        assert _count_runs(repo) == 1, (
            "an open after a close on an unchanged tree must not re-run a cached check"
        )

        # A second close serves the check from the cache. Its packet must say
        # so: the verdict is the cached run's, observed when that run happened,
        # not stamped as though the close had just executed it.
        closed = _close(repo, config)
        assert closed.returncode == 0, closed.stdout + closed.stderr
        assert _count_runs(repo) == 1, "a close on an unchanged tree serves the cache"
        manifest, _ = validator.extract(Path(json.loads(closed.stdout)["packet_path"]))
        entry = next(t for t in manifest["tests"] if t["command"] == COUNTER_PASS)
        assert entry["status"] == "cached", entry
        assert entry["cache_key"] == by_name["counter"]["cache_key"], entry
        assert entry["cached_at"] == by_name["counter"]["cached_at"], entry
        assert entry["observed_at"] == entry["cached_at"], entry


class _TornFile:
    """A writable file that dies halfway through its first write."""

    def __init__(self, handle):
        self._handle = handle

    def write(self, data):
        self._handle.write(data[: len(data) // 2])
        self._handle.flush()
        raise OSError("simulated interruption mid-write")

    def __getattr__(self, name):
        return getattr(self._handle, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._handle.close()
        return False


def cache_atomic_write_cases():
    """An interrupted cache write never leaves a corrupt cache file (issue #371).

    Two writers share one machine-level cache, and either can die mid-write.
    The write is torn halfway through by patching io.open, which every
    standard-library text write goes through. The cache file must still hold
    the last complete write, and no partial temp file may be left beside it.
    """
    import io
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "cache-dir" / "check-cache.json"
        good = {"checks": {"k1": {"exit_code": 0, "cached_at": "t", "command": "c"}},
                "last_full_run_at": "2026-01-01T00:00:00Z"}
        validator.save_cache(cache_path, good)
        assert validator.load_cache(cache_path) == good

        real_open = io.open

        def torn_open(file, mode="r", *args, **kwargs):
            handle = real_open(file, mode, *args, **kwargs)
            return _TornFile(handle) if any(m in mode for m in "wax+") else handle

        newer = {"checks": {"k2": {"exit_code": 0, "cached_at": "u", "command": "d"}},
                 "last_full_run_at": "2026-02-01T00:00:00Z"}
        io.open = torn_open
        try:
            try:
                validator.save_cache(cache_path, newer)
            except OSError:
                pass
        finally:
            io.open = real_open

        raw = cache_path.read_text(encoding="utf-8")
        try:
            survived = json.loads(raw)
        except json.JSONDecodeError:
            raise AssertionError(
                f"an interrupted write left a corrupt cache file: {raw!r}"
            ) from None
        assert survived == good, survived
        leftovers = sorted(p.name for p in cache_path.parent.iterdir())
        assert leftovers == ["check-cache.json"], leftovers


def cache_path_confined_cases():
    """A relative receiver_check_cache never lands in the repo tree (issue #371).

    It resolves under the default cache directory, outside every tree. One
    that climbs out of that directory is refused, not followed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        cache_dir = validator.default_cache_path().parent
        resolved = validator.resolve_cache_path(
            {"receiver_check_cache": "team/cache.json"}, repo,
        )
        assert resolved == cache_dir / "team" / "cache.json", resolved
        assert repo.resolve() not in resolved.resolve().parents, resolved
        try:
            escaped = validator.resolve_cache_path(
                {"receiver_check_cache": "../../escape.json"}, repo,
            )
        except validator.PacketError as exc:
            assert "receiver_check_cache" in str(exc), exc
        else:
            raise AssertionError(f"a climbing relative path was followed: {escaped}")
        absolute = Path(tmp) / "elsewhere" / "cache.json"
        assert validator.resolve_cache_path(
            {"receiver_check_cache": str(absolute)}, repo,
        ) == absolute


def cache_no_inputs_fields_cases():
    """A config with no cache_inputs keeps prior fields, plus status and duration_ms."""
    with tempfile.TemporaryDirectory() as tmp:
        cache_path = Path(tmp) / "check-cache.json"
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "under-test",
            "command": PASSING_COMMAND,
        }], None)

        code, receipt = _receive_receipt(repo, config, packet)
        assert code == 0, receipt
        assert receipt["verdict"] == "ACCEPTED", receipt
        check = receipt["checks"][0]
        # Prior fields unchanged.
        assert check["name"] == "under-test"
        assert check["command"] == PASSING_COMMAND
        assert check["exit_code"] == 0
        assert "output" in check
        # New fields present.
        assert check["status"] == "passed", check
        assert isinstance(check["duration_ms"], int), check
        assert "cache_key" not in check
        assert "cached_at" not in check
        assert not cache_path.exists(), (
            "a config with no cache_inputs must not open a cache file"
        )

        red_config = _cache_config(repo, "red.json", [{
            "name": "under-test",
            "command": FAILING_COMMAND,
        }], None)
        code, receipt = _receive_receipt(repo, red_config, packet)
        assert code == 2, receipt
        check = receipt["checks"][0]
        assert check["status"] == "failed", check
        assert check["exit_code"] != 0
        assert isinstance(check["duration_ms"], int), check
        assert "stdout" in check or "stderr" in check


def cache_expand_cases():
    """`~` expands; a directory means every file under it; key covers command."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        _init_repo(repo)
        with tempfile.NamedTemporaryFile(
            dir=Path.home(), prefix=".im-up-cache-expand-probe-", delete=False
        ) as probe:
            probe.write(b"home-probe\n")
            home_file = Path(probe.name)
        try:
            key_home = validator.check_cache_key(
                {"command": "true", "cache_inputs": [f"~/{home_file.name}"]},
                repo,
            )
            key_home_other = validator.check_cache_key(
                {"command": "true", "cache_inputs": [str(home_file)]},
                repo,
            )
            assert key_home and key_home_other
            assert key_home == key_home_other, "~ must expand to the same file"
        finally:
            home_file.unlink(missing_ok=True)

        assert validator.weekly_full_due({"last_full_run_at": "2026-10-01T00:00:00"})

        (repo / "inputs").mkdir()
        (repo / "inputs" / "a.txt").write_text("a\n", encoding="utf-8")
        (repo / "inputs" / "b.txt").write_text("b\n", encoding="utf-8")
        key_dir = validator.check_cache_key(
            {"command": "true", "cache_inputs": ["inputs"]}, repo
        )
        key_a_only = validator.check_cache_key(
            {"command": "true", "cache_inputs": ["inputs/a.txt"]}, repo
        )
        assert key_dir and key_a_only
        assert key_dir != key_a_only, "a directory covers more than one file"

        key_cmd1 = validator.check_cache_key(
            {"command": "true", "cache_inputs": ["inputs/a.txt"]}, repo
        )
        key_cmd2 = validator.check_cache_key(
            {"command": "false", "cache_inputs": ["inputs/a.txt"]}, repo
        )
        assert key_cmd1 != key_cmd2, "the command string is part of the key"

        assert validator.check_cache_key({"command": "true"}, repo) is None



# A check that prints U+0141 (UTF-8 C5 81; 0x81 has no cp1252 mapping)
# followed by a byte that is not valid UTF-8, then fails so its output is
# kept in the receipt. Shell-neutral: runs under cmd.exe and /bin/sh.
NON_CP1252_CHECK = (
    "python -c \"import sys; sys.stdout.buffer.write(bytes([0xc5, 0x81, 0x20, 0xff])); "
    "sys.stdout.flush(); sys.exit(1)\""
)


def utf8_check_output_cases():
    """Check output decodes as UTF-8 whatever the caller's locale (issue #372).

    The validator is run with UTF-8 mode off and PYTHONIOENCODING=cp1252, the
    environment of a Windows host outside a closer that sets them. A check
    printing a character outside cp1252 crashed the validator there. The
    trailing invalid byte makes the case discriminate on a UTF-8 host too:
    strict UTF-8 decoding crashes on it, errors="replace" does not.
    """
    import os
    with tempfile.TemporaryDirectory() as tmp:
        repo, packet, config = _prepared_repo(tmp, [{
            "name": "non-cp1252",
            "command": NON_CP1252_CHECK,
        }], None)
        env = dict(os.environ, PYTHONUTF8="0", PYTHONIOENCODING="cp1252")
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(packet),
             "--mode", "receive", "--repo-root", str(repo), "--config", str(config)],
            capture_output=True, env=env,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        try:
            receipt = json.loads(stdout)
        except json.JSONDecodeError:
            raise AssertionError(
                "validator crashed on non-cp1252 check output: "
                + result.stderr.decode("utf-8", errors="replace")[-600:]
            ) from None
        assert result.returncode == 2, receipt
        check = receipt["checks"][0]
        assert check["status"] == "failed", check
        assert "Ł" in check["stdout"], check  # decoded as UTF-8
        assert "�" in check["stdout"], check  # invalid byte replaced


def utf8_git_output_cases():
    """Git output decodes as UTF-8 whatever the caller's locale.

    The same defect as issue #372 on the validator's git calls: a branch name
    whose UTF-8 bytes include one cp1252 leaves undefined (U+0401 is D0 81)
    crashed `git branch --show-current` decoding on a cp1252 host.
    """
    import os
    branch = "feature-Ё"
    with tempfile.TemporaryDirectory() as tmp:
        repo, _, config = _prepared_repo(tmp, [{
            "name": "passing", "command": PASSING_COMMAND,
        }], None)
        subprocess.run(["git", "checkout", "-q", "-b", branch], cwd=repo, check=True)
        head = validator.git(repo, "rev-parse", "HEAD")
        packet = _fill_packet(repo / "packet.md", head, branch=branch)
        env = dict(os.environ, PYTHONUTF8="0", PYTHONIOENCODING="cp1252")
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(packet),
             "--mode", "receive", "--repo-root", str(repo), "--config", str(config)],
            capture_output=True, env=env,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        try:
            receipt = json.loads(stdout)
        except json.JSONDecodeError:
            raise AssertionError(
                "validator crashed on non-cp1252 git output: "
                + result.stderr.decode("utf-8", errors="replace")[-600:]
            ) from None
        assert result.returncode == 0, receipt
        assert receipt["verdict"] == "ACCEPTED", receipt

# Every file measured byte-identical across the pair (sha256, 2026-08-24) is
# in the contract. If a file stops being shared, REMOVE it from this tuple and
# record why in the removing change -- a contract that silently narrows is the
# defect the contract exists to catch. Card-private scripts are absent on
# purpose: snapshot_state.py and close_session.py exist only in im-down;
# open_session.py exists only in im-up. They are not shared and must not be
# added here to force a false symmetry.
SHARED_PARITY_CONTRACT = (
    "CONFIG.example.json",
    "PACKET-FORMAT.md",
    "fixture-clean.md",
    "fixture-failed-probe.md",
    "fixture-missing-field.md",
    "fixture-red-check.md",
    "fixture-stale.md",
    "test_validate_packet.py",
    "validate_packet.py",
)


def duplication_case() -> tuple[bool, str]:
    """The pair ships shared files in two directories. They must not drift.

    Guarding only three files was too narrow: eight files are byte-identical
    across the pair, and a change to any of the other five diverged the cards
    with nothing to catch it. The contract now names every shared file, and
    the run reports which files it compared, so a future narrowing shows up
    in the output rather than only in the source.

    Returns (verified, message). On a single-card install there is no sibling
    to compare against, so parity is NOT VERIFIED rather than passed -- a
    suite that prints no-drift having compared nothing reports a property it
    did not test. A sibling that exists but lacks a contract file has drifted:
    absence is a difference, not a skip.
    """
    sibling_name = {"im-down": "im-up", "im-up": "im-down"}.get(HERE.name)
    if sibling_name is None:
        # A copied or renamed install is a single-card layout, not a crash:
        # the pre-adoption run must finish and say what it could not test.
        return (False,
                f"parity NOT VERIFIED: this card runs from directory "
                f"'{HERE.name}', not one of the im-down/im-up pair, so the "
                f"{len(SHARED_PARITY_CONTRACT)}-file shared contract was "
                "not tested")
    sibling_dir = HERE.parent / sibling_name
    if not sibling_dir.is_dir():
        return (False,
                f"parity NOT VERIFIED: sibling card '{sibling_name}' is not "
                f"present, so the {len(SHARED_PARITY_CONTRACT)}-file shared "
                "contract was not tested")
    for filename in SHARED_PARITY_CONTRACT:
        ours = HERE / filename
        theirs = sibling_dir / filename
        assert ours.exists(), \
            f"{filename} is in the parity contract but absent from {HERE.name}"
        assert theirs.exists(), \
            f"{filename} is in the parity contract but absent from {sibling_name}"
        assert theirs.read_bytes() == ours.read_bytes(), \
            f"{filename} has drifted from {sibling_name}"
    compared = ", ".join(SHARED_PARITY_CONTRACT)
    return (True,
            f"parity: compared {len(SHARED_PARITY_CONTRACT)} shared files "
            f"against {sibling_name}: {compared}")


def _pair_script(name: str) -> Path:
    """Resolve a card-private script from this card or its sibling."""
    local = HERE / name
    if local.is_file():
        return local
    sibling_name = {"im-down": "im-up", "im-up": "im-down"}.get(HERE.name)
    if sibling_name:
        sibling = HERE.parent / sibling_name / name
        if sibling.is_file():
            return sibling
    raise FileNotFoundError(f"{name} not found on {HERE.name} or its sibling")


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True,
                    capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"],
                    cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"],
                    cwd=repo, check=True)
    (repo / "README.md").write_text("fixture", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"],
                    cwd=repo, check=True, capture_output=True)


def _fill_packet(scaffold: Path, head: str, branch: str = "main") -> Path:
    """Replace scaffold markers with a produce/receive-valid body at HEAD."""
    clean, _ = validator.extract(HERE / "fixture-clean.md")
    clean["repository"]["head"] = head
    clean["repository"]["branch"] = branch
    body = (
        f"<!-- SESSION-PACKET-V1\n{json.dumps(clean, indent=2)}\n"
        "SESSION-PACKET-V1 -->\n"
        "## Narrative\nTest.\n## Decisions\nNone.\n"
        "## What We Tried\nNone.\n## Resume Bootstrap\nNext.\n"
    )
    scaffold.write_text(body, encoding="utf-8")
    return scaffold


def close_session_cases():
    """close_session.py is the one public close: state, commit, then packet.

    Ordering lives inside one process. A config without state_file fails
    rather than writing a packet with no doctrine. The filled packet's HEAD
    equals the close commit and passes both produce and receive mode.
    """
    close_py = _pair_script("close_session.py")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _init_repo(repo)
        head_before = validator.git(repo, "rev-parse", "HEAD")

        config = repo / "boundary.json"
        config.write_text(json.dumps({
            "state_file": ".claude/session-state.json",
            "close_commit": {"contains": "RITUAL:"},
            "packet_dir": "packets",
            "receiver_checks": [{
                "name": "clean-tree",
                "command": "git diff --quiet && git diff --cached --quiet",
            }],
        }), encoding="utf-8")

        result = subprocess.run(
            ["python", str(close_py),
             "--config", str(config),
             "--repo-root", str(repo),
             "--objective", "Finish the feature",
             "--next-action", "Run tests",
             "--purpose", "Continue work"],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        out = json.loads(result.stdout)

        state_path = Path(out["state_path"])
        assert state_path.is_file(), "state file was not created"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["objective"] == "Finish the feature"
        assert state["next_action"]["task"] == "Run tests"
        assert state["next_action"]["purpose"] == "Continue work"
        assert state["repository"]["head"] == head_before
        assert "created_at" in state

        head_after = out["head"]
        assert head_after != head_before, "HEAD was not moved by close commit"
        assert head_after == validator.git(repo, "rev-parse", "HEAD")
        message = validator.git(repo, "log", "-1", "--pretty=%B")
        assert "RITUAL:" in message, f"commit missing marker: {message}"
        tracked = validator.git(repo, "ls-files", ".claude/session-state.json")
        assert tracked, "state file not tracked after commit"

        packet_path = Path(out["packet_path"])
        assert packet_path.is_file(), "packet scaffold was not created"
        data, _ = validator.extract(packet_path)
        assert data["repository"]["head"] == head_after, (
            "packet HEAD must equal the close commit, not the pre-close HEAD"
        )

        # Doctrine skip: no state_file key → close refuses before any packet.
        bad_config = repo / "bad.json"
        bad_config.write_text(json.dumps({
            "close_commit": {"contains": "RITUAL:"},
            "packet_dir": "packets",
        }), encoding="utf-8")
        result = subprocess.run(
            ["python", str(close_py),
             "--config", str(bad_config),
             "--repo-root", str(repo),
             "--objective", "x", "--next-action", "y", "--purpose", "z"],
            text=True, capture_output=True,
        )
        assert result.returncode != 0, "should fail without state_file"
        assert "state_file" in result.stdout, result.stdout

        # Filled packet at the close HEAD passes produce and receive.
        filled = _fill_packet(packet_path, head_after)
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(filled),
             "--mode", "produce", "--repo-root", str(repo),
             "--config", str(config)],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout
        result = subprocess.run(
            ["python", str(HERE / "validate_packet.py"), str(filled),
             "--mode", "receive", "--repo-root", str(repo),
             "--config", str(config)],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout
        receipt = json.loads(result.stdout)
        assert receipt["verdict"] == "ACCEPTED", receipt


def open_session_cases():
    """open_session.py validates the packet then loads durable state into one
    receipt. Missing state after a valid packet rejects rather than admitting
    a session with no doctrine.
    """
    close_py = _pair_script("close_session.py")
    open_py = _pair_script("open_session.py")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        _init_repo(repo)
        config = repo / "boundary.json"
        config.write_text(json.dumps({
            "state_file": ".claude/session-state.json",
            "close_commit": {"contains": "RITUAL:"},
            "packet_dir": "packets",
            "receiver_checks": [{
                "name": "clean-tree",
                "command": "git diff --quiet && git diff --cached --quiet",
            }],
        }), encoding="utf-8")

        closed = subprocess.run(
            ["python", str(close_py),
             "--config", str(config),
             "--repo-root", str(repo),
             "--objective", "Finish the feature",
             "--next-action", "Run tests",
             "--purpose", "Continue work"],
            text=True, capture_output=True,
        )
        assert closed.returncode == 0, closed.stdout + closed.stderr
        closed_out = json.loads(closed.stdout)
        filled = _fill_packet(
            Path(closed_out["packet_path"]), closed_out["head"],
        )

        result = subprocess.run(
            ["python", str(open_py), str(filled),
             "--config", str(config),
             "--repo-root", str(repo)],
            text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        receipt = json.loads(result.stdout)
        assert receipt["verdict"] == "ACCEPTED", receipt
        assert receipt["state_read"]["status"] == "loaded", receipt
        assert receipt["state_read"]["objective"] == "Finish the feature"
        assert receipt["state_read"]["next_action"]["task"] == "Run tests"

        # State write skipped: config names a path that was never written.
        # Keep the tree clean so the failure is the missing doctrine, not a
        # dirty-tree receiver check.
        skip_config = repo / "skip-state.json"
        skip_config.write_text(json.dumps({
            "state_file": ".claude/never-written-state.json",
            "close_commit": {"contains": "RITUAL:"},
            "packet_dir": "packets",
            "receiver_checks": [{
                "name": "clean-tree",
                "command": "git diff --quiet && git diff --cached --quiet",
            }],
        }), encoding="utf-8")
        result = subprocess.run(
            ["python", str(open_py), str(filled),
             "--config", str(skip_config),
             "--repo-root", str(repo)],
            text=True, capture_output=True,
        )
        assert result.returncode != 0, "open must fail when state file is missing"
        receipt = json.loads(result.stdout)
        assert receipt["verdict"] == "REJECTED", receipt
        assert receipt.get("state_read", {}).get("status") == "missing", receipt


if __name__ == "__main__":
    expect_structure("fixture-clean.md", True)
    expect_structure("fixture-missing-field.md", False)
    expect_structure("fixture-stale.md", True)
    expect_structure("fixture-failed-probe.md", True)
    placeholder_cases()
    lint_cases()
    repository_cases()
    close_commit_cases()
    claimed_head_cases()
    cli_cases()
    close_session_cases()
    open_session_cases()
    red_check_cases()
    assertions_held_cases()
    cache_hit_and_input_change_cases()
    cache_outside_change_cases()
    cache_directory_inputs_cases()
    cache_failing_never_cached_cases()
    cache_weekly_disagreement_cases()
    cache_no_inputs_fields_cases()
    cache_expand_cases()
    cache_close_shares_cases()
    cache_atomic_write_cases()
    cache_path_confined_cases()
    utf8_check_output_cases()
    utf8_git_output_cases()
    parity_verified, parity_message = duplication_case()
    print(parity_message)
    roster = ("PASS: clean, stale, incomplete, failed-probe, placeholder, "
              "unfailable-check, command-probe, close-commit, close-commit-cli, "
              "claimed-head, claimed-head-cli, receive-mode-config, "
              "close-session, open-session, red-check, assertions-held, "
              "cache-hit, cache-outside, cache-directory, cache-fail, "
              "cache-weekly, cache-no-inputs, cache-expand, cache-close-shared, "
              "cache-atomic, cache-path-confined, utf8-output, utf8-git-output")
    # no-drift appears in the pass roster only when parity was actually
    # compared; a single-card install reports NOT VERIFIED above instead.
    print(roster + ", no-drift" if parity_verified else roster)
