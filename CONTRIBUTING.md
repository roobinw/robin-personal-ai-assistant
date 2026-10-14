# Contributing to Robin

Thanks for helping. Robin is plain Markdown plus a few standard-library Python scripts, so most changes need no setup.

## Layout

```
skills/<skill-name>/SKILL.md      the instructions an assistant loads
skills/<skill-name>/references/   detail loaded only when needed
skills/<skill-name>/scripts/      deterministic helpers (Python 3.9+, standard library only)
skills/<skill-name>/evals/        behaviour checks and trigger queries
tests/                            unit tests for the scripts
tools/                            validator and ZIP builder
```

## Before you open a pull request

```bash
pip install pyyaml skills-ref
python3 tools/validate_skills.py                         # repo rules
for d in skills/*/; do agentskills validate "$d"; done    # Agent Skills spec
python3 -m unittest discover tests                       # scripts
```

CI runs the same checks.

## House rules

- Keep each `SKILL.md` under 500 lines. Move detail into `references/`, linked straight from `SKILL.md`.
- Descriptions stay under 200 characters, in the third person: what the skill does, then when to use it.
- Personal values belong in the user's `Robin settings` document, never in the skill files.
- Every new behaviour gets an example or an eval case. A change to scoring needs a unit test.
- Bump `metadata.version` in all four skills, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the README badge together, and add a CHANGELOG entry.

## Adding an adapter

Copy `skills/robin-sidekick-assistant/references/adapters/google-workspace.md` and fill in your apps' limits: how repeats work, which calendar fields map to the Load Meter input, and where settings and the log can live. Link it from `SKILL.md` and the README's "Works with" table.
