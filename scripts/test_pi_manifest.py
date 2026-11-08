"""Pi package manifest contract.

`pi install git:github.com/MrBinnacle/skills` reads the `pi` key of the root
`package.json`. Without that key Pi loads the 14 cards from `skills/` and none
of the extensions in `mechanisms/` (observed with Pi 1.5.0 on 2026-11-08).

This suite checks the published bytes, not a Pi run:
1. The keyword `pi-package` is present.
2. The declared skill paths hold every shipped card and no other `SKILL.md`.
3. The declared extension globs match exactly the `mechanisms/*/index.ts` files.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_scoreboard import iter_skill_dirs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def declared(manifest: dict, key: str) -> list[str]:
    value = manifest.get("pi", {}).get(key)
    if not isinstance(value, list) or not value:
        raise AssertionError(f"package.json pi.{key} must be a non-empty list")
    return value


def check(root: Path) -> list[str]:
    manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
    errors = []
    if "pi-package" not in manifest.get("keywords", []):
        errors.append("package.json keywords lacks pi-package")
    try:
        skill_paths = declared(manifest, "skills")
        extension_globs = declared(manifest, "extensions")
    except AssertionError as exc:
        return errors + [str(exc)]
    loaded = {p.parent.resolve() for d in skill_paths for p in (root / d).rglob("SKILL.md")}
    shipped = {p.resolve() for p in iter_skill_dirs(root)}
    errors += [f"shipped card not under pi.skills: {p.name}" for p in sorted(shipped - loaded)]
    errors += [f"pi.skills loads an unshipped card: {p.name}" for p in sorted(loaded - shipped)]
    matched = {p.resolve() for g in extension_globs for p in root.glob(g.removeprefix("./"))}
    present = {p.resolve() for p in (root / "mechanisms").glob("*/index.ts")}
    errors += [f"mechanism not under pi.extensions: {p.parent.name}" for p in sorted(present - matched)]
    errors += [f"pi.extensions matches a non-mechanism file: {p}" for p in sorted(matched - present)]
    return errors


def main() -> int:
    errors = check(ROOT)
    for e in errors:
        print(f"FAIL {e}")
    print("PASS pi manifest" if not errors else f"{len(errors)} failure(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
