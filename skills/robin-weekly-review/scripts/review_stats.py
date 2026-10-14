#!/usr/bin/env python3
"""Trend and threshold calibration for the Robin weekly review log.

Standard library only. Reads the log as CSV (exported from the
"Robin log" sheet, header row required) or as one pipe line per week:

    2026-W41 | rest=3 | self=4 | pts_past=29.5 | pts_next=31 | free_eves=2 | status=complete

Commands:

    python3 review_stats.py trend log.csv [--weeks 8]
    python3 review_stats.py calibrate log.csv [--green 27 --red 33]

Both print JSON. See ../references/review-log.md for the column list
and the calibration rule.
"""

import argparse
import csv
import io
import json
import statistics
import sys

NUMERIC = ("rest", "self", "pts_past", "pts_next", "free_eves")


def read_rows(text):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    if "|" in lines[0] and "=" in lines[0]:
        rows = []
        for ln in lines:
            parts = [p.strip() for p in ln.split("|")]
            row = {"week": parts[0]}
            for p in parts[1:]:
                if "=" in p:
                    key, value = p.split("=", 1)
                    row[key.strip()] = value.strip().strip('"')
            rows.append(row)
    else:
        rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
    for row in rows:
        for key in NUMERIC:
            try:
                row[key] = float(row[key]) if row.get(key) not in (None, "") else None
            except ValueError:
                row[key] = None
    return sorted(rows, key=lambda r: r.get("week", ""))


def mean(values):
    values = [v for v in values if v is not None]
    return round(statistics.mean(values), 2) if values else None


def direction(values):
    """Compare the mean of the newer half with the older half."""
    values = [v for v in values if v is not None]
    if len(values) < 4:
        return "not enough data"
    half = len(values) // 2
    old, new = statistics.mean(values[:half]), statistics.mean(values[-half:])
    if abs(new - old) < 0.25:
        return "flat"
    return "up" if new > old else "down"


def trend(rows, weeks):
    recent = rows[-weeks:]
    return {
        "weeks": [r.get("week") for r in recent],
        "average": {k: mean(r.get(k) for r in recent) for k in NUMERIC},
        "direction": {k: direction([r.get(k) for r in recent]) for k in ("rest", "self", "pts_past")},
        "incomplete_reviews": [r.get("week") for r in recent if str(r.get("status", "")).lower() == "incomplete"],
    }


def calibrate(rows, green, red, min_weeks=6):
    usable = [r for r in rows if r.get("rest") is not None and r.get("pts_past") is not None]
    result = {"weeks_used": len(usable), "current": {"green_below": green, "red_from": red}}
    if len(usable) < min_weeks:
        result["suggestion"] = None
        result["reason"] = f"need at least {min_weeks} weeks with a rest score and last week's points"
        return result
    drained = [r["pts_past"] for r in usable if r["rest"] <= 2]
    rested = [r["pts_past"] for r in usable if r["rest"] >= 4]
    new_red = round(statistics.median(drained) * 2) / 2 if len(drained) >= 2 else None
    new_green = round(statistics.median(rested) * 2) / 2 if len(rested) >= 2 else None
    result["drained_weeks"] = len(drained)
    result["rested_weeks"] = len(rested)
    if new_red is None or new_green is None:
        result["suggestion"] = None
        result["reason"] = "need at least 2 drained weeks (rest 1-2) and 2 rested weeks (rest 4-5)"
    elif new_green >= new_red:
        result["suggestion"] = None
        result["reason"] = (f"rested weeks ({new_green:g} pts) are not lighter than drained weeks "
                            f"({new_red:g} pts) yet; points do not explain your rest scores")
    else:
        result["suggestion"] = {"green_below": new_green, "red_from": new_red}
        result["reason"] = (f"median of rested weeks is {new_green:g} pts, "
                            f"median of drained weeks is {new_red:g} pts")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Trend and calibration for the Robin log.")
    parser.add_argument("command", choices=["trend", "calibrate"])
    parser.add_argument("input", nargs="?", help="CSV or pipe-format log (default: stdin)")
    parser.add_argument("--weeks", type=int, default=8, help="weeks to include in the trend")
    parser.add_argument("--green", type=float, default=27)
    parser.add_argument("--red", type=float, default=33)
    args = parser.parse_args(argv)
    text = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    rows = read_rows(text)
    if args.command == "trend":
        out = trend(rows, args.weeks)
    else:
        out = calibrate(rows, args.green, args.red)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
