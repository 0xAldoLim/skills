#!/usr/bin/env python3
"""Validate filesystem skill discovery, metadata, links, and invocation hints."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any


MAJOR = {"ctf-ai-ml", "ctf-crypto", "ctf-forensics", "ctf-malware", "ctf-misc", "ctf-osint", "ctf-pwn", "ctf-reverse", "ctf-web"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, ["missing opening frontmatter delimiter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["missing closing frontmatter delimiter"]
    try:
        import yaml
        metadata = yaml.safe_load('\n'.join(lines[1:end]))
        if not isinstance(metadata, dict):
            return {}, ['frontmatter must be a YAML mapping']
    except ImportError:
        return {}, ['install validation dependency PyYAML']
    except yaml.YAMLError as error:
        return {}, [f'invalid YAML frontmatter: {error}']
    for field in ("name", "description"):
        if not metadata.get(field):
            errors.append(f"missing required frontmatter field: {field}")
    return metadata, errors


def validate_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r'(?ms)^\s*```[^\n]*\n.*?^\s*```\s*$', '', text)
        for raw in LINK_RE.findall(text):
            target = raw.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            # Code such as func(arg), array[index](arg), or payload syntax can
            # resemble Markdown. Repository-local links use path-safe bytes.
            if not re.fullmatch(r"(?:\.\.?/)?[A-Za-z0-9_./-]+(?:#[A-Za-z0-9_.%~-]+)?", target):
                continue
            relative = target.split("#", 1)[0]
            suffix = Path(relative).suffix.lower()
            if suffix not in {".md", ".sh", ".py", ".json", ".yaml", ".yml", ".toml"} and not (path.parent / relative).exists():
                continue
            if relative and not (path.parent / relative).resolve().exists():
                errors.append(f"{path.relative_to(root)}: missing relative link target {relative}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, Path] = {}
    skills = sorted(root.glob("*/SKILL.md"))
    if not skills:
        return ["no discoverable SKILL.md files"]
    for path in skills:
        metadata, metadata_errors = parse_frontmatter(path)
        errors.extend(f"{path.relative_to(root)}: {error}" for error in metadata_errors)
        name = str(metadata.get("name", ""))
        if name and name != path.parent.name:
            errors.append(f"{path.relative_to(root)}: name {name!r} does not match directory {path.parent.name!r}")
        if name in seen:
            errors.append(f"duplicate skill identifier {name!r}: {seen[name].relative_to(root)} and {path.relative_to(root)}")
        elif name:
            seen[name] = path
        if name in MAJOR:
            body = path.read_text(encoding="utf-8")
            if "allowed-tools" in metadata or "Claude Code" in str(metadata.get("compatibility", "")):
                errors.append(f"{name}: obsolete agent-specific execution metadata")
            invocation = metadata.get("metadata", {}).get("user-invocable")
            if str(invocation).lower() != "true":
                errors.append(f"{name}: explicit invocation must be enabled")
            for requirement in ("../docs/SCOPE.md", "../docs/INSTANCE_HEALTH.md", "../docs/WORKFLOW.md", "../docs/LEARNING.md", "--auto", "at most two", "verified", "exact active"):
                if requirement not in body:
                    errors.append(f"{name}: missing execution contract {requirement!r}")
            index = path.parent / "INDEX.md"
            agent = path.parent / "agents" / "openai.yaml"
            if not index.is_file():
                errors.append(f"{name}: missing generated INDEX.md")
            if not agent.is_file():
                errors.append(f"{name}: missing direct-invocation agents/openai.yaml")
            else:
                agent_text = agent.read_text(encoding="utf-8")
                import yaml
                try:
                    value = yaml.safe_load(agent_text)
                    if not isinstance(value, dict) or not isinstance(value.get('interface'), dict):
                        errors.append(f'{name}: invalid agent interface YAML')
                except yaml.YAMLError as error:
                    errors.append(f'{name}: invalid agent YAML: {error}')
                if f"${name}" not in agent_text:
                    errors.append(f"{name}: default_prompt must explicitly mention ${name}")
                if "allow_implicit_invocation: true" not in agent_text:
                    errors.append(f"{name}: implicit invocation policy is not enabled")
    missing = MAJOR - seen.keys()
    errors.extend(f"missing required category skill: {name}" for name in sorted(missing))
    if "solve-challenge" not in seen:
        errors.append("missing dispatcher skill: solve-challenge")
    errors.extend(validate_links(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
