"""Offline release/pin regression: fake CLI, real pin readers, no Git writes/network.

Run: python scripts/test_install_form_expectations.py
The real cold-install check still runs separately in test_install_form.py.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
TARGET = Path(__file__).with_name("test_install_form.py")
spec = importlib.util.spec_from_file_location("install_gate_under_test", TARGET)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
pin = mod.pin

OLD = "a" * 40
NEW = "b" * 40
URL = "https://github.com/MrBinnacle/skills.git"
PATHS = {
    "mrbinnacle-engineering": "skills/engineering",
    "mrbinnacle-orchestration": "skills/orchestration",
    "mrbinnacle-meta": "skills/meta",
    "tips-anywhere": "mods/tips-anywhere",
    "binnacle-hud": "mods/binnacle-hud",
}
OLD_INSTALL = {name: "4.0.0" for name in PATHS if name != "binnacle-hud"}
NEW_INSTALL = {name: "4.1.0" for name in PATHS}
CALLS: list[tuple[str, list[str]]] = []


def catalog(sha: str, names=None) -> dict:
    names = list(PATHS) if names is None else names
    version = "4.0.0" if sha == OLD else "4.1.0"
    return {"name": "mrbinnacle-skills", "plugins": [
        {"name": name, "source": {"source": "git-subdir", "url": URL,
         "path": PATHS[name], "sha": sha, "ref": f"v{version}"}}
        for name in names
    ]}


def history() -> dict:
    data = {}
    for sha, installed in ((OLD, OLD_INSTALL), (NEW, NEW_INSTALL)):
        version = next(iter(installed.values()))
        data[(sha, "package.json")] = {"version": version}
        data[(sha, pin.MANIFEST_REL)] = catalog(sha, list(installed))
        for name in installed:
            data[(sha, f"{PATHS[name]}/{pin.PLUGIN_MANIFEST_REL}")] = {
                "name": name, "version": version,
            }
    return data


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def marketplace(root: Path, sha: str) -> None:
    write_json(root / pin.MANIFEST_REL, catalog(sha))
    write_json(root / "package.json", {"version": "4.1.0", "repository": {"url": URL}})
    for name, path in PATHS.items():
        write_json(root / path / pin.PLUGIN_MANIFEST_REL, {"name": name, "version": "4.1.0"})


def git_reader(data: dict):
    def git(root, *args):
        if args[0] == "show":
            sha, path = args[1].split(":", 1)
            if (sha, path) in data:
                return json.dumps(data[(sha, path)])
        elif args[:2] == ("cat-file", "-e"):
            sha, path = args[2].split(":", 1)
            if (sha, path) in data:
                return ""
        elif args[:2] == ("rev-parse", "--verify"):
            raise pin.PinError("fixture has no tags")
        else:
            raise AssertionError(f"unexpected Git operation: {args}")
        raise pin.PinError(f"missing fixture object: {args}")
    return git


def exercise(label, public_sha, candidate_sha, public_installed, local_installed,
             expected_failure=None, empty_card=None, broken_registry=False,
             broken_catalog=False, receipt="3.1.0") -> None:
    CALLS.clear()
    mod.FAILURES.clear()
    with tempfile.TemporaryDirectory(prefix="install-form-fixture-") as folder:
        root = Path(folder)
        candidate = root / "candidate"
        published_source = root / "published-source"
        marketplace(candidate, candidate_sha)
        marketplace(published_source, public_sha)
        if broken_catalog:
            write_json(candidate / pin.MANIFEST_REL, {"plugins": []})

        def cli(executable, args, env, cwd):
            assert executable == "offline-fake-cli"
            assert env["HOME"] == env["USERPROFILE"]
            assert env["GIT_CONFIG_NOSYSTEM"] == "1"
            assert "IdentityFile=/dev/null" in env["GIT_SSH_COMMAND"]
            assert Path(env["GIT_CONFIG_GLOBAL"]).read_text() == ""
            side = "published" if Path(cwd).name == "published" else "local"
            CALLS.append((side, list(args)))
            stdout = ""
            if args[:3] == ["plugin", "marketplace", "add"]:
                if side == "published":
                    assert args[3] == URL
                    config = Path(env["CLAUDE_CONFIG_DIR"])
                    snapshot = config / "plugins/marketplaces/mrbinnacle-skills"
                    shutil.copytree(published_source, snapshot)
                    write_json(config / "plugins/known_marketplaces.json", {
                        "mrbinnacle-skills": {"installLocation": "" if broken_registry else str(snapshot)}
                    })
                else:
                    assert args[3] == str(candidate)
                stdout = "Successfully added marketplace"
            elif args[:2] == ["plugin", "install"]:
                stdout = "Successfully installed plugin"
            elif args == ["plugin", "list", "--json"]:
                installed = public_installed if side == "published" else local_installed
                rows = []
                for name, version in installed.items():
                    destination = root / "installed" / side / name
                    destination.mkdir(parents=True, exist_ok=True)
                    if name.startswith("mrbinnacle-") and (side, name) != empty_card:
                        card = destination / "example/SKILL.md"
                        card.parent.mkdir(exist_ok=True)
                        card.write_text("fixture card", encoding="utf-8")
                    rows.append({"id": name + "@mrbinnacle-skills", "version": version,
                                 "installPath": str(destination)})
                stdout = json.dumps(rows)
            elif args == ["--version"]:
                stdout = "2.1.319 (Claude Code)"
            else:
                raise AssertionError(f"unexpected CLI command: {args}")
            return subprocess.CompletedProcess([executable, *args], 0, stdout, "")

        with (patch.object(mod, "ROOT", candidate), patch.object(pin, "git", git_reader(history())),
              patch.object(mod, "find_claude", return_value="offline-fake-cli"),
              patch.object(mod, "run_cli", side_effect=cli),
              patch.dict(os.environ, {"INSTALL_FORM_STRICT": "1"}),
              contextlib.redirect_stdout(io.StringIO()) as output):
            mod.live_cold_installs(
                root / "cold",
                [f"claude plugin marketplace add {URL}"],
                [["claude", "plugin", "install", "mrbinnacle-engineering", "--scope", "user"]],
                "2.1.319", receipt,
            )
        if expected_failure:
            assert any(expected_failure in name for name in mod.FAILURES), output.getvalue()
        else:
            assert not mod.FAILURES, output.getvalue()
            assert ("published", ["plugin", "install", "mrbinnacle-engineering", "--scope", "user"]) in CALLS
            for side, sha in (("published", public_sha), ("local", candidate_sha)):
                hud_call = (side, ["plugin", "install", "binnacle-hud"])
                assert (hud_call in CALLS) == (sha == NEW), (label, CALLS)
    assert not root.exists(), "offline fixture cleanup failed"
    print(f"PASS {label}")


exercise("release PR: both pins old, candidate manifests new", OLD, OLD, OLD_INSTALL, OLD_INSTALL)
exercise("pin PR: published old, candidate new with HUD", OLD, NEW, OLD_INSTALL, NEW_INSTALL)
exercise("after pin: both surfaces require HUD 4.1.0", NEW, NEW, NEW_INSTALL, NEW_INSTALL)
for side in ("published", "local"):
    label = "published marketplace's pinned" if side == "published" else "its pinned"
    for mutation in ("wrong-version", "missing-HUD", "extra-plugin"):
        changed = dict(NEW_INSTALL)
        if mutation == "wrong-version":
            changed = {name: "4.0.0" for name in changed}  # internally consistent but wrong
        elif mutation == "missing-HUD":
            del changed["binnacle-hud"]
        else:
            changed["unexpected-plugin"] = "4.1.0"
        exercise(f"reject {side} {mutation}", NEW, NEW,
                 changed if side == "published" else NEW_INSTALL,
                 changed if side == "local" else NEW_INSTALL, expected_failure=label)
    exercise(f"reject {side} missing card content", NEW, NEW, NEW_INSTALL, NEW_INSTALL,
             expected_failure="carries cards", empty_card=(side, "mrbinnacle-engineering"))
exercise("reject malformed published snapshot evidence", OLD, OLD, OLD_INSTALL, OLD_INSTALL,
         expected_failure="published marketplace pins can be resolved", broken_registry=True)
exercise("reject empty candidate expectations", OLD, NEW, OLD_INSTALL, NEW_INSTALL,
         expected_failure="checked-out marketplace pins can be resolved", broken_catalog=True)
exercise("reject lead-dated receipt", OLD, OLD, OLD_INSTALL, OLD_INSTALL,
         expected_failure="Verified forms plugin version", receipt="4.1.0")

# Expectations fail closed before the CLI result can define what should exist.
with tempfile.TemporaryDirectory(prefix="install-form-metadata-") as folder:
    root = Path(folder)
    marketplace(root, OLD)
    for mutation in ("bad-entry", "missing-name", "duplicate-name", "bad-source", "missing-sha",
                     "bad-path", "rooted-path", "drive-relative-path", "wrong-url", "wrong-ref", "missing-object", "bad-version",
                     "bad-pinned-catalog", "missing-existing-plugin", "wrong-pinned-version",
                     "missing-entering-manifest", "all-entering", "mixed-versions"):
        marketplace(root, OLD)
        data = history()
        cat = catalog(OLD)
        first = cat["plugins"][0]
        if mutation == "bad-entry": cat["plugins"][0] = "not an entry"
        elif mutation == "missing-name": del first["name"]
        elif mutation == "duplicate-name": cat["plugins"].append(copy.deepcopy(first))
        elif mutation == "bad-source": first["source"] = "./relative"
        elif mutation == "missing-sha": del first["source"]["sha"]
        elif mutation == "bad-path": first["source"]["path"] = "../outside"
        elif mutation == "rooted-path": first["source"]["path"] = "/outside"
        elif mutation == "drive-relative-path": first["source"]["path"] = "C:outside"
        elif mutation == "wrong-url": first["source"]["url"] = "https://example.invalid/repo.git"
        elif mutation == "wrong-ref": first["source"]["ref"] = "v3.0.0"
        elif mutation == "missing-object": del data[(OLD, "package.json")]
        elif mutation == "bad-version": data[(OLD, "package.json")]["version"] = 4
        elif mutation == "bad-pinned-catalog": data[(OLD, pin.MANIFEST_REL)]["plugins"].append("bad")
        elif mutation == "missing-existing-plugin": del data[(OLD, "skills/engineering/" + pin.PLUGIN_MANIFEST_REL)]
        elif mutation == "wrong-pinned-version": data[(OLD, "skills/engineering/" + pin.PLUGIN_MANIFEST_REL)]["version"] = "9.0.0"
        elif mutation == "missing-entering-manifest": (root / PATHS["binnacle-hud"] / pin.PLUGIN_MANIFEST_REL).unlink()
        elif mutation == "all-entering": cat["plugins"] = [cat["plugins"][-1]]
        elif mutation == "mixed-versions": cat["plugins"][-1] = catalog(NEW)["plugins"][-1]
        write_json(root / pin.MANIFEST_REL, cat)
        with patch.object(mod, "ROOT", root), patch.object(pin, "git", git_reader(data)):
            try:
                mod.install_expectations(root)
            except (ValueError, pin.PinError):
                pass
            else:
                raise AssertionError(f"accepted {mutation}")
        print(f"PASS reject metadata {mutation}")

    marketplace(root, OLD)
    with (patch.object(mod, "ROOT", root), patch.object(pin, "git", git_reader(history())),
          patch.object(pin, "expected_release", return_value=pin.Release(NEW, "4.1.0", False))):
        # Reachability is not freshness: old source pins resolve, but the separate
        # unchanged checker still refuses them once the new release has merged.
        assert mod.install_expectations(root)[0] == OLD_INSTALL
        result = pin.check(root)
        assert any("sha" in error for error in result.errors), result
        assert any("ref" in error for error in result.errors), result
    print("PASS separate pin checker still rejects stale candidate pins")

print("PASS offline regression: 33 cases; no CLI install, Git write, network, or model call")
