#!/usr/bin/env python3
"""Next due date for a Robin-managed reminder: contact date + interval.

Standard library only. Examples:

    python3 next_due.py --from 2026-09-23 --every "2 weeks"
    python3 next_due.py --from 2026-01-31 --every 1m        # -> 2026-02-28
    python3 next_due.py --every 14d                         # from today

Prints JSON: {"from": ..., "every": ..., "next_due": ..., "weekday": ..., "days": ...}
"""

import argparse
import calendar
import json
import re
import sys
from datetime import date, timedelta

UNITS = {
    "d": "days", "day": "days", "days": "days",
    "w": "weeks", "wk": "weeks", "week": "weeks", "weeks": "weeks",
    "m": "months", "mo": "months", "month": "months", "months": "months",
    "y": "years", "yr": "years", "year": "years", "years": "years",
}
PATTERN = re.compile(r"^(?:every\s+)?(\d+)?\s*([a-z]+)$")


def parse_interval(text):
    """'2 weeks', '2w', 'every 3 months', 'week' -> (2, 'weeks')."""
    cleaned = text.strip().lower().replace("!", "").replace("fortnight", "2 weeks")
    match = PATTERN.match(cleaned)
    if not match or match.group(2) not in UNITS:
        raise ValueError(f"cannot read interval {text!r}; use e.g. '2 weeks', '14d', '1 month'")
    count = int(match.group(1) or 1)
    if count < 1:
        raise ValueError("interval must be at least 1")
    return count, UNITS[match.group(2)]


def add_interval(start, count, unit):
    if unit == "days":
        return start + timedelta(days=count)
    if unit == "weeks":
        return start + timedelta(weeks=count)
    months = count if unit == "months" else count * 12
    month_index = start.month - 1 + months
    year, month = start.year + month_index // 12, month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute the next due date of a reminder.")
    parser.add_argument("--from", dest="start", help="date of the contact, YYYY-MM-DD (default: today)")
    parser.add_argument("--every", required=True, help="interval, e.g. '2 weeks', '14d', '1 month'")
    args = parser.parse_args(argv)
    try:
        start = date.fromisoformat(args.start) if args.start else date.today()
        count, unit = parse_interval(args.every)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    nxt = add_interval(start, count, unit)
    print(json.dumps({
        "from": start.isoformat(),
        "every": f"{count} {unit if count != 1 else unit[:-1]}",
        "next_due": nxt.isoformat(),
        "weekday": nxt.strftime("%A"),
        "days": (nxt - start).days,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
