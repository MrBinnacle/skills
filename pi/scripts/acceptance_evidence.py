"""Controller-side evidence for the six fixed acceptance fixtures, not a sandbox.

Arithmetic evaluation deliberately supports only plain two-argument arithmetic returns.
Unsupported implementations are unverified, not silently accepted or executed.
"""
from __future__ import annotations

import ast
import hashlib
import json
import operator
from pathlib import Path
import shlex
import sys

IGNORED = {".git", "__pycache__", ".pytest_cache"}


def snapshot(root: Path) -> str | None:
    """Hash fixture files, including tests; refuse links and unreadable inputs."""
    files = []
    try:
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root)
            if any(part in IGNORED for part in rel.parts):
                continue
            if path.is_symlink():
                return None
            if path.is_file():
                files.append((rel.as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
        return hashlib.sha256(json.dumps(files, separators=(",", ":")).encode()).hexdigest()
    except OSError:
        return None


def capture_event(event: dict, root: Path) -> dict:
    """Called by the RPC reader before queueing; overwrite, never trust incoming evidence."""
    captured = dict(event)
    captured.pop("acceptance_controller", None)
    if event.get("type") in {"tool_execution_start", "tool_execution_end", "agent_settled"}:
        captured["acceptance_controller"] = {"version": 1, "snapshot": snapshot(root)}
    return captured


def direct_pytest(command: str) -> bool:
    """Only the fixture's requested command, not prose, shell operators or -c code."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    return (len(argv) == 4 and argv[0] in {"python", "python3", sys.executable}
            and argv[1:] == ["-m", "pytest", "-q"])


def numeric_function(source: str, name: str, expected) -> bool:
    """Evaluate a restricted AST on asymmetric, negative, zero and fractional cases."""
    binary = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv}

    def evaluate(node, values):
        if isinstance(node, ast.Name) and node.id in values:
            return values[node.id]
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in binary:
            return binary[type(node.op)](evaluate(node.left, values), evaluate(node.right, values))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = evaluate(node.operand, values)
            return -value if isinstance(node.op, ast.USub) else value
        raise ValueError("unsupported expression")

    try:
        tree = ast.parse(source)
        matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
        if len(matches) != 1:
            return False
        fn = matches[0]
        args = fn.args
        if (fn.decorator_list or args.defaults or args.kw_defaults or args.kwonlyargs
                or args.posonlyargs or args.vararg or args.kwarg or len(args.args) != 2
                or len(fn.body) != 1 or not isinstance(fn.body[0], ast.Return)):
            return False
        # Module-level execution/rebinding would change the meaning of this function.
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                return False
            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if (node.decorator_list or node.args.defaults or node.args.kw_defaults
                    or node.returns or getattr(node, "type_params", [])
                    or any(arg.annotation for arg in all_args)
                    or (node.args.vararg and node.args.vararg.annotation)
                    or (node.args.kwarg and node.args.kwarg.annotation)):
                return False
        names = [node.name for node in tree.body]
        if len(names) != len(set(names)):
            return False
        for a, b in ((7, 2), (2, 7), (-3, 4), (0, 0), (1.5, .25)):
            actual = evaluate(fn.body[0].value, {args.args[0].arg: a, args.args[1].arg: b})
            if type(actual) not in (int, float) or actual != expected(a, b):
                return False
        return True
    except (SyntaxError, ValueError, TypeError, ArithmeticError):
        return False


def existing_tests_preserved(source: str, original: str) -> bool:
    """Preserve original imports/test ASTs, not only lines containing 'test_'."""
    try:
        old, new = ast.parse(original), ast.parse(source)
        for node in old.body:
            identity = ast.dump(node, include_attributes=False)
            if sum(ast.dump(candidate, include_attributes=False) == identity for candidate in new.body) != 1:
                return False
            if isinstance(node, ast.FunctionDef):
                if sum(isinstance(candidate, ast.FunctionDef) and candidate.name == node.name
                       for candidate in new.body) != 1:
                    return False
        return True
    except SyntaxError:
        return False


def subtract_test_present(source: str) -> bool:
    """Recognize a concrete asymmetric assertion in a top-level pytest test function."""
    try:
        tree = ast.parse(source)
        if any(not isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)) for node in tree.body):
            return False
        # The recognized call must resolve to the sole direct calc.subtract import.
        # Allowed statement types alone do not prevent a function/import from shadowing it.
        bindings = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "subtract":
                bindings.append(False)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name == "*":
                        return False
                    bound = alias.asname or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name)
                    if bound == "subtract":
                        bindings.append(isinstance(node, ast.ImportFrom) and node.level == 0
                                        and node.module == "calc" and alias.name == "subtract"
                                        and alias.asname is None)
        if bindings != [True]:
            return False
        names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        if len(names) != len(set(names)):
            return False
        for fn in tree.body:
            if (not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test_") or fn.decorator_list
                    or fn.args.args or fn.args.posonlyargs or fn.args.kwonlyargs or fn.args.vararg
                    or fn.args.kwarg or len(fn.body) != 1):
                continue
            for node in fn.body:
                if not isinstance(node, ast.Assert) or not isinstance(node.test, ast.Compare):
                    continue
                comparison = node.test
                call = comparison.left
                if (len(comparison.ops) != 1 or not isinstance(comparison.ops[0], ast.Eq)
                        or not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name)
                        or call.func.id != "subtract" or len(call.args) != 2 or call.keywords):
                    continue
                a, b = (ast.literal_eval(arg) for arg in call.args)
                expected = ast.literal_eval(comparison.comparators[0])
                if (type(a) in (int, float) and type(b) in (int, float) and a != b
                        and type(expected) in (int, float) and expected == a - b):
                    return True
        return False
    except (SyntaxError, ValueError, TypeError):
        return False


def completed_checks(events: list[dict], text_of, counts) -> list[dict]:
    """Pair starts/ends by id, require real pytest output and a stable fixture snapshot."""
    starts = {}
    checks = []
    for index, event in enumerate(events):
        call = event.get("toolCallId")
        if event.get("type") == "tool_execution_start" and call:
            starts[call] = (index, event)
        elif event.get("type") == "tool_execution_end" and call in starts:
            start_index, start = starts.pop(call)
            command = (start.get("args") or {}).get("command", "")
            before = start.get("acceptance_controller") or {}
            after = event.get("acceptance_controller") or {}
            output = text_of((event.get("result") or {}).get("content"))
            if (start.get("toolName") in {"bash", "powershell"} and direct_pytest(command)
                    and event.get("toolName") == start.get("toolName")
                    and before.get("version") == after.get("version") == 1
                    and before.get("snapshot") and before["snapshot"] == after.get("snapshot")
                    and any(passed + failed > 0 for passed, failed in counts(output))):
                checks.append({"command": command, "index": index, "start_index": start_index,
                               "snapshot": after["snapshot"], "is_error": event.get("isError", False)})
    return checks
