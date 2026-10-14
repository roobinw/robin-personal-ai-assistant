#!/usr/bin/env python3
"""Build one upload-ready ZIP per skill in dist/.

Each ZIP holds the skill folder itself at the top level, which is what
claude.ai and the Gemini app expect. Eval files and caches are left out.

Run from the repo root: python3 tools/build_zips.py
"""

import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = {"evals", "__pycache__"}


def build(skill_dir, dist):
    target = dist / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill_dir.rglob("*")):
            rel = path.relative_to(skill_dir)
            if path.is_dir() or SKIP_DIRS & set(rel.parts) or path.suffix == ".pyc":
                continue
            zf.write(path, pathlib.Path(skill_dir.name) / rel)
    return target


def main():
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    for skill_dir in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        target = build(skill_dir, dist)
        print(f"{target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
