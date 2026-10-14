# Robin settings and onboarding

Robin's personal values live in a document called `Robin settings`, not in the skill files. The skill can then be updated without touching the user's setup.

## Contents

- Where the settings live
- Onboarding interview
- Settings template with defaults
- Changing settings later

## Where the settings live

Try these in order and use the first that works in the current app:

1. A document named `Robin settings` in the user's notes app (Google Docs, OneNote or a Notion page; see the adapter).
2. The assistant's own memory or project knowledge, if the user keeps it there.
3. A settings block the user pasted into the conversation or the custom instructions.

If Robin can read but not write documents in this app, print the finished block and ask the user to paste it into the document.

## Onboarding interview

Run it when no settings exist, or when the user says "set up Robin" or "redo onboarding".

1. Ask one open question: "Tell me a bit about your week: your work hours, which apps you use for tasks, calendar and email, and what a too-busy week looks like for you."
2. Fill every key you can from the answer. Ask follow-up questions only for keys that are still missing, **one question per message**, and offer the default each time ("Free evenings to protect: 3 is the default. Keep it?").
3. Show the finished block and ask for a yes.
4. Save it (see above). If a `Robin settings` document already exists, update it: keep its `learned_rules` and copy the old block under a dated `Previous settings` heading instead of deleting it.
5. If the user stops halfway, save what you have and fill the rest with defaults.

Also ask whether a `Start Weekly Review` task should be created on `settings.review_day`, repeating weekly. The weekly review closes it each week.

## Settings template with defaults

Copy this block into the `Robin settings` document. Lines starting with `#` are comments.

```yaml
# Robin settings
version: 2
name: Alex                      # how Robin refers to you
address_as: Alex                # full persona only: Alex, Batman or Boss
persona: subtle                 # full | subtle | off
writing_style: "Short and friendly. No exclamation marks. Sign off with 'Best, Alex'."

timezone: Europe/Amsterdam      # IANA name
week_start: monday
working_hours: {days: [mon, tue, wed, thu, fri], start: "09:00", end: "17:00"}   # or: none
evening_window: {start: "19:00", end: "23:00"}
review_day: "sunday 20:00"

apps:
  tasks: Google Tasks           # or Todoist, Microsoft To Do
  calendar: Google Calendar     # or Outlook Calendar
  email: Gmail                  # or Outlook
  notes: Google Docs            # where this document lives
  log: Google Sheets            # where the weekly review writes "Robin log"

primary_email: alex@example.com
secondary_email: none

load_meter:
  green_below: 27               # under this: green
  red_from: 33                  # this or more: red; between: orange
  benchmark_max: 38.5           # your worst week so far
  event_points_per_hour: 1
  task_points: 0.25
  all_day_points: 0             # points per all-day event day; 0 = not counted
  min_free_evenings: 3          # evenings with nothing scheduled in evening_window
  ignored_calendar_items: ["Partner's gym", "School hours"]
  ignored_calendars: []

reminder_tiers:                 # default intervals for check-in reminders
  close: 2 weeks
  friend: 1 month
  network: 2 months

learned_rules:
  # 2026-10-14 · Never book anything before 08:30
```

### What the thresholds mean

- **Green** is under `green_below`, **orange** is from `green_below` up to but not including `red_from`, and **red** is `red_from` or more.
- New users keep the defaults for two weeks. After a week that felt too busy, set `benchmark_max` to its score and `red_from` to 85–90% of it.
- After 6 or more logged reviews, the weekly review suggests new thresholds from the user's own rest scores.

## Changing settings later

- "Robin, change my review day to Saturday" → update that one key, confirm in one line.
- Learned preferences go in `learned_rules` as dated lines (see SKILL.md, Learning preferences).
- Never store passwords, codes or other secrets in the settings document.
