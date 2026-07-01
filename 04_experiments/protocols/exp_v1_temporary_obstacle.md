# Experiment Protocol: V1 Temporary Obstacle Token

## Experiment ID

EXP-V1-TO-001

## Purpose

Evaluate whether PAET can detect temporary obstacles that are absent from the static map but block or threaten the current planned route.

## Evaluation Question

Can a map-vs-current-observation PAET detector identify temporary obstacle events using existing LiDAR, map, TF, and path data?

## Environment

- Primary: ROS/Gazebo simulation.
- Secondary: limited real-robot route with non-human temporary obstacles.
- Robot platform: current ROS 1 Noetic robot described in `robot_platform_profile.md`.

## PAET Tokens Evaluated

- `temporary_obstacle`
- derived, optional: `execution_blocked`

## Required Data Sources

- `/map`
- `/scan` or `/scan_ira`
- `/odom`
- `/tf`
- `/move_base/GlobalPlanner/plan`
- optional: `/move_base/local_costmap/costmap`
- optional: `/move_base/status`

## Scenario Design

Simulation scenarios:

1. No temporary obstacle on route.
2. Temporary obstacle near but not blocking route.
3. Temporary obstacle directly on route.
4. Temporary obstacle appears after the robot has started moving.
5. Persistent blockage where no valid local passage exists.

Real-robot case study:

- Use non-human objects only, such as a box, cone, cart, or barrier.
- Place the object in a known free-space region of the static map.
- Avoid human crowd scenes in V1.
- Keep raw images out of Git and avoid identifiable data.

## Ground Truth

Ground truth should be interval/region labels:

```text
start_time, end_time, obstacle_id, label, map_region, blocking_status, notes
```

Positive label:

- obstacle appears in static-map free space and is near enough to the planned path to affect navigation.

Negative labels:

- no obstacle;
- obstacle exists but is not near the route;
- obstacle corresponds to a known static-map obstacle.

## Detector Rule Under Test

Emit `temporary_obstacle` when:

```text
scan obstacle point or cluster is observed
and the corresponding static-map cells are free
and the cluster is within near_path_distance_m of the planned path
and the event persists for min_event_duration_s
```

Suggested initial thresholds:

```text
static_free_threshold: occupancy <= 20
near_path_distance_m: 0.4
min_cluster_points: 8
min_event_duration_s: 1.0
```

## Baselines

- Existing `move_base` + TEB + costmap without explicit temporary-obstacle token output.
- Costmap obstacle layer event inferred from local costmap updates.
- Simple scan obstacle detector without static-map comparison.

## Metrics

Token metrics:

- Precision.
- Recall.
- F1.
- Detection latency.
- False positive count per run.

Decision-support metrics:

- detour/replan correctness;
- stuck count;
- recovery behavior count;
- route completion success;
- time-to-detect obstacle.

Failure-reason metric:

- proportion of blocked/replanned trials where PAET correctly labels `temporary_obstacle` as the reason.

## Minimum Trial Count

Simulation:

- at least 10 runs per scenario type before making performance claims.

Real robot:

- at least 3 demonstration runs with a non-human obstacle for case-study evidence.

## Privacy and Safety

- No people should be used as obstacles in V1.
- Use lightweight non-damaging obstacles.
- Keep raw sensor data outside Git.
- Record only derived event logs and metrics in the repository.

## Completion Criteria

- PAET event logs contain `temporary_obstacle` events with spatial anchors.
- Ground-truth labels exist for every run.
- Event-level and decision-level metrics are computable.
- Any manuscript claim is backed by experiment and result registry rows.

