#!/usr/bin/env python3
"""Metadata-only logger for PAET events."""

import csv
import json
import os
import threading
from pathlib import Path

import rospy

from paet_ros.msg import PAETEventArray


class PAETEventLogger:
    def __init__(self):
        rospy.init_node("paet_event_logger")
        self.closed = False
        self.lock = threading.Lock()

        logging_cfg = rospy.get_param("/logging", {})
        self.run_id = rospy.get_param("~run_id", logging_cfg.get("run_id", "paet_v1_run"))
        log_dir = rospy.get_param("~log_dir", logging_cfg.get("log_dir", "~/.ros/paet_logs"))
        self.log_dir = Path(os.path.expanduser(log_dir))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.log_dir / ("%s_events.csv" % self.run_id)
        self.jsonl_path = self.log_dir / ("%s_events.jsonl" % self.run_id)

        self.csv_file = self.csv_path.open("a", newline="", encoding="utf-8")
        self.jsonl_file = self.jsonl_path.open("a", encoding="utf-8")
        self.writer = csv.DictWriter(
            self.csv_file,
            fieldnames=[
                "timestamp",
                "run_id",
                "token",
                "confidence",
                "x",
                "y",
                "z",
                "radius",
                "start_time",
                "end_time",
                "evidence_channels",
                "risk_delta",
                "wait_recommended",
                "detour_recommended",
                "reject_recommended",
                "reason",
            ],
        )
        if self.csv_path.stat().st_size == 0:
            self.writer.writeheader()
            self.csv_file.flush()

        rospy.Subscriber("/paet/events", PAETEventArray, self.on_events, queue_size=50)
        rospy.on_shutdown(self.close)
        rospy.loginfo("PAET event logger writing to %s and %s", self.csv_path, self.jsonl_path)

    def on_events(self, msg):
        with self.lock:
            if self.closed:
                return
            for event in msg.events:
                row = {
                    "timestamp": event.header.stamp.to_sec(),
                    "run_id": self.run_id,
                    "token": event.token,
                    "confidence": event.confidence,
                    "x": event.spatial_anchor.x,
                    "y": event.spatial_anchor.y,
                    "z": event.spatial_anchor.z,
                    "radius": event.radius,
                    "start_time": event.start_time.to_sec(),
                    "end_time": event.end_time.to_sec(),
                    "evidence_channels": ";".join(event.evidence_channels),
                    "risk_delta": event.risk_delta,
                    "wait_recommended": event.wait_recommended,
                    "detour_recommended": event.detour_recommended,
                    "reject_recommended": event.reject_recommended,
                    "reason": event.reason,
                }
                self.writer.writerow(row)
                self.jsonl_file.write(json.dumps(row, ensure_ascii=True) + "\n")
            self.csv_file.flush()
            self.jsonl_file.flush()

    def close(self):
        with self.lock:
            self.closed = True
            try:
                self.csv_file.close()
                self.jsonl_file.close()
            except Exception:
                pass

    def spin(self):
        rospy.spin()


if __name__ == "__main__":
    PAETEventLogger().spin()
