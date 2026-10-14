# Adapter: Todoist

Use when `settings.apps.tasks` is Todoist. Calendar and email stay with the user's other apps (usually Google or Microsoft).

## What changes

- **Native interval from today.** Todoist's `every!` recurrence (with an exclamation mark) schedules the next date from the completion date. A check-in task like `Call Sarah` with due `every! 2 weeks` does exactly what Robin needs: when the user reports the catch-up, complete the task and Todoist sets the next one from today.
- `every` without `!` counts from the old due date. Offer to switch check-in tasks to `every!` the first time you see one.
- **Never overwrite a recurring due string** to move a date. Use the connector's reschedule action (or "postpone") so the recurrence survives.
- If the user has no spreadsheet app, log each weekly review as one comment on a task called `Robin log`, using the line format from `robin-weekly-review`. One comment per week keeps the log out of the task description.
- Labels can mark tiers for check-ins: `@close`, `@friend`, `@network`.

## Load Meter inputs

- Count tasks with a due date inside the week. Use the connector's search by date range, or the filter `due after: <day before week start> & due before: <day after week end>`.
- Todoist tasks with a duration and a time also show in some calendar integrations. If the same item appears as a calendar event, count it once, as the event (`time_blocked: true`).
- For the past week, use completed tasks by completion date.

## Settings and log locations

Todoist has no documents. Keep `Robin settings` in the user's notes app (Google Docs, Notion, OneNote) or in the description of a Todoist task called `Robin settings` that has no due date.
