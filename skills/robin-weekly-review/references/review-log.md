# The Robin log

One row per weekly review, in a spreadsheet called `Robin log` (Google Sheets or Excel). A spreadsheet has no size cap worth worrying about, and its rows can be charted.

## Columns

| Column | Example | Meaning |
| --- | --- | --- |
| `week` | `2026-W42` | ISO week that just ended |
| `date` | `2026-10-18` | Date of the review |
| `rest` | `3` | Answer (a), 1–5; empty for a quick review |
| `self` | `4` | Answer (b), 1–5; empty for a quick review |
| `less` | `late meetings` | Answer (c), a few words |
| `pts_past` | `29.5` | Load Meter total for the week that ended |
| `pts_next` | `28` | Load Meter total for the coming week |
| `band_next` | `orange` | Band of the coming week |
| `free_eves` | `2` | Free evenings in the coming week |
| `status` | `complete` | `complete`, `quick` or `incomplete` |

Create the sheet with this header row the first time. Never rewrite earlier rows.

## When the spreadsheet cannot be written

Write the same data as one line, in this exact format, to the first place that works:

1. A `Robin log` document (one line per week, newest at the bottom).
2. A comment on a `Robin log` task (Todoist).
3. The chat, asking the user to paste it.

```
2026-W42 | rest=3 | self=4 | pts_past=29.5 | pts_next=28 | free_eves=2 | status=complete | less="late meetings"
```

`scripts/review_stats.py` reads both the CSV export and this line format.

## Trend

Use the last 4–8 rows. For rest, me-time and points, say whether the newer half of the rows is higher, lower or within 0.25 of the older half ("up", "down", "flat"). Mention any week marked `incomplete`.

## Calibration rule

Run it only with 6 or more rows that have both `rest` and `pts_past`.

1. Drained weeks: `rest` 1–2. Rested weeks: `rest` 4–5.
2. Suggested `red_from` = median `pts_past` of drained weeks, rounded to the nearest 0.5.
3. Suggested `green_below` = median `pts_past` of rested weeks, rounded to the nearest 0.5.
4. Suggest only when there are at least 2 weeks of each kind and green is below red. Otherwise say the data does not separate yet.
5. Show the old and new numbers and ask before changing `Robin settings`.

Example: rested weeks scored 22, 20 and 24 points; drained weeks 35 and 37. The suggestion is green under 22 and red from 36.
