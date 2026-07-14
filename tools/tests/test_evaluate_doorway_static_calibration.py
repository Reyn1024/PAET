import csv
import tempfile
import unittest
from pathlib import Path

from tools.evaluate_doorway_static_calibration import summarize_trial


DIAGNOSTIC_FIELDS = [
    "timestamp",
    "run_id",
    "estimate_valid",
    "estimated_width_m",
    "left_boundary_y_m",
    "right_boundary_y_m",
    "required_width_m",
    "narrow_margin_threshold_m",
    "trigger_threshold_width_m",
    "clearance_margin_m",
    "narrow_condition",
    "token_triggered",
    "decision",
]


class DoorwayCalibrationEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.events = self.root / "events.csv"
        self.diagnostics = self.root / "doorway_gap.csv"
        with self.events.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(
                f,
                fieldnames=["run_id", "token", "start_time", "end_time"],
            ).writeheader()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_diagnostics(self, rows):
        with self.diagnostics.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=DIAGNOSTIC_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def trial(self, should_trigger="false"):
        return {
            "trial_id": "trial-1",
            "run_id": "run-1",
            "scenario_type": "wide",
            "manual_label_should_trigger": should_trigger,
            "measured_width_m": "1.30",
            "observation_window_s": "10",
            "event_csv_path": str(self.events),
            "diagnostic_csv_path": str(self.diagnostics),
        }

    def test_valid_non_trigger_width_is_evaluated(self):
        self.write_diagnostics([{
            "timestamp": "1.0",
            "run_id": "run-1",
            "estimate_valid": "true",
            "estimated_width_m": "1.30",
            "left_boundary_y_m": "0.65",
            "right_boundary_y_m": "-0.65",
            "required_width_m": "1.0",
            "narrow_margin_threshold_m": "0.1",
            "trigger_threshold_width_m": "1.1",
            "clearance_margin_m": "0.3",
            "narrow_condition": "false",
            "token_triggered": "false",
            "decision": "width_above_threshold",
        }])

        summary = summarize_trial(self.trial())

        self.assertFalse(summary["triggered"])
        self.assertEqual(summary["valid_estimate_count"], 1)
        self.assertAlmostEqual(summary["observed_gap_width_m"], 1.30)
        self.assertAlmostEqual(summary["width_error_m"], 0.0)

    def test_invalid_estimate_with_geometry_is_rejected(self):
        self.write_diagnostics([{
            "timestamp": "1.0",
            "run_id": "run-1",
            "estimate_valid": "false",
            "estimated_width_m": "0.0",
            "left_boundary_y_m": "",
            "right_boundary_y_m": "",
            "required_width_m": "1.0",
            "narrow_margin_threshold_m": "0.1",
            "trigger_threshold_width_m": "1.1",
            "clearance_margin_m": "",
            "narrow_condition": "false",
            "token_triggered": "false",
            "decision": "no_valid_gap",
        }])

        with self.assertRaisesRegex(ValueError, "invalid estimate must have blank geometry"):
            summarize_trial(self.trial())


if __name__ == "__main__":
    unittest.main()
