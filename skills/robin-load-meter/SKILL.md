---
name: robin-load-meter
description: Scores a week in story points (1 per calendar hour, 0.25 per task), green to red, and counts free evenings. Use for "how busy is my week", "load meter", free evenings, or after booking.
license: MIT
compatibility: Needs read access to a calendar and a task app. The scoring script needs Python 3.9+; without code execution, apply the rules by hand.
metadata:
  version: "2.0.0"
  author: roobinw
---

# Robin Load Meter

The Load Meter turns a week into one number so overload is visible before it happens: 1 point per hour of plans, 0.25 per task, compared with the user's green and red thresholds.

Values written as `settings.<key>` come from the user's `Robin settings` document (see `robin-sidekick-assistant`). If there are no settings, use the defaults in [references/scoring-rules.md](references/scoring-rules.md) and say so.

## Steps

1. **Pick the week.** "This week", "next week" or the week of a new booking. Weeks start on `settings.week_start` in `settings.timezone`. Use `mode: upcoming` for a week ahead and `mode: past` for a week behind.
2. **Fetch the data.** All calendar events overlapping the week (with all-day flag, "show as free" flag, the user's response, event type and calendar name) and all tasks due in the week. For a past week, also tasks completed in it.
3. **Score it.**
   - If you can run code: write the input JSON described in [references/scoring-rules.md](references/scoring-rules.md) and run `python3 scripts/load_meter.py input.json`. Use its numbers as they are.
   - If you cannot run code: apply the rules in [references/scoring-rules.md](references/scoring-rules.md) by hand, and show a per-day table so the user can check it.
4. **Report** in this shape:

   ```
   Next week: 28 points, orange (red starts at 33, 5 to go).
   Mon 2.5 · Tue 3 · Wed 2.25 · Thu 4.25 · Fri 4 · Sat 8.5 · Sun 3.5
   Free evenings: 2 of 3 wanted (Sat, Sun).
   Biggest items: Moving help for Tom (8 h), Concert (3.5 h), Book club (3 h).
   ```

   Add one line per double booking. Leave out lines that have nothing to say.
5. **Act on overload.** If a new event or task moved the week into orange or red, or free evenings fell below `settings.load_meter.min_free_evenings`, say so straight away and ask what to drop or move. Suggest the one or two easiest items. Change nothing until the user decides.

## Rules in brief

The full rules, edge cases and a worked example are in [references/scoring-rules.md](references/scoring-rules.md).

- Timed events: 1 point per hour (`settings.load_meter.event_points_per_hour`). Overlapping events count once.
- Tasks: 0.25 points each (`settings.load_meter.task_points`). Tasks without a due date do not count.
- Not counted: declined events, events shown as free, working-location, birthday and out-of-office events, items in `settings.load_meter.ignored_calendar_items` or `ignored_calendars`, and time inside `settings.working_hours`.
- All-day events: 0 points unless `settings.load_meter.all_day_points` says otherwise.
- A task that also has a calendar block counts once, as the event.
- Bands: green under `green_below`; orange from `green_below` up to but not including `red_from`; red at `red_from` or more.
- A free evening has no counted event touching `settings.evening_window` (19:00–23:00 by default).

## Gotchas

- Read Google Tasks due dates literally (`2026-10-14T00:00:00.000Z` is 14 October). Converting the time zone moves tasks to the wrong day.
- Never guess events you could not fetch. If a calendar or task list is missing, score what you have and name what is missing.
- The number is a guide for the user's own decisions. Never move or cancel anything because of a score.
