"""Dependency lint for the Pi ports under pi/skills/.

Each port must load and work on its own. The lint fails when a port:
  - links to a local file that does not exist,
  - links to, or names, a skill outside the ported set,
  - names a Claude Code tool, hook, or path,
  - references a harness config file,
  - ships an auxiliary file that SKILL.md cannot reach through links,
  - has CRLF line endings,
  - has frontmatter Pi would reject or that does not match its directory.

Usage: python pi/scripts/lint_pi_skills.py [skills_dir]
Exit 0 when clean, 1 with one line per finding otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DIR = REPO / "pi" / "skills"

ALLOWED_CROSS_LINKS = {("vacuous-check", "mocked-stub")}

# Skills that exist in this repository, or were named in the porting plan, but are
# not in the ported set. A port that names one of them dangles in a Pi install.
EXTRA_KNOWN_SKILLS = {
    "disposition-schema", "brief-ids", "im-down", "im-up", "clirunner-env",
    "detached-child", "stale-deploy", "linkcheck-throttle", "sdk-via-openrouter",
    "prefill-rejection", "frontend-slop", "equivalent-mutant", "skill-family-curation",
    "steering-head", "closure-mode", "dead-predicate", "pretooluse-prose", "blocked-form",
    "skill-reachability", "agent-snapshot", "cwd-drift", "worktree-cwd",
    "halt-as-deliverable", "honesty-first", "poteto-mode", "write-a-skill", "tdd",
}

CLAUDE_CODE_PATTERNS = [
    (r"\bClaude Code\b", "names Claude Code"),
    (r"\.claude\b", "names a .claude path"),
    (r"\bCLAUDE\.md\b", "names CLAUDE.md"),
    (r"\b(Bash|Agent|Task|Skill|SendMessage|TodoWrite|AskUserQuestion|WebFetch|WebSearch"
     r"|NotebookEdit|MultiEdit|Glob|Grep|Read|Write|Edit)\s+tool\b", "names a Claude Code tool"),
    (r"`(Bash|Agent|Task|Skill|SendMessage|TodoWrite|AskUserQuestion|MultiEdit|Glob|Grep)`",
     "names a Claude Code tool"),
    (r"(?<!Git )\bBash\b", "names the Claude Code Bash tool (Pi's tool is `bash`)"),
    (r"(?<![\w/.-])claude\b(?!-)", "names the claude CLI"),
    (r"\bsubagent_type\b", "names a Claude Code tool parameter"),
    (r"\b(PreToolUse|PostToolUse|UserPromptSubmit|SessionStart|SubagentStop|PreCompact)\b",
     "names a Claude Code hook event"),
    (r"\$ARGUMENTS\b", "uses $ARGUMENTS, which Pi does not substitute"),
]

CONFIG_PATTERNS = [
    (r"\bmodels\.json\b", "references models.json"),
    (r"\bpstack\b", "references pstack"),
    (r"\bplugin\.json\b|\bmarketplace\.json\b|\.claude-plugin\b", "references plugin config"),
    (r"\bsettings\.local\.json\b|\bhooks\.json\b", "references a harness config file"),
    (r"/setup-[a-z]", "references a setup skill"),
]

# A backticked kebab-case name on a line that talks about skills is a skill reference,
# even when the skill exists nowhere this lint can read (retired, private, third-party).
SKILL_CONTEXT_RE = re.compile(r"see also|related|\bcard\b|\bskill\b|sibling|companion", re.I)
KEBAB_TOKEN_RE = re.compile(r"`((?!claude-)[a-z0-9]+(?:-[a-z0-9]+)+)`")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def known_skills(ported: set[str]) -> set[str]:
    names = set(EXTRA_KNOWN_SKILLS)
    for pattern in ("skills/*/*/SKILL.md", "_quarantine/*/SKILL.md"):
        names.update(p.parent.name for p in REPO.glob(pattern))
    return names - ported


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def lint(skills_dir: Path) -> list[str]:
    findings: list[str] = []
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    ported = {p.name for p in skill_dirs}
    outside = known_skills(ported)
    outside_re = re.compile(
        r"(?<![\w-])(" + "|".join(sorted(map(re.escape, outside), key=len, reverse=True)) + r")(?![\w-])"
    )

    for skill in skill_dirs:
        entry = skill / "SKILL.md"
        if not entry.is_file():
            findings.append(f"{skill.name}: missing SKILL.md")
            continue

        fm = frontmatter(entry.read_text(encoding="utf-8"))
        if fm is None:
            findings.append(f"{skill.name}/SKILL.md: missing or unterminated frontmatter")
        else:
            name, desc = fm.get("name", ""), fm.get("description", "").strip("\"'")
            if name != skill.name:
                findings.append(f"{skill.name}/SKILL.md: name '{name}' does not match directory")
            if not NAME_RE.match(name) or len(name) > 64:
                findings.append(f"{skill.name}/SKILL.md: name '{name}' is not a valid Pi skill name")
            if not desc:
                findings.append(f"{skill.name}/SKILL.md: missing description (Pi will not load it)")
            elif len(desc) > 1024:
                findings.append(f"{skill.name}/SKILL.md: description is {len(desc)} chars (max 1024)")

        reachable: set[Path] = set()
        queue = [entry]
        for md in sorted(skill.rglob("*.md")):
            rel = md.relative_to(skills_dir).as_posix()
            text = md.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                for pattern, why in CLAUDE_CODE_PATTERNS + CONFIG_PATTERNS:
                    if re.search(pattern, line):
                        findings.append(f"{rel}:{lineno}: {why}")
                for m in outside_re.finditer(line):
                    findings.append(f"{rel}:{lineno}: names skill '{m.group(1)}' outside the ported set")
                if SKILL_CONTEXT_RE.search(line):
                    for m in KEBAB_TOKEN_RE.finditer(line):
                        if m.group(1) not in ported and not outside_re.fullmatch(m.group(1)):
                            findings.append(f"{rel}:{lineno}: names '{m.group(1)}' as a skill outside the ported set")
                for m in LINK_RE.finditer(line):
                    target = m.group(1)
                    if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                        if "github.com" in target and re.search(r"/(skills|_quarantine)/", target):
                            findings.append(f"{rel}:{lineno}: links into the skills repository by URL: {target}")
                        continue
                    path = (md.parent / target.split("#", 1)[0]).resolve()
                    if not path.exists():
                        findings.append(f"{rel}:{lineno}: broken link {target}")
                        continue
                    try:
                        other = path.relative_to(skills_dir.resolve()).parts[0]
                    except ValueError:
                        findings.append(f"{rel}:{lineno}: link leaves the ported set: {target}")
                        continue
                    if other != skill.name and (skill.name, other) not in ALLOWED_CROSS_LINKS:
                        findings.append(f"{rel}:{lineno}: links to another skill '{other}' (not allowed)")

        while queue:
            md = queue.pop()
            if md in reachable:
                continue
            reachable.add(md)
            for m in LINK_RE.finditer(strip_code_fences(md.read_text(encoding="utf-8"))):
                target = m.group(1).split("#", 1)[0]
                if not target or re.match(r"^[a-z]+:", target):
                    continue
                path = (md.parent / target).resolve()
                if path.is_file() and path.suffix == ".md" and skill.resolve() in path.parents:
                    queue.append(path)
        for f in sorted(p for p in skill.rglob("*") if p.is_file()):
            if b"\r\n" in f.read_bytes():
                findings.append(f"{f.relative_to(skills_dir).as_posix()}: CRLF line endings (the repository uses LF)")
            if f.resolve() not in {r.resolve() for r in reachable}:
                findings.append(f"{f.relative_to(skills_dir).as_posix()}: not reachable from SKILL.md (drop it or link it)")

    return findings


def main() -> int:
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    findings = lint(skills_dir)
    for f in findings:
        print(f)
    print(f"{len(findings)} finding(s) across {sum(1 for p in skills_dir.iterdir() if p.is_dir())} skill(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
