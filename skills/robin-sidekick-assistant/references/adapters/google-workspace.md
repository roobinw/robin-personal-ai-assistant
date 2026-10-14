# Adapter: Google Workspace

Default backend: Google Tasks, Google Calendar, Gmail, Google Docs (settings) and Google Sheets (log).

## Which connectors exist

| Assistant | Tasks | Calendar | Gmail | Docs / Sheets |
| --- | --- | --- | --- | --- |
| Gemini app | Yes (Workspace app) | Yes | Yes | Yes |
| Claude | **No built-in Tasks connector** | Yes | Yes | Yes (Drive, Docs, Sheets connectors) |

On Claude, Google Tasks needs a third-party MCP server. Without one, tell the user once and suggest switching `settings.apps.tasks` to Todoist (Claude has a Todoist connector) or keeping to-dos in the calendar as all-day reminders.

## Google Tasks: limits that change Robin's behaviour

- **No recurrence in the API.** Connectors cannot read or change a repeating task's schedule. Robin therefore manages check-in intervals itself (see `robin-relationship-reminders`): plain tasks with the interval in the title, such as `Sarah (every 2 weeks)`.
- **Due dates are dates only.** The time part is dropped, so never promise a reminder at a time of day through Tasks. Use a calendar event for that.
- **Read due dates literally.** The API returns midnight UTC (`2026-10-14T00:00:00.000Z`). Take the first 10 characters as the date; never convert it to another time zone.
- **Notes hold at most 8,192 characters and titles 1,024.** Keep logs out of task notes; the weekly review writes to a sheet.
- Repeating tasks cannot be moved between lists, and subtasks or shared tasks cannot repeat.
- Listing completed tasks needs both "show completed" and "show hidden".

## Google Calendar: fields the Load Meter needs

| Calendar field | Load Meter input |
| --- | --- |
| `summary` | `title` |
| `start.dateTime` / `end.dateTime` | `start` / `end` |
| `start.date` / `end.date` (end is exclusive) | `all_day: true`, `start` / `end` |
| `transparency: "transparent"` ("Show as free") | `transparency: "transparent"` |
| your attendee entry's `responseStatus` | `response` (`declined` is not counted) |
| `eventType` (`workingLocation`, `birthday`, `outOfOffice`, `focusTime`, `fromGmail`) | `event_type` |
| calendar name | `calendar` |

Inviting guests emails them, so it follows non-negotiable 2.

## Gmail

- Check which send-as addresses exist before replying; reply from the address the email was sent to.
- Create drafts with the connector and let the user press send, or send only after an explicit "send".
- Labels and archive are fine to suggest; trash and delete need approval (non-negotiable 3).

## Docs and Sheets

- Settings: a Google Doc titled `Robin settings`.
- Log: a Google Sheet titled `Robin log`, one row per week (columns in `robin-weekly-review`).
- If the connector can read but not write Docs or Sheets, print the text or row for the user to paste.
