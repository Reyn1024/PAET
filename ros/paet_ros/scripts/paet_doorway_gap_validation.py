#!/usr/bin/env python3
"""Validate scan-rate doorway-gap diagnostic persistence with synthetic messages."""

import csv
import math
import signal
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import rospy

from paet_ros.msg import DoorwayGapDiagnostic


def make_diagnostic(run_id, stamp, decision, width=None, triggered=False):
    msg = DoorwayGapDiagnostic()
    msg.header.stamp = stamp
    msg.header.frame_id = "base_footprint"
    msg.run_id = run_id
    msg.required_width_m = 1.0
    msg.narrow_margin_threshold_m = 0.1
    msg.trigger_threshold_width_m = 1.1
    msg.min_event_duration_s = 0.5
    msg.token_triggered = triggered
    msg.decision = decision
    if width is None:
        msg.estimate_valid = False
        msg.estimated_width_m = math.nan
        msg.left_boundary_y_m = math.nan
        msg.right_boundary_y_m = math.nan
        msg.clearance_margin_m = math.nan
        return msg

    msg.estimate_valid = True
    msg.estimated_width_m = width
    msg.left_boundary_y_m = width / 2.0
    msg.right_boundary_y_m = -width / 2.0
    msg.left_point_count = 10
    msg.right_point_count = 10
    msg.clearance_margin_m = width - msg.required_width_m
    msg.narrow_condition = msg.clearance_margin_m < msg.narrow_margin_threshold_m
    return msg


def wait_for_subscriber(pub):
    deadline = time.time() + 5.0
    while pub.get_num_connections() == 0 and time.time() < deadline:
        if rospy.is_shutdown():
            raise RuntimeError("ROS shut down while waiting for diagnostic logger")
        rospy.sleep(0.05)
    if pub.get_num_connections() == 0:
        raise RuntimeError("timed out waiting for /paet/doorway_gap_diagnostics subscriber")


def stop_logger(proc):
    if proc.poll() is not None:
        return
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=5.0)


def main():
    rospy.init_node("paet_doorway_gap_validation", anonymous=True)
    run_id = "doorway_gap_validation_%s" % uuid.uuid4().hex[:8]
    logger_node_name = "paet_event_logger_validation_%s" % uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory(prefix="paet_doorway_gap_") as log_dir:
        proc = subprocess.Popen([
            "rosrun",
            "paet_ros",
            "paet_event_logger.py",
            "__name:=%s" % logger_node_name,
            "_run_id:=%s" % run_id,
            "_log_dir:=%s" % log_dir,
        ])
        try:
            pub = rospy.Publisher(
                "/paet/doorway_gap_diagnostics",
                DoorwayGapDiagnostic,
                queue_size=10,
            )
            wait_for_subscriber(pub)
            start = rospy.Time.now()
            messages = [
                make_diagnostic(run_id, start, "no_valid_gap"),
                make_diagnostic(run_id, start + rospy.Duration(0.1), "width_above_threshold", 1.3),
                make_diagnostic(run_id, start + rospy.Duration(0.2), "token_triggered", 0.9, True),
            ]
            for msg in messages:
                pub.publish(msg)
                rospy.sleep(0.1)
        finally:
            rospy.sleep(0.25)
            stop_logger(proc)

        csv_path = Path(log_dir) / ("%s_doorway_gap.csv" % run_id)
        with csv_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 3:
            raise AssertionError("expected 3 diagnostic rows, got %d" % len(rows))
        if any(row["run_id"] != run_id for row in rows):
            raise AssertionError("diagnostic CSV contains an unexpected run_id")
        if rows[0]["estimated_width_m"] != "":
            raise AssertionError("invalid estimate width must be blank")
        decisions = [row["decision"] for row in rows]
        expected = ["no_valid_gap", "width_above_threshold", "token_triggered"]
        if decisions != expected:
            raise AssertionError("unexpected diagnostic decisions: %s" % decisions)
        print("doorway-gap diagnostic logging ok: rows=3 run_id=%s" % run_id)


if __name__ == "__main__":
    main()
