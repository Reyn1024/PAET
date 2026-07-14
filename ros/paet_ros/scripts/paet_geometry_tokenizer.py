#!/usr/bin/env python3
"""Geometry-first PAET tokenizer for ROS1 Noetic.

This node is intentionally read-only with respect to the navigation stack.
It subscribes to map/scan/path data and publishes PAET events plus RViz
markers. It does not publish cmd_vel and does not modify move_base.
"""

import math
import threading
from dataclasses import dataclass

import rospy
import tf2_ros
from geometry_msgs.msg import Point
from nav_msgs.msg import OccupancyGrid, Path
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker, MarkerArray

from paet_ros.msg import PAETEvent, PAETEventArray


def clamp(value, low, high):
    return max(low, min(high, value))


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def transform_point_2d(transform, x, y):
    """Transform a 2D point using a geometry_msgs/TransformStamped."""
    t = transform.transform.translation
    yaw = yaw_from_quaternion(transform.transform.rotation)
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    return (
        t.x + cos_yaw * x - sin_yaw * y,
        t.y + sin_yaw * x + cos_yaw * y,
    )


def distance_point_to_segment(px, py, ax, ay, bx, by):
    vx = bx - ax
    vy = by - ay
    wx = px - ax
    wy = py - ay
    c1 = vx * wx + vy * wy
    if c1 <= 0.0:
        return math.hypot(px - ax, py - ay)
    c2 = vx * vx + vy * vy
    if c2 <= 1e-9:
        return math.hypot(px - ax, py - ay)
    b = min(1.0, c1 / c2)
    proj_x = ax + b * vx
    proj_y = ay + b * vy
    return math.hypot(px - proj_x, py - proj_y)


@dataclass
class ActiveEvent:
    start_time: rospy.Time
    last_seen: rospy.Time


class PAETGeometryTokenizer:
    def __init__(self):
        rospy.init_node("paet_geometry_tokenizer")

        self.global_frame = rospy.get_param("~global_frame", rospy.get_param("/frames/global_frame", "map"))
        self.robot_frame = rospy.get_param("~robot_frame", rospy.get_param("/frames/robot_frame", "base_footprint"))

        topics = rospy.get_param("/topics", {})
        self.map_topic = topics.get("map", "/map")
        self.scan_topic = topics.get("scan", "/scan")
        self.fused_scan_topic = topics.get("fused_scan", "/scan_ira")
        self.plan_topic = topics.get("global_plan", "/move_base/GlobalPlanner/plan")
        self.use_fused_scan = rospy.get_param("~use_fused_scan", True)

        robot = rospy.get_param("/robot", {})
        self.robot_width = float(robot.get("footprint_width_m", 0.70))
        self.safety_margin = float(robot.get("safety_margin_m", 0.15))

        dn = rospy.get_param("/doorway_narrow", {})
        self.dn_enabled = bool(dn.get("enabled", True))
        self.narrow_margin_threshold = float(dn.get("narrow_margin_threshold_m", 0.10))
        self.dn_min_duration = float(dn.get("min_event_duration_s", 0.5))
        self.lookahead_distance = float(dn.get("lookahead_distance_m", 1.5))
        self.forward_min = float(dn.get("forward_min_m", 0.15))
        self.side_limit = float(dn.get("side_limit_m", 2.0))

        to = rospy.get_param("/temporary_obstacle", {})
        self.to_enabled = bool(to.get("enabled", True))
        self.near_path_distance = float(to.get("near_path_distance_m", 0.4))
        self.min_cluster_points = int(to.get("min_cluster_points", 8))
        self.to_min_duration = float(to.get("min_event_duration_s", 1.0))
        self.static_free_threshold = int(to.get("static_free_threshold", 20))
        self.max_scan_range = float(to.get("max_scan_range_m", 8.0))

        self.map_msg = None
        self.plan_points = []
        self.lock = threading.Lock()
        self.active = {}

        self.tf_buffer = tf2_ros.Buffer(cache_time=rospy.Duration(10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)

        self.events_pub = rospy.Publisher("/paet/events", PAETEventArray, queue_size=10)
        self.marker_pub = rospy.Publisher("/paet/debug_markers", MarkerArray, queue_size=10)

        rospy.Subscriber(self.map_topic, OccupancyGrid, self.on_map, queue_size=1)
        rospy.Subscriber(self.plan_topic, Path, self.on_plan, queue_size=1)
        scan_topic = self.fused_scan_topic if self.use_fused_scan else self.scan_topic
        rospy.Subscriber(scan_topic, LaserScan, self.on_scan, queue_size=1)

        rospy.loginfo("PAET tokenizer started. scan_topic=%s map_topic=%s plan_topic=%s", scan_topic, self.map_topic, self.plan_topic)

    def on_map(self, msg):
        with self.lock:
            self.map_msg = msg

    def on_plan(self, msg):
        points = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]
        with self.lock:
            self.plan_points = points

    def on_scan(self, msg):
        now = rospy.Time.now()
        events = []
        markers = MarkerArray()

        base_points = self.scan_points_in_frame(msg, self.robot_frame)
        map_points = self.scan_points_in_frame(msg, self.global_frame)

        if self.dn_enabled and base_points:
            event = self.detect_doorway_narrow(now, base_points)
            if event:
                events.append(event)

        if self.to_enabled and map_points:
            event = self.detect_temporary_obstacle(now, map_points)
            if event:
                events.append(event)

        if events:
            arr = PAETEventArray()
            arr.header.stamp = now
            arr.header.frame_id = self.global_frame
            arr.events = events
            self.events_pub.publish(arr)
            markers.markers = [self.make_marker(i, event) for i, event in enumerate(events)]
            self.marker_pub.publish(markers)

    def scan_points_in_frame(self, scan, target_frame):
        try:
            tf = self.tf_buffer.lookup_transform(
                target_frame,
                scan.header.frame_id,
                scan.header.stamp,
                rospy.Duration(0.05),
            )
        except Exception as exc:
            rospy.logdebug("TF lookup failed %s <- %s: %s", target_frame, scan.header.frame_id, exc)
            return []

        points = []
        angle = scan.angle_min
        for r in scan.ranges:
            if math.isfinite(r) and scan.range_min <= r <= min(scan.range_max, self.max_scan_range):
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                points.append(transform_point_2d(tf, x, y))
            angle += scan.angle_increment
        return points

    def detect_doorway_narrow(self, now, base_points):
        left = []
        right = []
        for x, y in base_points:
            if self.forward_min <= x <= self.lookahead_distance and abs(y) <= self.side_limit:
                if y > 0.0:
                    left.append(y)
                elif y < 0.0:
                    right.append(y)

        if not left or not right:
            self.clear_event("doorway_narrow")
            return None

        left_wall = min(left)
        right_wall = max(right)
        observed_gap = left_wall - right_wall
        required_width = self.robot_width + 2.0 * self.safety_margin
        clearance_margin = observed_gap - required_width

        if clearance_margin >= self.narrow_margin_threshold:
            self.clear_event("doorway_narrow")
            return None

        confidence = clamp(
            (required_width + self.narrow_margin_threshold - observed_gap) / max(self.narrow_margin_threshold, 1e-6),
            0.0,
            1.0,
        )
        active = self.update_event("doorway_narrow", now)
        if (now - active.start_time).to_sec() < self.dn_min_duration:
            return None

        anchor = self.robot_anchor_in_map()
        reason = "observed_gap_width=%.3f required_width=%.3f clearance_margin=%.3f" % (
            observed_gap,
            required_width,
            clearance_margin,
        )
        return self.make_event(
            token="doorway_narrow",
            confidence=confidence,
            anchor=anchor,
            radius=max(observed_gap / 2.0, 0.05),
            start=active.start_time,
            end=now,
            evidence=["scan", "tf", "robot_footprint"],
            risk_delta=0.5 + 0.5 * confidence,
            wait=False,
            detour=True,
            reject=confidence > 0.85,
            reason=reason,
        )

    def detect_temporary_obstacle(self, now, map_points):
        with self.lock:
            map_msg = self.map_msg
            plan_points = list(self.plan_points)

        if map_msg is None or len(plan_points) < 2:
            self.clear_event("temporary_obstacle")
            return None

        unexpected = []
        for x, y in map_points:
            occ = self.occupancy_at(map_msg, x, y)
            if occ is None or occ < 0 or occ > self.static_free_threshold:
                continue
            if self.distance_to_plan(x, y, plan_points) <= self.near_path_distance:
                unexpected.append((x, y))

        if len(unexpected) < self.min_cluster_points:
            self.clear_event("temporary_obstacle")
            return None

        active = self.update_event("temporary_obstacle", now)
        if (now - active.start_time).to_sec() < self.to_min_duration:
            return None

        cx = sum(p[0] for p in unexpected) / len(unexpected)
        cy = sum(p[1] for p in unexpected) / len(unexpected)
        confidence = clamp(float(len(unexpected)) / max(float(self.min_cluster_points * 3), 1.0), 0.0, 1.0)
        anchor = Point(x=cx, y=cy, z=0.0)
        reason = "unexpected_free_space_obstacle_points=%d near_path_distance=%.3f" % (
            len(unexpected),
            self.near_path_distance,
        )
        return self.make_event(
            token="temporary_obstacle",
            confidence=confidence,
            anchor=anchor,
            radius=self.near_path_distance,
            start=active.start_time,
            end=now,
            evidence=["map", "scan", "tf", "global_plan"],
            risk_delta=0.6 + 0.4 * confidence,
            wait=False,
            detour=True,
            reject=confidence > 0.9,
            reason=reason,
        )

    def occupancy_at(self, grid, x, y):
        info = grid.info
        mx = int((x - info.origin.position.x) / info.resolution)
        my = int((y - info.origin.position.y) / info.resolution)
        if mx < 0 or my < 0 or mx >= info.width or my >= info.height:
            return None
        return grid.data[my * info.width + mx]

    def distance_to_plan(self, x, y, points):
        best = float("inf")
        for i in range(len(points) - 1):
            ax, ay = points[i]
            bx, by = points[i + 1]
            best = min(best, distance_point_to_segment(x, y, ax, ay, bx, by))
        return best

    def robot_anchor_in_map(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                self.global_frame,
                self.robot_frame,
                rospy.Time(0),
                rospy.Duration(0.05),
            )
            t = tf.transform.translation
            return Point(x=t.x, y=t.y, z=t.z)
        except Exception:
            return Point(x=0.0, y=0.0, z=0.0)

    def update_event(self, token, now):
        active = self.active.get(token)
        if active is None:
            active = ActiveEvent(start_time=now, last_seen=now)
            self.active[token] = active
        active.last_seen = now
        return active

    def clear_event(self, token):
        self.active.pop(token, None)

    def make_event(self, token, confidence, anchor, radius, start, end, evidence, risk_delta, wait, detour, reject, reason):
        event = PAETEvent()
        event.header.stamp = end
        event.header.frame_id = self.global_frame
        event.token = token
        event.confidence = float(confidence)
        event.spatial_anchor = anchor
        event.radius = float(radius)
        event.start_time = start
        event.end_time = end
        event.evidence_channels = evidence
        event.risk_delta = float(risk_delta)
        event.wait_recommended = bool(wait)
        event.detour_recommended = bool(detour)
        event.reject_recommended = bool(reject)
        event.reason = reason
        return event

    def make_marker(self, index, event):
        marker = Marker()
        marker.header = event.header
        marker.ns = "paet_events"
        marker.id = index
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position = event.spatial_anchor
        marker.pose.orientation.w = 1.0
        marker.scale.x = max(event.radius * 2.0, 0.2)
        marker.scale.y = max(event.radius * 2.0, 0.2)
        marker.scale.z = 0.2
        if event.token == "doorway_narrow":
            marker.color.r = 1.0
            marker.color.g = 0.55
            marker.color.b = 0.0
        else:
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
        marker.color.a = 0.75
        marker.lifetime = rospy.Duration(0.5)
        return marker

    def spin(self):
        rospy.spin()


if __name__ == "__main__":
    PAETGeometryTokenizer().spin()

