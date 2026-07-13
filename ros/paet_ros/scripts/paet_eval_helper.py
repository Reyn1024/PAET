#!/usr/bin/env python3
"""Offline helper for event-level PAET metrics.

Expected event CSV columns:
timestamp, run_id, token, confidence, start_time, end_time, ...

Expected ground-truth CSV columns:
start_time, end_time, label
"""

import argparse
import csv


def load_intervals(path, label_column):
    intervals = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            label = row[label_column]
            intervals.append((float(row["start_time"]), float(row["end_time"]), label))
    return intervals


def overlaps(a_start, a_end, b_start, b_end):
    return max(a_start, b_start) <= min(a_end, b_end)


def compute_metrics(events, truth, token):
    event_intervals = [(s, e) for s, e, label in events if label == token]
    truth_intervals = [(s, e) for s, e, label in truth if label == token]

    matched_truth = set()
    true_positive = 0
    false_positive = 0

    for e_start, e_end in event_intervals:
        match = None
        for idx, (t_start, t_end) in enumerate(truth_intervals):
            if idx in matched_truth:
                continue
            if overlaps(e_start, e_end, t_start, t_end):
                match = idx
                break
        if match is None:
            false_positive += 1
        else:
            true_positive += 1
            matched_truth.add(match)

    false_negative = len(truth_intervals) - len(matched_truth)
    precision = true_positive / float(true_positive + false_positive) if (true_positive + false_positive) else 0.0
    recall = true_positive / float(true_positive + false_negative) if (true_positive + false_negative) else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "token": token,
        "tp": true_positive,
        "fp": false_positive,
        "fn": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--ground-truth", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    events = load_intervals(args.events, "token")
    truth = load_intervals(args.ground_truth, "label")
    metrics = compute_metrics(events, truth, args.token)
    for key in ["token", "tp", "fp", "fn", "precision", "recall", "f1"]:
        print("%s,%s" % (key, metrics[key]))


if __name__ == "__main__":
    main()

