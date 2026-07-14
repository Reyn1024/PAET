#!/usr/bin/env python3
"""Summarize stationary doorway_narrow calibration trials."""

import argparse
import csv
import re
from pathlib import Path


OBSERVED_GAP_RE = re.compile(r"observed_gap_width=([-+]?[0-9]*\.?[0-9]+)")


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "trigger"}


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


def read_event_segments(path):
    event_path = Path(path).expanduser()
    if not event_path.exists():
        return []
    with event_path.open(newline="", encoding="utf-8-sig") as f:
        return [row for row in csv.DictReader(f) if row.get("token") == "doorway_narrow"]


def summarize_trial(trial):
    measured_width = parse_float(trial.get("measured_width_m", ""))
    should_trigger = parse_bool(trial.get("manual_label_should_trigger", ""))
    scenario_type = trial.get("scenario_type", "")
    segments = read_event_segments(trial.get("event_csv_path", ""))
    triggered = len(segments) > 0
    observed_gaps = [
        gap for gap in (parse_observed_gap(segment.get("reason", "")) for segment in segments)
        if gap is not None
    ]

    width_error_values = []
    if measured_width is not None:
        width_error_values = [gap - measured_width for gap in observed_gaps]

    false_positive = (not should_trigger) and triggered
    missed_positive = should_trigger and not triggered
    fragmented = len(segments) > 1
    trigger_agreement = should_trigger == triggered

    return {
        "trial_id": trial.get("trial_id", ""),
        "run_id": trial.get("run_id", ""),
        "scenario_type": scenario_type,
        "manual_label_should_trigger": should_trigger,
        "triggered": triggered,
        "trigger_agreement": trigger_agreement,
        "segment_count": len(segments),
        "fragmented_static_event": fragmented,
        "false_positive": false_positive,
        "missed_positive": missed_positive,
        "measured_width_m": measured_width,
        "observed_gap_width_m": max(observed_gaps) if observed_gaps else None,
        "width_error_m": max(width_error_values) if width_error_values else None,
        "absolute_width_error_m": max(abs(value) for value in width_error_values) if width_error_values else None,
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
        rows = [summarize_trial(row) for row in csv.DictReader(f)]
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
