# Load Meter scoring rules

These rules are what `scripts/load_meter.py` implements. When scoring by hand, follow them exactly.

## Contents

- Defaults
- Script input
- Rules
- Worked example

## Defaults

| Setting | Default |
| --- | --- |
| `timezone` | the user's local zone |
| `week_start` | monday |
| `working_hours` | none (Robin settings ships Mon–Fri 09:00–17:00) |
| `evening_window` | 19:00–23:00 |
| `min_free_evenings` | 3 |
| `green_below` / `red_from` | 27 / 33 |
| `event_points_per_hour` / `task_points` | 1 / 0.25 |
| `all_day_points` | 0 |
| `ignored_calendar_items` / `ignored_calendars` | none |

## Script input

```json
{
  "settings": {
    "timezone": "Europe/Amsterdam",
    "week_start": "monday",
    "working_hours": {"days": ["mon", "tue", "wed", "thu", "fri"], "start": "09:00", "end": "17:00"},
    "evening_window": {"start": "19:00", "end": "23:00"},
    "min_free_evenings": 3,
    "green_below": 27,
    "red_from": 33,
    "ignored_calendar_items": ["Partner's gym"]
  },
  "week_of": "2026-10-12",
  "mode": "upcoming",
  "events": [
    {"title": "Dinner with Sarah", "start": "2026-10-12T19:00:00+02:00", "end": "2026-10-12T21:00:00+02:00"},
    {"title": "Birthday: Lisa", "start": "2026-10-17", "end": "2026-10-18", "all_day": true, "event_type": "birthday"},
    {"title": "Webinar", "start": "2026-10-18T19:00:00+02:00", "end": "2026-10-18T20:00:00+02:00", "response": "declined"}
  ],
  "tasks": [
    {"title": "Pay rent", "due": "2026-10-12T00:00:00.000Z"},
    {"title": "File taxes", "due": "2026-10-15", "time_blocked": true},
    {"title": "Done early", "due": "2026-10-20", "completed": "2026-10-13T10:00:00Z"}
  ]
}
```

Optional event fields: `all_day`, `transparency` (`transparent` = shown as free), `response` (`declined`, `tentative`, `accepted`, `needsAction`), `event_type` (`workingLocation`, `birthday`, `outOfOffice`, `focusTime`, `default`), `calendar`. Optional task fields: `completed` (timestamp), `status`, `time_blocked`. Settings keys may be left out; the defaults apply. `--text` prints a readable report instead of JSON.

## Rules

1. **The week** runs from `week_start` 00:00 to the same time seven days later, in `timezone`. `week_of` may be any day inside it.
2. **Events that never count**, each listed with a reason:
   - the user declined it;
   - it is shown as free (`transparency: transparent`, or Outlook `showAs: free`);
   - its type is working location, birthday or out of office;
   - its title contains an item from `ignored_calendar_items` (case-insensitive), or it sits in one of `ignored_calendars`;
   - it falls outside the week.
3. **Timed events** count the part inside the week and outside `working_hours`. An event from 16:00 to 19:00 with work ending at 17:00 counts 2 hours. Tentative and unanswered invites count.
4. **Overlaps count once.** Robin merges overlapping counted events into one block of clock time and reports each overlap as a double booking.
5. **All-day events** score `all_day_points` per day they cover (0 by default, so they only appear in the "ignored" list). When `all_day_points` is above 0, that day's evening is not free.
6. **Tasks** score `task_points` each:
   - Upcoming week: every task due in the week, done or not.
   - Past week: tasks completed in the week (by completion date), plus open tasks that were due in it.
   - Tasks without a due date, or due outside the week, do not count.
   - A task with `time_blocked: true` also has a calendar block, so only the event counts.
7. **Rounding**: hours and points are rounded half up to the nearest 0.25.
8. **Bands**: green when the total is under `green_below`; orange from `green_below` up to but not including `red_from`; red at `red_from` or more.
9. **Free evenings**: a day's evening is free when no counted event overlaps `evening_window` (ignored events do not spoil it). The target is `min_free_evenings` out of 7.
10. **Clock changes**: durations are real elapsed time, so the night the clocks go back has 25 hours.

## Worked example

The week of Monday 12 October 2026, Europe/Amsterdam, working hours Mon–Fri 09:00–17:00. The full input is in the repository at `skills/robin-load-meter/evals/files/example-week.json`, and the unit tests check these numbers.

| Day | Counted events | Hours | Tasks | Points | Free evening |
| --- | --- | --- | --- | --- | --- |
| Mon | Dinner with Sarah 19:00–21:00 | 2 | 2 | 2.5 | no |
| Tue | Dentist 08:00–09:30 (1 h before work), parents' evening 19:30–21:00. Team lunch is inside work hours. | 2.5 | 2 | 3 | no |
| Wed | Football training 18:30–20:00 and Call with mum 19:00–20:00 overlap, so 1.5 h | 1.5 | 3 | 2.25 | no |
| Thu | Focus block 17:00–18:00, book club 19:00–22:00. Partner's gym is ignored. | 4 | 1 | 4.25 | no |
| Fri | Concert 20:00–23:30. "Office" is a working-location event. | 3.5 | 2 | 4 | no |
| Sat | Moving help for Tom 10:00–18:00. Birthday and "drinks (maybe)" shown as free are ignored. | 8 | 2 | 8.5 | yes |
| Sun | Family visit 14:00–17:00. The webinar was declined. | 3 | 2 | 3.5 | yes |

Total: 24.5 event points + 14 tasks × 0.25 = **28 points, orange** (5 points to red). Free evenings: 2 of the 3 wanted. Not counted: "File taxes" (it has a calendar block), "Fix bike light" (no due date) and "Dentist follow-up" (due next week).

Report it as:

```
Next week: 28 points, orange (red starts at 33, 5 to go).
Mon 2.5 · Tue 3 · Wed 2.25 · Thu 4.25 · Fri 4 · Sat 8.5 · Sun 3.5
Free evenings: 2 of 3 wanted (Sat, Sun).
Double booking: Football training and Call with mum overlap for 60 minutes on Wednesday.
Biggest items: Moving help for Tom (8 h), Concert (3.5 h), Book club (3 h).
```
