#!/usr/bin/env python3
"""Robin Load Meter: score one week in story points.

Standard library only (Python 3.9+). Reads a JSON document from a file
argument or stdin and prints the result as JSON, or as a short text
report with --text.

Input shape (every settings key is optional and falls back to DEFAULTS):

    {
      "settings": {"timezone": "Europe/Amsterdam", "green_below": 27, ...},
      "week_of": "2026-10-14",          # any date inside the week
      "mode": "upcoming",               # or "past"
      "events": [{"title": "...", "start": "...", "end": "...", ...}],
      "tasks":  [{"title": "...", "due": "2026-10-14", ...}]
    }

The scoring rules are documented in ../references/scoring-rules.md.
"""

import argparse
import json
import math
import sys
from datetime import date, datetime, time, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9
    sys.exit("load_meter.py needs Python 3.9 or newer (zoneinfo).")

DEFAULTS = {
    "timezone": "UTC",
    "week_start": "monday",
    "working_hours": None,  # e.g. {"days": ["mon", ...], "start": "09:00", "end": "17:00"}
    "evening_window": {"start": "19:00", "end": "23:00"},
    "min_free_evenings": 3,
    "green_below": 27,
    "red_from": 33,
    "event_points_per_hour": 1.0,
    "task_points": 0.25,
    "all_day_points": 0.0,
    "ignored_calendar_items": [],
    "ignored_calendars": [],
}

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
SKIPPED_EVENT_TYPES = {
    "workinglocation": "working location",
    "birthday": "birthday",
    "outofoffice": "out of office",
}


class InputError(ValueError):
    pass


def quarter(x):
    """Round half up to the nearest 0.25."""
    return math.floor(x * 4 + 0.5 + 1e-9) / 4


def parse_hhmm(value):
    try:
        h, m = value.split(":")
        return time(int(h) % 24, int(m))
    except Exception as exc:
        raise InputError(f"bad time {value!r}, expected HH:MM") from exc


def weekday_index(name):
    key = str(name).strip().lower()[:3]
    if key not in WEEKDAYS:
        raise InputError(f"bad weekday {name!r}")
    return WEEKDAYS.index(key)


def parse_date(value):
    # Google Tasks returns due dates as RFC 3339 midnight UTC; only the
    # date part carries meaning, so never convert it to another zone.
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise InputError(f"bad date {value!r}") from exc


def parse_datetime(value, tz):
    text = str(value).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise InputError(f"bad datetime {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(timezone.utc)


def at(day, clock, tz):
    # Build the local wall time, then work in UTC: Python subtracts and
    # compares datetimes that share a tzinfo by wall clock, which loses or
    # gains an hour on daylight-saving nights.
    return datetime.combine(day, clock, tzinfo=tz).astimezone(timezone.utc)


def subtract(intervals, cut):
    """Remove the [start, end) interval `cut` from a list of intervals."""
    out = []
    cs, ce = cut
    for s, e in intervals:
        if ce <= s or cs >= e:
            out.append((s, e))
            continue
        if s < cs:
            out.append((s, cs))
        if ce < e:
            out.append((ce, e))
    return out


def union(intervals):
    merged = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def hours(intervals):
    return sum((e - s).total_seconds() for s, e in intervals) / 3600


def split_by_day(intervals, days, tz):
    """Return {date: hours} for intervals cut at local midnights."""
    out = {d: 0.0 for d in days}
    for d in days:
        lo, hi = at(d, time(0), tz), at(d + timedelta(days=1), time(0), tz)
        for s, e in intervals:
            s2, e2 = max(s, lo), min(e, hi)
            if s2 < e2:
                out[d] += (e2 - s2).total_seconds() / 3600
    return out


def evening_interval(day, window, tz):
    start, end = parse_hhmm(window["start"]), parse_hhmm(window["end"])
    end_day = day if end > start else day + timedelta(days=1)
    return at(day, start, tz), at(end_day, end, tz)


def matches_any(text, needles):
    low = (text or "").lower()
    for needle in needles:
        if needle and str(needle).lower() in low:
            return needle
    return None


def score(doc):
    settings = dict(DEFAULTS)
    settings.update({k: v for k, v in (doc.get("settings") or {}).items() if v is not None or k == "working_hours"})
    tz = ZoneInfo(settings["timezone"])
    mode = doc.get("mode", "upcoming")
    if mode not in ("upcoming", "past"):
        raise InputError("mode must be 'upcoming' or 'past'")

    anchor = parse_date(doc.get("week_of") or date.today().isoformat())
    first = weekday_index(settings["week_start"])
    week_start = anchor - timedelta(days=(anchor.weekday() - first) % 7)
    days = [week_start + timedelta(days=i) for i in range(7)]
    w_lo, w_hi = at(days[0], time(0), tz), at(days[-1] + timedelta(days=1), time(0), tz)

    work = settings.get("working_hours")
    work_cuts = []
    if work:
        work_days = {weekday_index(d) for d in work.get("days", WEEKDAYS[:5])}
        ws, we = parse_hhmm(work["start"]), parse_hhmm(work["end"])
        work_cuts = [(at(d, ws, tz), at(d, we, tz)) for d in days if d.weekday() in work_days]

    ignored, counted_events, all_day_points_by_day = [], [], {d: 0.0 for d in days}
    raw_counted = []  # (title, raw interval) used for free evenings and double bookings

    for ev in doc.get("events") or []:
        title = ev.get("title", "(untitled)")
        etype = str(ev.get("event_type", "default")).replace("_", "").lower()
        reason = None
        if str(ev.get("response", "")).lower() == "declined":
            reason = "declined"
        elif str(ev.get("transparency", "")).lower() == "transparent":
            reason = "shown as free"
        elif etype in SKIPPED_EVENT_TYPES:
            reason = SKIPPED_EVENT_TYPES[etype]
        elif ev.get("calendar") and matches_any(ev["calendar"], settings["ignored_calendars"]):
            reason = f"ignored calendar: {ev['calendar']}"
        else:
            hit = matches_any(title, settings["ignored_calendar_items"])
            if hit:
                reason = f"ignored item: {hit}"
        if reason:
            ignored.append({"title": title, "reason": reason})
            continue

        if ev.get("all_day"):
            start, end = parse_date(ev["start"]), parse_date(ev.get("end") or ev["start"])
            if end <= start:
                end = start + timedelta(days=1)  # Google uses an exclusive end date
            covered = [d for d in days if start <= d < end]
            if not covered:
                ignored.append({"title": title, "reason": "outside week"})
            elif settings["all_day_points"] <= 0:
                ignored.append({"title": title, "reason": "all-day (0 points)"})
            else:
                for d in covered:
                    all_day_points_by_day[d] += settings["all_day_points"]
                counted_events.append({"title": title, "all_day": True, "days": [d.isoformat() for d in covered],
                                       "points": quarter(settings["all_day_points"] * len(covered))})
            continue

        s, e = parse_datetime(ev["start"], tz), parse_datetime(ev["end"], tz)
        s, e = max(s, w_lo), min(e, w_hi)
        if s >= e:
            ignored.append({"title": title, "reason": "outside week"})
            continue
        parts = [(s, e)]
        for cut in work_cuts:
            parts = subtract(parts, cut)
        raw_counted.append((title, (s, e)))
        if not parts:
            ignored.append({"title": title, "reason": "inside working hours"})
            continue
        counted_events.append({"title": title, "start": s.astimezone(tz).isoformat(), "end": e.astimezone(tz).isoformat(),
                               "hours": round(hours(parts), 2), "_parts": parts})

    merged = union([p for ev in counted_events if not ev.get("all_day") for p in ev["_parts"]])
    event_hours_by_day = split_by_day(merged, days, tz)

    double_bookings = []
    timed = sorted(raw_counted, key=lambda item: item[1][0])
    for i, (t1, (s1, e1)) in enumerate(timed):
        for t2, (s2, e2) in timed[i + 1:]:
            if s2 >= e1:
                break
            double_bookings.append({"first": t1, "second": t2,
                                    "overlap_minutes": int((min(e1, e2) - s2).total_seconds() // 60)})

    task_count_by_day = {d: 0 for d in days}
    counted_tasks = []
    for task in doc.get("tasks") or []:
        title = task.get("title", "(untitled)")
        if task.get("time_blocked"):
            ignored.append({"title": title, "reason": "time-blocked (counted as event)"})
            continue
        due = parse_date(task["due"]) if task.get("due") else None
        done = parse_datetime(task["completed"], tz).astimezone(tz).date() if task.get("completed") else None
        is_done = done is not None or str(task.get("status", "")).lower() == "completed"
        day = None
        if mode == "upcoming":
            day = due if due in task_count_by_day else None
        else:
            if done in task_count_by_day:
                day = done
            elif not is_done and due in task_count_by_day:
                day = due
        if day is None:
            ignored.append({"title": title, "reason": "no due date" if due is None and done is None else "outside week"})
            continue
        task_count_by_day[day] += 1
        counted_tasks.append({"title": title, "day": day.isoformat()})

    per_day, free_days = [], []
    ev_pts = settings["event_points_per_hour"]
    t_pts = settings["task_points"]
    for d in days:
        lo, hi = evening_interval(d, settings["evening_window"], tz)
        busy = any(s < hi and e > lo for _, (s, e) in raw_counted) or all_day_points_by_day[d] > 0
        if not busy:
            free_days.append(d.isoformat())
        pts = event_hours_by_day[d] * ev_pts + task_count_by_day[d] * t_pts + all_day_points_by_day[d]
        per_day.append({
            "date": d.isoformat(),
            "weekday": WEEKDAYS[d.weekday()].title(),
            "event_hours": quarter(event_hours_by_day[d]),
            "tasks": task_count_by_day[d],
            "points": quarter(pts),
            "free_evening": not busy,
        })

    event_points = hours(merged) * ev_pts + sum(all_day_points_by_day.values())
    task_points = sum(task_count_by_day.values()) * t_pts
    total = quarter(event_points + task_points)
    green, red = settings["green_below"], settings["red_from"]
    band = "green" if total < green else ("orange" if total < red else "red")

    for ev in counted_events:
        ev.pop("_parts", None)
    top = sorted((ev for ev in counted_events if not ev.get("all_day")), key=lambda ev: -ev["hours"])[:5]

    return {
        "week_start": days[0].isoformat(),
        "week_end": days[-1].isoformat(),
        "mode": mode,
        "total_points": total,
        "band": band,
        "thresholds": {"green_below": green, "red_from": red},
        "points_to_red": max(0.0, quarter(red - total)),
        "event_points": quarter(event_points),
        "task_points": quarter(task_points),
        "tasks_counted": len(counted_tasks),
        "per_day": per_day,
        "free_evenings": len(free_days),
        "free_evening_days": free_days,
        "min_free_evenings": settings["min_free_evenings"],
        "meets_free_evening_target": len(free_days) >= settings["min_free_evenings"],
        "double_bookings": double_bookings,
        "top_events": top,
        "ignored": ignored,
    }


def as_text(result):
    icon = {"green": "GREEN", "orange": "ORANGE", "red": "RED"}[result["band"]]
    lines = [
        f"Week {result['week_start']} to {result['week_end']} ({result['mode']}): "
        f"{result['total_points']:g} points, {icon}",
        f"Events {result['event_points']:g} pts, tasks {result['task_points']:g} pts "
        f"({result['tasks_counted']} tasks). Red starts at {result['thresholds']['red_from']:g}.",
        "",
        "Day  Points  Hours  Tasks  Free evening",
    ]
    for d in result["per_day"]:
        lines.append(f"{d['weekday']:<4} {d['points']:>6g} {d['event_hours']:>6g} {d['tasks']:>6}  "
                     f"{'yes' if d['free_evening'] else 'no'}")
    lines.append("")
    lines.append(f"Free evenings: {result['free_evenings']} (target {result['min_free_evenings']})")
    for db in result["double_bookings"]:
        lines.append(f"Double booking: {db['first']} / {db['second']} ({db['overlap_minutes']} min)")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Score a week with the Robin Load Meter.")
    parser.add_argument("input", nargs="?", help="JSON file (default: stdin)")
    parser.add_argument("--text", action="store_true", help="print a short text report instead of JSON")
    args = parser.parse_args(argv)
    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    try:
        result = score(json.loads(raw))
    except (InputError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(as_text(result) if args.text else json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
