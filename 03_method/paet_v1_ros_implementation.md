# PAET V1 ROS Implementation Method

Date: 2026-07-01

Goal: implement the first PAET prototype as a non-invasive ROS 1 package that reads existing robot data sources and publishes physical-affordance event tokens.

## Core Decision

Start with rules and geometry, not machine learning.

Reason:

- The current robot already exposes LiDAR, point cloud, map, odometry, IMU, costmap, and navigation feedback.
- `doorway_narrow` and `temporary_obstacle` are primarily geometric/map-consistency events.
- Rule-based geometry gives traceable decisions, which is valuable for the SCI method paper.
- Learning-based detectors can be added later after a labeled dataset exists.

## Package Strategy

Create a new ROS 1 package on the Ubuntu robot side:

```text
paet_ros/
  CMakeLists.txt
  package.xml
  config/
    paet_v1.yaml
  launch/
    paet_v1.launch
  msg/
    PAETEvent.msg
    PAETEventArray.msg
  scripts/
    paet_geometry_tokenizer.py
    paet_event_logger.py
    paet_eval_helper.py
  README.md
```

Do not modify the production `move_base`, TEB, Cartographer, or chassis driver packages in V1.

## ROS Data Sources

Use read-only subscriptions first:

| Input | Type | Use |
|---|---|---|
| `/map` | `nav_msgs/OccupancyGrid` | static map prior |
| `/scan` | `sensor_msgs/LaserScan` | current local obstacle geometry |
| `/scan_ira` | `sensor_msgs/LaserScan` | fused front/rear 2D scan, if more stable than `/scan` |
| `/points_raw` | `sensor_msgs/PointCloud2` | 3D geometry and clearance, optional in first node |
| `/odom` | `nav_msgs/Odometry` | robot pose and local motion |
| `/tf` | `tf` | transform scan/robot data into `map` or `odom` frame |
| `/move_base/status` | `actionlib_msgs/GoalStatusArray` | navigation state and stuck/failure context |
| `/move_base/GlobalPlanner/plan` | `nav_msgs/Path` | current planned path |
| `/move_base/local_costmap/costmap` | `nav_msgs/OccupancyGrid` | optional current costmap evidence |
| `/move_base/global_costmap/costmap` | `nav_msgs/OccupancyGrid` | optional baseline costmap evidence |

Avoid image topics in V1 unless privacy and camera runtime are verified.

## Output Topics

Publish:

```text
/paet/events
/paet/debug_markers
/paet/diagnostics
```

Recommended message shape:

```text
# PAETEvent.msg
std_msgs/Header header
string token
float32 confidence
geometry_msgs/Point spatial_anchor
float32 radius
time start_time
time end_time
string[] evidence_channels
float32 risk_delta
bool wait_recommended
bool detour_recommended
bool reject_recommended
string reason
```

```text
# PAETEventArray.msg
std_msgs/Header header
PAETEvent[] events
```

## Node 1: `paet_geometry_tokenizer.py`

Responsibilities:

- detect `doorway_narrow`;
- detect `temporary_obstacle`;
- optionally detect `execution_blocked` from persistent blockage;
- publish token events and debug markers.

### `doorway_narrow` Rule

Use a local corridor/path cross-section test.

Inputs:

- robot footprint width from config;
- safety margin from config;
- current planned path or local forward direction;
- `/scan` or `/scan_ira`;
- optional static map.

Derived values:

```text
required_width = robot_width + 2 * safety_margin
observed_gap_width = free-space width perpendicular to path direction
clearance_margin = observed_gap_width - required_width
```

Token rule:

```text
if clearance_margin < narrow_margin_threshold:
    emit doorway_narrow
```

Suggested initial thresholds, to be calibrated:

```text
safety_margin: 0.15 m
narrow_margin_threshold: 0.10 m
min_event_duration: 0.5 s
```

Confidence:

```text
confidence = clamp((required_width + narrow_margin_threshold - observed_gap_width) / narrow_margin_threshold, 0, 1)
```

Evidence channels:

```text
["scan", "path", "robot_footprint"]
```

Ground truth:

- manually measured doorway/passages;
- manually labeled narrow intervals in bag/simulation logs.

### `temporary_obstacle` Rule

Compare current obstacle observations against the static map along or near the planned route.

Inputs:

- `/map`;
- `/scan` or `/scan_ira`;
- robot pose from TF/odom;
- current global or local plan;
- optional local costmap.

Derived values:

```text
scan_obstacle_points_map_frame
static_map_occupancy_at_points
unexpected_obstacle_count
unexpected_obstacle_cluster_size
distance_to_planned_path
```

Token rule:

```text
if obstacle is observed in currently free static-map space
and obstacle is near the planned path
and it persists for min_event_duration:
    emit temporary_obstacle
```

Suggested initial thresholds:

```text
near_path_distance: 0.4 m
min_cluster_points: 8
min_event_duration: 1.0 s
static_free_threshold: occupancy <= 20
```

Confidence:

```text
confidence = weighted score of persistence, cluster size, and path proximity
```

Evidence channels:

```text
["map", "scan", "path"]
```

Ground truth:

- simulation: spawn obstacle in known free area;
- real robot: place a non-human object in a known free corridor.

### Derived `execution_blocked`

Do not make this a primary detector. Derive it when:

```text
temporary_obstacle or doorway_narrow persists
and no valid alternate path exists
or move_base reports repeated failure/recovery
```

For V1, use it only as an explanatory tag in logs, not as an autonomous stop command.

## Node 2: `paet_event_logger.py`

Responsibilities:

- subscribe to `/paet/events`;
- write CSV/JSONL event logs outside Git-tracked source folders;
- record run metadata.

Minimum columns:

```text
timestamp, run_id, token, confidence, x, y, radius, evidence_channels,
risk_delta, wait_recommended, detour_recommended, reject_recommended, reason
```

## Node 3: `paet_eval_helper.py`

Responsibilities:

- align PAET event logs with ground-truth interval labels;
- compute precision, recall, F1, detection latency;
- export metrics to `05_results/result_registry.csv` manually or via reviewed script.

## Configuration

Create `config/paet_v1.yaml`:

```yaml
frames:
  global_frame: map
  robot_frame: base_footprint

topics:
  map: /map
  scan: /scan
  fused_scan: /scan_ira
  odom: /odom
  global_plan: /move_base/GlobalPlanner/plan
  move_base_status: /move_base/status

robot:
  footprint_width_m: TBD
  footprint_length_m: TBD
  safety_margin_m: 0.15

doorway_narrow:
  enabled: true
  narrow_margin_threshold_m: 0.10
  min_event_duration_s: 0.5
  lookahead_distance_m: 1.5

temporary_obstacle:
  enabled: true
  near_path_distance_m: 0.4
  min_cluster_points: 8
  min_event_duration_s: 1.0
  static_free_threshold: 20
```

Do not finalize robot dimensions until they are verified on the robot.

## Integration Steps On Ubuntu Robot

1. Create `paet_ros` in `/home/robot/catkin_ws/src`.
2. Define `PAETEvent.msg` and `PAETEventArray.msg`.
3. Implement `paet_geometry_tokenizer.py`.
4. Run `catkin_make` or the workspace's normal build command.
5. Launch the normal navigation stack.
6. Launch `paet_v1.launch`.
7. Visualize `/paet/debug_markers` in RViz.
8. Record metadata-only event logs first.
9. Run simulation/real case protocols only after the detector output is stable.

## Validation Before Experiments

Before claiming any experimental result:

- verify topic availability with `rostopic list`;
- verify message rates for `/scan`, `/scan_ira`, `/odom`, `/map`;
- verify TF transform from scan frame to `map` or `odom`;
- verify robot footprint dimensions;
- manually inspect RViz markers for at least three scenarios;
- confirm logs do not contain raw images, credentials, or personal identifiers.

## Paper Framing

Describe V1 as:

> a rule-grounded, geometry-first PAET prototype for physically meaningful traversal events.

Do not claim:

- learned generalization;
- robust human intent understanding;
- language-conditioned planning;
- privacy-sensitive crowd perception;
- full autonomous decision replacement.

