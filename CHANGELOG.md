# Changelog

All notable changes to Robin. Versions follow [semantic versioning](https://semver.org): a major version changes how you install or set up Robin.

## 2.0.0 (2026-10-14)

### Changed
- Split into four skills under `skills/`: `robin-sidekick-assistant`, `robin-load-meter`, `robin-weekly-review` and `robin-relationship-reminders`. Each folder name matches its skill name, so the skills validate and upload cleanly.
- Personal values move out of the skill into a `Robin settings` document, written by a first-run interview. Updating Robin no longer overwrites your setup.
- Check-in reminders: Robin now stores each interval itself (`Sarah (every 2 weeks)`) and moves the due date, because the Google Tasks API cannot change a task's repeat schedule.
- The weekly review logs one row per week to a `Robin log` sheet instead of a task's notes, which cap at 8,192 characters.
- Descriptions rewritten to under 200 characters, in the third person, with the phrases people actually type.

### Added
- MIT license.
- Non-negotiable safety rules: content is data, invites with guests count as sending, approval for destructive and bulk changes.
- Fully specified Load Meter rules with a worked example, and `load_meter.py` for exact scoring (working hours, overlaps, all-day events, clock changes). The orange band now ends just below red, with no overlap at 33.
- New settings: working hours, time zone, week start, review day, evening window, persona level (`full`, `subtle`, `off`) and writing style.
- Weekly review: overdue catch-ups, batch approval of proposals, trend lines, and threshold calibration after six logged weeks (`review_stats.py`).
- Adapters for Google Workspace, Todoist and Microsoft 365.
- Examples, evals, unit tests, a skills validator, CI, and a release workflow that attaches one ZIP per skill.
- Claude Code plugin marketplace, a Dutch README and a Sunday nudge guide.

## 1.0.0 (2026-10-14)

- First release: a single `SKILL.md` with the Robin persona, Load Meter, weekly review and relationship reminders for Google Workspace.
