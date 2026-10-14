#!/usr/bin/env python3
"""Check every skills/*/SKILL.md against the Agent Skills spec and this repo's rules.

Run from the repo root: python3 tools/validate_skills.py
Needs PyYAML (pip install pyyaml). Exits 1 on any error.
"""

import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Claude's upload page caps descriptions at 200 characters; the spec allows 1,024.
MAX_DESCRIPTION = 200
LINK_RE = re.compile(r"\]\(([^)#\s]+)\)|`((?:references|scripts|assets)/[^`\s]+)`")


def check_skill(skill_dir, plugin_version):
    errors = []
    path = skill_dir / "SKILL.md"
    if not path.exists():
        return [f"{skill_dir.name}: SKILL.md missing"]
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return [f"{skill_dir.name}: frontmatter missing"]
    meta, body = yaml.safe_load(match.group(1)), match.group(2)
    where = skill_dir.name

    unknown = set(meta) - ALLOWED_KEYS
    if unknown:
        errors.append(f"{where}: unknown frontmatter keys {sorted(unknown)}")
    name = str(meta.get("name", ""))
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{where}: name {name!r} must be lowercase letters, digits and single hyphens, max 64")
    if name != skill_dir.name:
        errors.append(f"{where}: name {name!r} must match its folder name")
    if "anthropic" in name or "claude" in name:
        errors.append(f"{where}: name must not contain 'anthropic' or 'claude'")
    desc = str(meta.get("description", ""))
    if not desc or len(desc) > MAX_DESCRIPTION:
        errors.append(f"{where}: description is {len(desc)} characters (1-{MAX_DESCRIPTION})")
    if re.search(r"<[^>]+>", desc + name):
        errors.append(f"{where}: name and description must not contain XML tags")
    if len(str(meta.get("compatibility", ""))) > 500:
        errors.append(f"{where}: compatibility is over 500 characters")
    metadata = meta.get("metadata") or {}
    if not all(isinstance(v, str) for v in metadata.values()):
        errors.append(f"{where}: metadata values must be strings")
    if plugin_version and metadata.get("version") != plugin_version:
        errors.append(f"{where}: metadata.version {metadata.get('version')!r} != plugin version {plugin_version!r}")
    if meta.get("license") != "MIT":
        errors.append(f"{where}: license should be MIT")

    lines = text.count("\n") + 1
    if lines > 500:
        errors.append(f"{where}: SKILL.md is {lines} lines (max 500)")
    if len(body) / 4 > 5000:
        errors.append(f"{where}: SKILL.md body is about {len(body) // 4} tokens (max 5000)")

    for m in LINK_RE.finditer(text):
        target = m.group(1) or m.group(2)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (skill_dir / target).exists():
            errors.append(f"{where}: link to missing file {target}")
    return errors


def main():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    errors = []
    if market["plugins"][0].get("version") not in (None, plugin["version"]):
        errors.append("marketplace.json plugin version differs from plugin.json")
    skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    if not skill_dirs:
        errors.append("no skills found")
    for skill_dir in skill_dirs:
        errors.extend(check_skill(skill_dir, plugin["version"]))
    if (ROOT / "SKILL.md").exists():
        errors.append("SKILL.md at the repo root would shadow skills/ for installers")
    for e in errors:
        print(f"error: {e}")
    print(f"checked {len(skill_dirs)} skills: {'FAILED' if errors else 'ok'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
