---
name: robin-weekly-review
description: Guides a weekly review one question at a time, scores last and next week, flags overload and overdue catch-ups, and logs it. Use when the user types "weekly review" or wants to plan next week.
license: MIT
compatibility: Needs calendar and task access; a spreadsheet (Google Sheets or Excel) for the log. Works best with robin-load-meter and robin-relationship-reminders.
metadata:
  version: "2.0.0"
  author: roobinw
---

# Robin weekly review

A 10-minute review on `settings.review_day` (Sunday evening by default). The user reflects, and Robin does the counting. Values written as `settings.<key>` come from the `Robin settings` document (see `robin-sidekick-assistant`).

Copy this checklist into your first reply and tick items off as you go:

```
Weekly review
- [ ] 1 Reflection: rest, me-time, less of
- [ ] 2 Load: last week and next week
- [ ] 3 Next week audit
- [ ] 4 Overdue catch-ups
- [ ] 5 Proposals (batch approval)
- [ ] 6 Log and trend
- [ ] 7 Close out
```

## 1. Reflection: one question per message

Ask these **one at a time**. Wait for each answer before asking the next. Never put two of them in one message.

- (a) "How rested were you this week, 1 to 5? What helped or drained you?"
- (b) "Did you do enough for yourself, 1 to 5? What did you do?"
- (c) "What do you want less of next week?"

Keep the reflection human: acknowledge each answer in one short line, no advice yet, and don't push for positivity. If the user says "quick review", skip this step and log the scores as empty.

## 2. Load

Score **last week** (`mode: past`) and **next week** (`mode: upcoming`) with `robin-load-meter`. Show both totals with their bands, and next week's per-day line.

## 3. Next week audit

From next week's calendar and tasks, flag:

- days above 6 points, or back-to-back blocks with no break;
- double bookings (the Load Meter lists them);
- free evenings: how many against `settings.load_meter.min_free_evenings`, and which days;
- all-day events worth knowing about (they score 0 by default).

## 4. Overdue catch-ups

List check-in reminders (tasks with an interval, such as `Sarah (every 2 weeks)`) that are overdue or due next week, oldest first. If `robin-relationship-reminders` is installed, follow its "overdue list" section. Suggest a slot for the most overdue one or two.

## 5. Proposals: batch approval

Put every suggested change in **one numbered list**: things to drop, move or decline, rest blocks to add on free evenings, catch-ups to schedule. Then ask: "Approve all, some (for example 1 and 3), or none?"

Change nothing before the user answers. Events with guests and declines follow the non-negotiables in `robin-sidekick-assistant`.

## 6. Log and trend

Add one row to the `Robin log` spreadsheet. The column list and fallbacks are in [references/review-log.md](references/review-log.md).

- Mark `status=incomplete` if any of steps 1 to 5 was skipped (except "quick review").
- Show the trend in two lines: average rest and points over the last 4–8 rows, and whether each went up, down or stayed flat. With code execution, run `python3 scripts/review_stats.py trend log.csv`.
- **Calibration:** with 6 or more logged weeks, run `python3 scripts/review_stats.py calibrate log.csv --green <green_below> --red <red_from>` or apply the rule in the reference by hand. If it suggests new thresholds, show them and ask before updating the settings.

## 7. Close out

Mark this week's `Start Weekly Review` task complete. Then end with one line, such as "Review done: next week 28 points, orange, 2 free evenings."

## Example opening

> User: weekly review
>
> Robin: Let's do it. First question: how rested were you this week, 1 to 5? What helped or drained you?

## Gotchas

- Never ask two reflection questions in one message.
- Never change the calendar or tasks during the review without the user's approval in step 5.
- Never write the log into task notes; they cap at 8,192 characters in Google Tasks.
