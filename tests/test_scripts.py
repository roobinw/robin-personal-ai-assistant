"""Unit tests for the Robin skill scripts. Run: python3 -m unittest discover tests"""

import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


load_meter = load("load_meter", SKILLS / "robin-load-meter/scripts/load_meter.py")
next_due = load("next_due", SKILLS / "robin-relationship-reminders/scripts/next_due.py")
review_stats = load("review_stats", SKILLS / "robin-weekly-review/scripts/review_stats.py")

EXAMPLE_WEEK = json.loads((SKILLS / "robin-load-meter/evals/files/example-week.json").read_text())


def week(**overrides):
    doc = copy.deepcopy(EXAMPLE_WEEK)
    doc.update(overrides)
    return doc


class ExampleWeekTest(unittest.TestCase):
    """The worked example in robin-load-meter/references/scoring-rules.md."""

    def setUp(self):
        self.result = load_meter.score(week())

    def test_total_and_band(self):
        self.assertEqual(self.result["total_points"], 28.0)
        self.assertEqual(self.result["band"], "orange")
        self.assertEqual(self.result["event_points"], 24.5)
        self.assertEqual(self.result["task_points"], 3.5)
        self.assertEqual(self.result["points_to_red"], 5.0)

    def test_per_day_points(self):
        points = [d["points"] for d in self.result["per_day"]]
        self.assertEqual(points, [2.5, 3.0, 2.25, 4.25, 4.0, 8.5, 3.5])

    def test_free_evenings(self):
        self.assertEqual(self.result["free_evenings"], 2)
        self.assertEqual(self.result["free_evening_days"], ["2026-10-17", "2026-10-18"])
        self.assertFalse(self.result["meets_free_evening_target"])

    def test_overlap_is_counted_once_and_reported(self):
        wed = self.result["per_day"][2]
        self.assertEqual(wed["event_hours"], 1.5)
        self.assertEqual(self.result["double_bookings"],
                         [{"first": "Football training", "second": "Call with mum", "overlap_minutes": 60}])

    def test_ignored_reasons(self):
        reasons = {i["title"]: i["reason"] for i in self.result["ignored"]}
        self.assertEqual(reasons["Team lunch"], "inside working hours")
        self.assertEqual(reasons["Partner's gym"], "ignored item: Partner's gym")
        self.assertEqual(reasons["Office"], "working location")
        self.assertEqual(reasons["Birthday: Lisa"], "birthday")
        self.assertEqual(reasons["Neighbourhood drinks (maybe)"], "shown as free")
        self.assertEqual(reasons["Webinar: retirement planning"], "declined")
        self.assertEqual(reasons["File taxes"], "time-blocked (counted as event)")
        self.assertEqual(reasons["Fix bike light"], "no due date")
        self.assertEqual(reasons["Dentist follow-up"], "outside week")


class LoadMeterRulesTest(unittest.TestCase):
    base = {"settings": {"timezone": "Europe/Amsterdam", "green_below": 27, "red_from": 33},
            "week_of": "2026-10-14"}

    def run_with(self, events=(), tasks=(), **settings):
        doc = copy.deepcopy(self.base)
        doc["settings"].update(settings)
        doc["events"], doc["tasks"] = list(events), list(tasks)
        return load_meter.score(doc)

    def test_band_boundaries(self):
        hour = lambda n: {"title": "x", "start": "2026-10-17T08:00:00+02:00",
                          "end": f"2026-10-17T{8 + n:02d}:00:00+02:00"}
        self.assertEqual(self.run_with([hour(1)], green_below=1, red_from=2)["band"], "orange")
        self.assertEqual(self.run_with([hour(2)], green_below=1, red_from=2)["band"], "red")
        self.assertEqual(self.run_with([hour(1)], green_below=1.25, red_from=2)["band"], "green")

    def test_partial_working_hours(self):
        ev = {"title": "Late meeting", "start": "2026-10-14T16:00:00+02:00", "end": "2026-10-14T19:00:00+02:00"}
        r = self.run_with([ev], working_hours={"days": ["mon", "tue", "wed", "thu", "fri"],
                                               "start": "09:00", "end": "17:00"})
        self.assertEqual(r["total_points"], 2.0)

    def test_event_split_across_midnight(self):
        ev = {"title": "Late party", "start": "2026-10-16T22:00:00+02:00", "end": "2026-10-17T02:00:00+02:00"}
        r = self.run_with([ev])
        self.assertEqual([d["event_hours"] for d in r["per_day"]][4:6], [2.0, 2.0])

    def test_all_day_points_setting(self):
        ev = {"title": "Wedding", "start": "2026-10-17", "end": "2026-10-18", "all_day": True}
        self.assertEqual(self.run_with([ev])["total_points"], 0.0)
        r = self.run_with([ev], all_day_points=4)
        self.assertEqual(r["total_points"], 4.0)
        self.assertFalse(r["per_day"][5]["free_evening"])

    def test_past_mode_counts_completed_tasks_by_completion_date(self):
        tasks = [
            {"title": "done early", "due": "2026-10-20", "completed": "2026-10-13T10:00:00Z"},
            {"title": "still open", "due": "2026-10-15"},
            {"title": "done last week", "due": "2026-10-14", "completed": "2026-10-09T10:00:00Z"},
        ]
        doc = copy.deepcopy(self.base)
        doc.update(tasks=tasks, events=[], mode="past")
        r = load_meter.score(doc)
        self.assertEqual(r["tasks_counted"], 2)
        upcoming = self.run_with(tasks=tasks)
        self.assertEqual(upcoming["tasks_counted"], 2)  # "still open" and "done last week" are due this week

    def test_week_start_sunday(self):
        r = self.run_with(week_start="sunday")
        self.assertEqual((r["week_start"], r["week_end"]), ("2026-10-11", "2026-10-17"))

    def test_dst_week(self):
        # Clocks go back on Sunday 25 October 2026 in Europe/Amsterdam.
        ev = {"title": "Night shift", "start": "2026-10-25T00:00:00+02:00", "end": "2026-10-25T04:00:00+01:00"}
        doc = copy.deepcopy(self.base)
        doc.update(week_of="2026-10-21", events=[ev], tasks=[])
        self.assertEqual(load_meter.score(doc)["total_points"], 5.0)

    def test_bad_input_raises(self):
        with self.assertRaises(load_meter.InputError):
            load_meter.score({"mode": "weekly"})


class NextDueTest(unittest.TestCase):
    def due(self, start, every):
        count, unit = next_due.parse_interval(every)
        return next_due.add_interval(next_due.date.fromisoformat(start), count, unit).isoformat()

    def test_readme_example(self):
        self.assertEqual(self.due("2026-09-23", "2 weeks"), "2026-10-07")

    def test_formats(self):
        self.assertEqual(self.due("2026-10-14", "14d"), "2026-10-28")
        self.assertEqual(self.due("2026-10-14", "every 3 weeks"), "2026-11-04")
        self.assertEqual(self.due("2026-10-14", "every! 2 weeks"), "2026-10-28")
        self.assertEqual(self.due("2026-10-14", "fortnight"), "2026-10-28")
        self.assertEqual(self.due("2026-10-14", "month"), "2026-11-14")

    def test_month_end_is_clamped(self):
        self.assertEqual(self.due("2026-01-31", "1m"), "2026-02-28")
        self.assertEqual(self.due("2028-02-29", "1 year"), "2029-02-28")

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            next_due.parse_interval("sometimes")
        with self.assertRaises(ValueError):
            next_due.parse_interval("0 days")


class ReviewStatsTest(unittest.TestCase):
    LOG = "\n".join([
        "2026-W35 | rest=4 | self=4 | pts_past=22 | pts_next=25 | free_eves=4 | status=complete",
        "2026-W36 | rest=2 | self=3 | pts_past=35 | pts_next=30 | free_eves=1 | status=complete",
        "2026-W37 | rest=5 | self=4 | pts_past=20 | pts_next=28 | free_eves=4 | status=complete",
        "2026-W38 | rest=1 | self=2 | pts_past=37 | pts_next=33 | free_eves=1 | status=incomplete",
        "2026-W39 | rest=3 | self=3 | pts_past=29 | pts_next=27 | free_eves=3 | status=complete",
        "2026-W40 | rest=4 | self=5 | pts_past=24 | pts_next=26 | free_eves=3 | status=complete",
    ])

    def test_pipe_and_csv_parse_the_same(self):
        rows = review_stats.read_rows(self.LOG)
        csv_text = "week,rest,self,pts_past,pts_next,free_eves,status\n" + "\n".join(
            f"{r['week']},{r['rest']:g},{r['self']:g},{r['pts_past']:g},{r['pts_next']:g},{r['free_eves']:g},{r['status']}"
            for r in rows)
        self.assertEqual(review_stats.read_rows(csv_text), rows)

    def test_calibration_suggests_thresholds(self):
        out = review_stats.calibrate(review_stats.read_rows(self.LOG), 27, 33)
        self.assertEqual(out["suggestion"], {"green_below": 22.0, "red_from": 36.0})

    def test_calibration_needs_six_weeks(self):
        rows = review_stats.read_rows(self.LOG)[:5]
        self.assertIsNone(review_stats.calibrate(rows, 27, 33)["suggestion"])

    def test_trend(self):
        out = review_stats.trend(review_stats.read_rows(self.LOG), 8)
        self.assertEqual(out["incomplete_reviews"], ["2026-W38"])
        self.assertEqual(out["average"]["pts_past"], 27.83)


if __name__ == "__main__":
    unittest.main()
