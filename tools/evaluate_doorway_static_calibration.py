#!/usr/bin/env python3
"""Summarize stationary doorway_narrow calibration trials."""

import argparse
import csv
import re
from pathlib import Path


OBSERVED_GAP_RE = re.compile(r"observed_gap_width=([-+]?[0-9]*\.?[0-9]+)")
TRUE_VALUES = {"1", "true", "yes", "y", "trigger"}
FALSE_VALUES = {"0", "false", "no", "n", "no_trigger"}
PASSAGE_SCENARIOS = {"narrow", "borderline", "wide"}
ALLOWED_SCENARIOS = PASSAGE_SCENARIOS | {"open_negative", "clutter_negative"}


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
    return float(value)


def parse_observed_gap(reason):
    match = OBSERVED_GAP_RE.search(reason or "")
    if not match:
        return None
    return float(match.group(1))


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
    triggered = len(segments) > 0
    observed_gaps = [
        gap for gap in (parse_observed_gap(segment.get("reason", "")) for segment in segments)
        if gap is not None
    ]

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
        "measured_width_m": measured_width,
        "observed_gap_width_m": sum(observed_gaps) / len(observed_gaps) if observed_gaps else None,
        "width_error_m": sum(width_error_values) / len(width_error_values) if width_error_values else None,
        "absolute_width_error_m": sum(abs(value) for value in width_error_values) / len(width_error_values) if width_error_values else None,
        "event_duration_s": total_event_duration,
        "observation_window_s": observation_window,
        "event_coverage_ratio": total_event_duration / observation_window,
        "event_csv_path": trial.get("event_csv_path", ""),
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
        "measured_width_m",
        "observed_gap_width_m",
        "width_error_m",
        "absolute_width_error_m",
        "event_duration_s",
        "observation_window_s",
        "event_coverage_ratio",
        "event_csv_path",
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
