#!/usr/bin/env python3
"""Validate PAET logger segment merging against synthetic ROS events."""

import argparse
import csv
import os
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import rospy
from geometry_msgs.msg import Point

from paet_ros.msg import PAETEvent, PAETEventArray


def make_event(stamp, token="doorway_narrow"):
    event = PAETEvent()
    event.header.stamp = rospy.Time.from_sec(stamp)
    event.header.frame_id = "map"
    event.token = token
    event.confidence = 1.0
    event.spatial_anchor = Point(x=0.0, y=0.0, z=0.0)
    event.radius = 0.5
    event.start_time = rospy.Time.from_sec(stamp)
    event.end_time = rospy.Time.from_sec(stamp)
    event.evidence_channels = ["scan", "tf", "robot_footprint"]
    event.risk_delta = 1.0
    event.wait_recommended = False
    event.detour_recommended = True
    event.reject_recommended = True
    event.reason = "synthetic validation"
    return event


def publish_event(pub, stamp):
    msg = PAETEventArray()
    msg.header.stamp = rospy.Time.from_sec(stamp)
    msg.header.frame_id = "map"
    msg.events = [make_event(stamp)]
    pub.publish(msg)
    rospy.sleep(0.08)


def wait_for_subscriber(pub, timeout_s=5.0):
    deadline = time.time() + timeout_s
    while time.time() < deadline and not rospy.is_shutdown():
        if pub.get_num_connections() > 0:
            return
        rospy.sleep(0.05)
    raise RuntimeError("timed out waiting for logger subscriber on /paet/events")


def read_rows(csv_path):
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def assert_rows(csv_path, expected_count, run_id, label):
    rows = read_rows(csv_path)
    if len(rows) != expected_count:
        raise AssertionError("%s expected %d rows, got %d" % (label, expected_count, len(rows)))
    bad_run_ids = [row["run_id"] for row in rows if row["run_id"] != run_id]
    if bad_run_ids:
        raise AssertionError("%s has unexpected run_id values: %s" % (label, bad_run_ids))
    return rows


def start_logger(log_dir, run_id, segment_gap_s):
    cmd = [
        "rosrun",
        "paet_ros",
        "paet_event_logger.py",
        "_run_id:=%s" % run_id,
        "_log_dir:=%s" % log_dir,
        "_segment_gap_s:=%.3f" % segment_gap_s,
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def stop_logger(proc):
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=5.0)


def validate_case(name, event_offsets, stop_delay_s, expected_rows, segment_gap_s):
    run_id = "%s_%s" % (name, uuid.uuid4().hex[:8])
    log_dir_obj = tempfile.TemporaryDirectory(prefix="paet_logger_%s_" % name)
    log_dir = log_dir_obj.name
    csv_path = Path(log_dir) / ("%s_events.csv" % run_id)
    proc = start_logger(log_dir, run_id, segment_gap_s)
    try:
        rospy.sleep(0.8)
        pub = rospy.Publisher("/paet/events", PAETEventArray, queue_size=10)
        wait_for_subscriber(pub)
        base_stamp = rospy.Time.now().to_sec()
        for offset in event_offsets:
            publish_event(pub, base_stamp + offset)
        rospy.sleep(stop_delay_s)
        stop_logger(proc)
        rows = assert_rows(csv_path, expected_rows, run_id, name)
        print("%s ok: rows=%d run_id=%s" % (name, len(rows), run_id))
    finally:
        if proc.poll() is None:
            stop_logger(proc)
        log_dir_obj.cleanup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--segment-gap-s", type=float, default=0.75)
    args = parser.parse_args()

    rospy.init_node("paet_logger_segment_validation", anonymous=True)

    validate_case(
        "continuous_updates_one_row",
        event_offsets=[0.00, 0.05, 0.10, 0.15],
        stop_delay_s=args.segment_gap_s + 0.4,
        expected_rows=1,
        segment_gap_s=args.segment_gap_s,
    )
    validate_case(
        "short_gap_one_row",
        event_offsets=[0.00, 0.05, 0.60, 0.65],
        stop_delay_s=args.segment_gap_s + 0.4,
        expected_rows=1,
        segment_gap_s=args.segment_gap_s,
    )
    validate_case(
        "long_gap_two_rows",
        event_offsets=[0.00, 0.05, 0.90, 0.95],
        stop_delay_s=args.segment_gap_s + 0.4,
        expected_rows=2,
        segment_gap_s=args.segment_gap_s,
    )
    validate_case(
        "ctrl_c_flushes_tail",
        event_offsets=[0.00, 0.05, 0.10],
        stop_delay_s=0.1,
        expected_rows=1,
        segment_gap_s=args.segment_gap_s,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("validation failed: %s" % exc, file=sys.stderr)
        sys.exit(1)
