#!/usr/bin/env python3
"""Summarize stationary doorway_narrow calibration trials."""

import argparse
import csv
import math
from collections import Counter
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "trigger"}
FALSE_VALUES = {"0", "false", "no", "n", "no_trigger"}
PASSAGE_SCENARIOS = {"narrow", "borderline", "wide"}
ALLOWED_SCENARIOS = PASSAGE_SCENARIOS | {"open_negative", "clutter_negative"}
DIAGNOSTIC_DECISIONS = {
    "no_valid_gap",
    "width_above_threshold",
    "min_duration_pending",
    "token_triggered",
}
DIAGNOSTIC_REQUIRED_FIELDS = {
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
}


def parse_bool(value, field_name, trial_id):
    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(
        "trial %s has invalid %s=%r; use true/false" %
        (trial_id or "<missing-id>", field_name, value)
    )


def parse_float(value):
    value = str(value).strip()
    if not value:
        return None
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite numeric value %r" % value)
    return parsed


def read_event_segments(path, expected_run_id, trial_id):
    if not str(path).strip():
        raise ValueError("trial %s has an empty event_csv_path" % trial_id)
    event_path = Path(path).expanduser()
    if not event_path.is_file():
        raise ValueError("trial %s event CSV does not exist: %s" % (trial_id, event_path))
    with event_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    wrong_run_ids = sorted({row.get("run_id", "") for row in rows if row.get("run_id", "") != expected_run_id})
    if wrong_run_ids:
        raise ValueError(
            "trial %s expected run_id %s but event CSV contains %s" %
            (trial_id, expected_run_id, wrong_run_ids)
        )
    return [row for row in rows if row.get("token") == "doorway_narrow"]


def read_diagnostics(path, expected_run_id, trial_id):
    if not str(path).strip():
        raise ValueError("trial %s has an empty diagnostic_csv_path" % trial_id)
    diagnostic_path = Path(path).expanduser()
    if not diagnostic_path.is_file():
        raise ValueError(
            "trial %s diagnostic CSV does not exist: %s" % (trial_id, diagnostic_path)
        )
    with diagnostic_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing_fields = sorted(DIAGNOSTIC_REQUIRED_FIELDS - fields)
        if missing_fields:
            raise ValueError(
                "trial %s diagnostic CSV is missing fields: %s" %
                (trial_id, ", ".join(missing_fields))
            )
        rows = list(reader)
    if not rows:
        raise ValueError("trial %s diagnostic CSV has no samples" % trial_id)

    wrong_run_ids = sorted({
        row.get("run_id", "") for row in rows
        if row.get("run_id", "") != expected_run_id
    })
    if wrong_run_ids:
        raise ValueError(
            "trial %s expected run_id %s but diagnostic CSV contains %s" %
            (trial_id, expected_run_id, wrong_run_ids)
        )

    previous_timestamp = None
    parsed_rows = []
    for index, row in enumerate(rows, start=2):
        try:
            timestamp = parse_float(row.get("timestamp", ""))
            if timestamp is None:
                raise ValueError("missing timestamp")
            if previous_timestamp is not None and timestamp < previous_timestamp:
                raise ValueError("timestamps are not monotonic")
            previous_timestamp = timestamp

            estimate_valid = parse_bool(row.get("estimate_valid", ""), "estimate_valid", trial_id)
            narrow_condition = parse_bool(row.get("narrow_condition", ""), "narrow_condition", trial_id)
            token_triggered = parse_bool(row.get("token_triggered", ""), "token_triggered", trial_id)
            decision = row.get("decision", "").strip()
            if decision not in DIAGNOSTIC_DECISIONS:
                raise ValueError("unsupported decision=%r" % decision)

            width = parse_float(row.get("estimated_width_m", ""))
            left = parse_float(row.get("left_boundary_y_m", ""))
            right = parse_float(row.get("right_boundary_y_m", ""))
            required_width = parse_float(row.get("required_width_m", ""))
            threshold = parse_float(row.get("narrow_margin_threshold_m", ""))
            trigger_width = parse_float(row.get("trigger_threshold_width_m", ""))
            clearance = parse_float(row.get("clearance_margin_m", ""))

            if required_width is None or threshold is None or trigger_width is None:
                raise ValueError("missing threshold geometry")
            if not math.isclose(trigger_width, required_width + threshold, abs_tol=1e-4):
                raise ValueError("inconsistent trigger_threshold_width_m")
            if estimate_valid:
                if None in (width, left, right, clearance):
                    raise ValueError("valid estimate has blank geometry")
                if not math.isclose(width, left - right, abs_tol=1e-4):
                    raise ValueError("estimated width does not match boundaries")
                if not math.isclose(clearance, width - required_width, abs_tol=1e-4):
                    raise ValueError("clearance margin does not match width")
                expected_narrow = clearance < threshold
                if narrow_condition != expected_narrow:
                    raise ValueError("narrow_condition disagrees with threshold rule")
                if decision == "no_valid_gap":
                    raise ValueError("valid estimate uses no_valid_gap decision")
                if not narrow_condition:
                    if token_triggered or decision != "width_above_threshold":
                        raise ValueError("non-narrow estimate has inconsistent decision flags")
                elif token_triggered != (decision == "token_triggered"):
                    raise ValueError("narrow estimate has inconsistent decision flags")
                elif decision not in {"min_duration_pending", "token_triggered"}:
                    raise ValueError("narrow estimate has inconsistent decision")
            else:
                if any(value is not None for value in (width, left, right, clearance)):
                    raise ValueError("invalid estimate must have blank geometry")
                if narrow_condition or token_triggered or decision != "no_valid_gap":
                    raise ValueError("invalid estimate has inconsistent decision flags")
            parsed_rows.append({
                "timestamp": timestamp,
                "estimate_valid": estimate_valid,
                "estimated_width_m": width,
                "narrow_condition": narrow_condition,
                "token_triggered": token_triggered,
                "decision": decision,
            })
        except ValueError as exc:
            raise ValueError(
                "trial %s diagnostic CSV row %d: %s" % (trial_id, index, exc)
            ) from exc
    return parsed_rows


def summarize_trial(trial):
    trial_id = trial.get("trial_id", "").strip()
    run_id = trial.get("run_id", "").strip()
    if not trial_id or not run_id:
        raise ValueError("every trial requires non-empty trial_id and run_id")

    measured_width = parse_float(trial.get("measured_width_m", ""))
    observation_window = parse_float(trial.get("observation_window_s", ""))
    should_trigger = parse_bool(
        trial.get("manual_label_should_trigger", ""),
        "manual_label_should_trigger",
        trial_id,
    )
    scenario_type = trial.get("scenario_type", "").strip()
    if scenario_type not in ALLOWED_SCENARIOS:
        raise ValueError("trial %s has unsupported scenario_type=%r" % (trial_id, scenario_type))
    if scenario_type in PASSAGE_SCENARIOS and measured_width is None:
        raise ValueError("trial %s requires measured_width_m" % trial_id)
    if observation_window is None or observation_window <= 0.0:
        raise ValueError("trial %s requires positive observation_window_s" % trial_id)

    segments = read_event_segments(trial.get("event_csv_path", ""), run_id, trial_id)
    diagnostics = read_diagnostics(
        trial.get("diagnostic_csv_path", ""),
        run_id,
        trial_id,
    )
    triggered = len(segments) > 0
    diagnostic_triggered = any(row["token_triggered"] for row in diagnostics)
    if triggered != diagnostic_triggered:
        raise ValueError(
            "trial %s event and diagnostic logs disagree about token triggering" % trial_id
        )
    observed_gaps = [
        row["estimated_width_m"] for row in diagnostics if row["estimate_valid"]
    ]
    decision_counts = Counter(row["decision"] for row in diagnostics)

    width_error_values = []
    if measured_width is not None:
        width_error_values = [gap - measured_width for gap in observed_gaps]

    durations = []
    for segment in segments:
        start_time = parse_float(segment.get("start_time", ""))
        end_time = parse_float(segment.get("end_time", ""))
        if start_time is None or end_time is None or end_time < start_time:
            raise ValueError("trial %s contains an invalid event interval" % trial_id)
        durations.append(end_time - start_time)
    total_event_duration = sum(durations)

    false_positive = (not should_trigger) and triggered
    missed_positive = should_trigger and not triggered
    fragmented = len(segments) > 1
    trigger_agreement = should_trigger == triggered

    return {
        "trial_id": trial_id,
        "run_id": run_id,
        "scenario_type": scenario_type,
        "manual_label_should_trigger": should_trigger,
        "triggered": triggered,
        "trigger_agreement": trigger_agreement,
        "segment_count": len(segments),
        "fragmented_static_event": fragmented,
        "false_positive": false_positive,
        "missed_positive": missed_positive,
        "diagnostic_sample_count": len(diagnostics),
        "valid_estimate_count": len(observed_gaps),
        "valid_estimate_ratio": len(observed_gaps) / len(diagnostics),
        "no_valid_gap_count": decision_counts["no_valid_gap"],
        "width_above_threshold_count": decision_counts["width_above_threshold"],
        "min_duration_pending_count": decision_counts["min_duration_pending"],
        "token_triggered_sample_count": decision_counts["token_triggered"],
        "measured_width_m": measured_width,
        "observed_gap_width_m": sum(observed_gaps) / len(observed_gaps) if observed_gaps else None,
        "observed_gap_min_m": min(observed_gaps) if observed_gaps else None,
        "observed_gap_max_m": max(observed_gaps) if observed_gaps else None,
        "width_error_m": sum(width_error_values) / len(width_error_values) if width_error_values else None,
        "absolute_width_error_m": sum(abs(value) for value in width_error_values) / len(width_error_values) if width_error_values else None,
        "event_duration_s": total_event_duration,
        "observation_window_s": observation_window,
        "event_coverage_ratio": total_event_duration / observation_window,
        "event_csv_path": trial.get("event_csv_path", ""),
        "diagnostic_csv_path": trial.get("diagnostic_csv_path", ""),
        "notes": trial.get("operator_notes", ""),
    }


def write_summary(rows, output_path):
    fieldnames = [
        "trial_id",
        "run_id",
        "scenario_type",
        "manual_label_should_trigger",
        "triggered",
        "trigger_agreement",
        "segment_count",
        "fragmented_static_event",
        "false_positive",
        "missed_positive",
        "diagnostic_sample_count",
        "valid_estimate_count",
        "valid_estimate_ratio",
        "no_valid_gap_count",
        "width_above_threshold_count",
        "min_duration_pending_count",
        "token_triggered_sample_count",
        "measured_width_m",
        "observed_gap_width_m",
        "observed_gap_min_m",
        "observed_gap_max_m",
        "width_error_m",
        "absolute_width_error_m",
        "event_duration_s",
        "observation_window_s",
        "event_coverage_ratio",
        "event_csv_path",
        "diagnostic_csv_path",
        "notes",
    ]
    with Path(output_path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", required=True, help="Doorway calibration trial manifest CSV.")
    parser.add_argument("--output", required=True, help="Output summary CSV path.")
    args = parser.parse_args()

    with Path(args.trials).open(newline="", encoding="utf-8-sig") as f:
        trials = list(csv.DictReader(f))

    trial_ids = [trial.get("trial_id", "").strip() for trial in trials]
    run_ids = [trial.get("run_id", "").strip() for trial in trials]
    if len(set(trial_ids)) != len(trial_ids):
        raise ValueError("trial manifest contains duplicate trial_id values")
    if len(set(run_ids)) != len(run_ids):
        raise ValueError("trial manifest contains duplicate run_id values")

    rows = [summarize_trial(trial) for trial in trials]
    write_summary(rows, args.output)

    total = len(rows)
    false_positives = sum(1 for row in rows if row["false_positive"])
    misses = sum(1 for row in rows if row["missed_positive"])
    fragmented = sum(1 for row in rows if row["fragmented_static_event"])
    print("trials,%d" % total)
    print("false_positives,%d" % false_positives)
    print("missed_positives,%d" % misses)
    print("fragmented_static_events,%d" % fragmented)
    print("summary,%s" % args.output)


if __name__ == "__main__":
    main()
