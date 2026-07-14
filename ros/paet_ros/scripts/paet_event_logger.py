#!/usr/bin/env python3
"""Metadata-only logger for PAET events and doorway-gap diagnostics."""

import csv
import json
import math
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path

import rospy

from paet_ros.msg import DoorwayGapDiagnostic, PAETEventArray


DOORWAY_GAP_FIELDS = [
    "timestamp",
    "run_id",
    "frame_id",
    "estimate_valid",
    "estimated_width_m",
    "left_boundary_y_m",
    "right_boundary_y_m",
    "left_point_count",
    "right_point_count",
    "required_width_m",
    "narrow_margin_threshold_m",
    "trigger_threshold_width_m",
    "clearance_margin_m",
    "min_event_duration_s",
    "narrow_condition",
    "token_triggered",
    "decision",
]


def finite_or_blank(value):
    value = float(value)
    return value if math.isfinite(value) else ""


@dataclass
class EventSegment:
    token: str
    start_time: float
    end_time: float
    timestamp: float
    confidence: float
    x: float
    y: float
    z: float
    radius: float
    evidence_channels: set = field(default_factory=set)
    risk_delta: float = 0.0
    wait_recommended: bool = False
    detour_recommended: bool = False
    reject_recommended: bool = False
    reason: str = ""

    @classmethod
    def from_event(cls, event):
        return cls(
            token=event.token,
            start_time=event.start_time.to_sec(),
            end_time=event.end_time.to_sec(),
            timestamp=event.header.stamp.to_sec(),
            confidence=float(event.confidence),
            x=event.spatial_anchor.x,
            y=event.spatial_anchor.y,
            z=event.spatial_anchor.z,
            radius=event.radius,
            evidence_channels=set(event.evidence_channels),
            risk_delta=float(event.risk_delta),
            wait_recommended=bool(event.wait_recommended),
            detour_recommended=bool(event.detour_recommended),
            reject_recommended=bool(event.reject_recommended),
            reason=event.reason,
        )

    def update(self, event):
        self.start_time = min(self.start_time, event.start_time.to_sec())
        self.end_time = max(self.end_time, event.end_time.to_sec())
        self.timestamp = max(self.timestamp, event.header.stamp.to_sec())
        self.confidence = max(self.confidence, float(event.confidence))
        self.x = event.spatial_anchor.x
        self.y = event.spatial_anchor.y
        self.z = event.spatial_anchor.z
        self.radius = event.radius
        self.evidence_channels.update(event.evidence_channels)
        self.risk_delta = max(self.risk_delta, float(event.risk_delta))
        self.wait_recommended = self.wait_recommended or bool(event.wait_recommended)
        self.detour_recommended = self.detour_recommended or bool(event.detour_recommended)
        self.reject_recommended = self.reject_recommended or bool(event.reject_recommended)
        if event.reason:
            self.reason = event.reason


class PAETEventLogger:
    def __init__(self):
        rospy.init_node("paet_event_logger")
        self.closed = False
        self.lock = threading.Lock()
        self.active_segments = {}

        logging_cfg = rospy.get_param("/logging", {})
        self.run_id = rospy.get_param("~run_id", logging_cfg.get("run_id", "paet_v1_run"))
        log_dir = rospy.get_param("~log_dir", logging_cfg.get("log_dir", "~/.ros/paet_logs"))
        self.segment_gap_s = float(rospy.get_param("~segment_gap_s", logging_cfg.get("segment_gap_s", 0.75)))
        self.log_dir = Path(os.path.expanduser(log_dir))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.log_dir / ("%s_events.csv" % self.run_id)
        self.jsonl_path = self.log_dir / ("%s_events.jsonl" % self.run_id)
        self.doorway_gap_csv_path = self.log_dir / ("%s_doorway_gap.csv" % self.run_id)

        self.csv_file = self.csv_path.open("a", newline="", encoding="utf-8")
        self.jsonl_file = self.jsonl_path.open("a", encoding="utf-8")
        self.doorway_gap_csv_file = self.doorway_gap_csv_path.open("a", newline="", encoding="utf-8")
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

        self.doorway_gap_writer = csv.DictWriter(
            self.doorway_gap_csv_file,
            fieldnames=DOORWAY_GAP_FIELDS,
        )
        if self.doorway_gap_csv_path.stat().st_size == 0:
            self.doorway_gap_writer.writeheader()
            self.doorway_gap_csv_file.flush()

        rospy.Subscriber("/paet/events", PAETEventArray, self.on_events, queue_size=50)
        rospy.Subscriber(
            "/paet/doorway_gap_diagnostics",
            DoorwayGapDiagnostic,
            self.on_doorway_gap,
            queue_size=200,
        )
        self.flush_timer = rospy.Timer(rospy.Duration(0.25), self.flush_inactive_segments)
        rospy.on_shutdown(self.close)
        rospy.loginfo(
            "PAET logger writing event segments to %s and %s and doorway-gap diagnostics to %s; segment_gap_s=%.3f",
            self.csv_path,
            self.jsonl_path,
            self.doorway_gap_csv_path,
            self.segment_gap_s,
        )

    def on_events(self, msg):
        with self.lock:
            if self.closed:
                return
            for event in msg.events:
                segment = self.active_segments.get(event.token)
                if segment is None:
                    self.active_segments[event.token] = EventSegment.from_event(event)
                    continue

                gap_s = event.start_time.to_sec() - segment.end_time
                if gap_s > self.segment_gap_s:
                    self.write_segment(segment)
                    self.active_segments[event.token] = EventSegment.from_event(event)
                else:
                    segment.update(event)

    def on_doorway_gap(self, msg):
        with self.lock:
            if self.closed:
                return
            if msg.run_id != self.run_id:
                rospy.logerr_throttle(
                    5.0,
                    "Ignoring doorway-gap diagnostic with run_id=%s; logger run_id=%s",
                    msg.run_id,
                    self.run_id,
                )
                return
            row = {
                "timestamp": msg.header.stamp.to_sec(),
                "run_id": self.run_id,
                "frame_id": msg.header.frame_id,
                "estimate_valid": bool(msg.estimate_valid),
                "estimated_width_m": finite_or_blank(msg.estimated_width_m),
                "left_boundary_y_m": finite_or_blank(msg.left_boundary_y_m),
                "right_boundary_y_m": finite_or_blank(msg.right_boundary_y_m),
                "left_point_count": int(msg.left_point_count),
                "right_point_count": int(msg.right_point_count),
                "required_width_m": finite_or_blank(msg.required_width_m),
                "narrow_margin_threshold_m": finite_or_blank(msg.narrow_margin_threshold_m),
                "trigger_threshold_width_m": finite_or_blank(msg.trigger_threshold_width_m),
                "clearance_margin_m": finite_or_blank(msg.clearance_margin_m),
                "min_event_duration_s": finite_or_blank(msg.min_event_duration_s),
                "narrow_condition": bool(msg.narrow_condition),
                "token_triggered": bool(msg.token_triggered),
                "decision": msg.decision,
            }
            self.doorway_gap_writer.writerow(row)
            self.doorway_gap_csv_file.flush()

    def flush_inactive_segments(self, _event=None):
        now = rospy.Time.now().to_sec()
        with self.lock:
            if self.closed:
                return
            stale_tokens = [
                token for token, segment in self.active_segments.items()
                if now - segment.end_time > self.segment_gap_s
            ]
            for token in stale_tokens:
                self.write_segment(self.active_segments.pop(token))

    def write_segment(self, segment):
        row = {
            "timestamp": segment.timestamp,
            "run_id": self.run_id,
            "token": segment.token,
            "confidence": segment.confidence,
            "x": segment.x,
            "y": segment.y,
            "z": segment.z,
            "radius": segment.radius,
            "start_time": segment.start_time,
            "end_time": segment.end_time,
            "evidence_channels": ";".join(sorted(segment.evidence_channels)),
            "risk_delta": segment.risk_delta,
            "wait_recommended": segment.wait_recommended,
            "detour_recommended": segment.detour_recommended,
            "reject_recommended": segment.reject_recommended,
            "reason": segment.reason,
        }
        self.writer.writerow(row)
        self.jsonl_file.write(json.dumps(row, ensure_ascii=True) + "\n")
        self.csv_file.flush()
        self.jsonl_file.flush()

    def close(self):
        with self.lock:
            if self.closed:
                return
            for token in sorted(self.active_segments):
                self.write_segment(self.active_segments[token])
            self.active_segments.clear()
            self.closed = True
            try:
                self.csv_file.close()
                self.jsonl_file.close()
                self.doorway_gap_csv_file.close()
            except Exception:
                pass

    def spin(self):
        rospy.spin()


if __name__ == "__main__":
    PAETEventLogger().spin()
