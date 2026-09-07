#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validator", HERE / "validate_packet.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

PASSING_COMMAND = "git rev-parse HEAD"
FAILING_COMMAND = "exit 1"


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
    parity_verified, parity_message = duplication_case()
    print(parity_message)
    roster = ("PASS: clean, stale, incomplete, failed-probe, placeholder, "
              "unfailable-check, command-probe, close-commit, close-commit-cli, "
              "claimed-head, claimed-head-cli, receive-mode-config, "
              "close-session, open-session, red-check, assertions-held")
    # no-drift appears in the pass roster only when parity was actually
    # compared; a single-card install reports NOT VERIFIED above instead.
    print(roster + ", no-drift" if parity_verified else roster)
