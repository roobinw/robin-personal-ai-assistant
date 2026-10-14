---
name: robin-relationship-reminders
description: Keeps repeating check-ins with people on track, counting the next one from the day you actually spoke. Use for "I spoke to Sarah today", "remind me to call mum every 3 weeks", or who is overdue.
license: MIT
compatibility: Needs a task app (Google Tasks, Todoist or Microsoft To Do). The date script needs Python 3.9+.
metadata:
  version: "2.0.0"
  author: roobinw
---

# Robin relationship reminders

Check-in reminders keep friendships and contacts from drifting. The next reminder always counts from the day the user actually spoke to the person, not from the old due date.

Most task apps cannot do this through their connectors (the Google Tasks API exposes no repeat rules), so **Robin owns the interval**: each person gets one plain task that stores its own interval, and Robin moves its due date.

## Task format

- **Title:** `<Name> (every <interval>)`, for example `Sarah (every 2 weeks)` or `Call mum (every 3 weeks)`.
- **Notes, first line:** `every: 2 weeks | tier: close | last: 2026-10-14`.
- **Notes, after that:** one log line per contact, newest first, at most 12 lines: `2026-10-14 · spoke`.

Default intervals per tier come from `settings.reminder_tiers` (close: 2 weeks, friend: 1 month, network: 2 months).

On Todoist, a task due `every! 2 weeks` works too: Todoist counts from the completion date. There, completing the task is enough (see the Todoist adapter in `robin-sidekick-assistant`).

## "I spoke to Sarah today"

1. **Find the task.** Search the task app for the name. If more than one task matches (two Sarahs), ask which one. If none matches, offer to create one with the tier the user picks.
2. **Work out the date.** Contact date = today unless the user said otherwise ("yesterday", "on Friday"). Next due = contact date + interval. With code execution, run `python3 scripts/next_due.py --from 2026-09-23 --every "2 weeks"`; month intervals stop at the month's last day.
3. **Update the task in place:** set the due date to the next due date, set `last:` in the notes, and add a log line. Do not complete it and create a copy; one task per person keeps the history together.
4. **Confirm in one line,** for example: "Logged. Next catch-up with Sarah: Wednesday 7 October (2 weeks from today)."

If the task repeats natively in the task app (for example, a repeat set in the Google Tasks app), the connector cannot move its repeat. Say so once, and offer to replace it with a Robin-managed task. Delete the old one only after the user agrees.

## Create a reminder

"Remind me to call mum every 3 weeks" → create `Call mum (every 3 weeks)`, due 3 weeks from today, notes `every: 3 weeks | tier: close | last: <today>`. Confirm the first date. Never add a calendar event as well.

## Overdue list

Used by `robin-weekly-review` and when the user asks "who am I overdue with?":

1. Find tasks whose title matches `(every …)` or whose notes start with `every:`.
2. List the ones overdue or due in the next 7 days, oldest first: name, days overdue, last contact.
3. Suggest a concrete slot for the top one or two, using the calendar's free evenings.

## Example

Today is Wednesday 23 September 2026. The task `Sarah (every 2 weeks)` is due 30 September.

> User: Hey Robin, I spoke to Sarah today.
>
> Robin: Logged. Next catch-up with Sarah: Wednesday 7 October (2 weeks from today).

The task's due date is now 7 October, its notes start with `every: 2 weeks | tier: close | last: 2026-09-23`, and the log line `2026-09-23 · spoke` was added.

## Gotchas

- Count from the contact date, never from the old due date.
- Never create a calendar event for a check-in reminder.
- Never delete a task the user made without asking.
