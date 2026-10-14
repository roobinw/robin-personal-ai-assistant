# Adapter: Microsoft 365

Use when the user's apps are Outlook (mail and calendar) and Microsoft To Do.

## Microsoft To Do

- A repeating task repeats from its due date, not from the day it was done. Use Robin-managed intervals for check-ins: plain tasks with the interval in the title, such as `Sarah (every 2 weeks)` (see `robin-relationship-reminders`).
- Task notes live in the task body. Keep logs out of it.
- Never also create a calendar event for a To Do task (non-negotiable 5), unless the user asks to block time for it; then count only the event.

## Outlook Calendar: fields the Load Meter needs

| Outlook field | Load Meter input |
| --- | --- |
| `subject` | `title` |
| `start` / `end` (with time zone) | `start` / `end` |
| `isAllDay: true` | `all_day: true` |
| `showAs: free` | `transparency: "transparent"` |
| `showAs: oof` | `event_type: "outOfOffice"` |
| `showAs: workingElsewhere` | `event_type: "workingLocation"` |
| `responseStatus.response: declined` | `response: "declined"` |
| calendar name | `calendar` |

`tentative` and `busy` both count. Sending a meeting request emails the attendees, so it follows non-negotiable 2.

## Outlook mail

- Shared mailboxes and send-as addresses: reply from the mailbox the email arrived in.
- Create drafts; send only on an explicit "send".
- Moving to Deleted Items counts as deleting (non-negotiable 3).

## Settings and log locations

- Settings: a Word document or OneNote page called `Robin settings`.
- Log: an Excel workbook called `Robin log` in OneDrive, one row per week with the columns from `robin-weekly-review`.
- If the connector cannot write files, print the text or row for the user to paste.
