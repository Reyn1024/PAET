# Experiment Protocol: V1 Doorway Narrow Token

## Experiment ID

EXP-V1-DN-001

## Purpose

Evaluate whether PAET can detect physically narrow passages that are risky for the robot's footprint and safety margin.

## Evaluation Question

Can a geometry-first PAET detector identify narrow doorway/corridor events from LiDAR/map/path data with traceable evidence?

## Environment

- Primary: ROS/Gazebo simulation.
- Secondary: limited real-robot building route with measured passage widths.
- Robot platform: current ROS 1 Noetic robot described in `robot_platform_profile.md`.

## PAET Tokens Evaluated

- `doorway_narrow`
- optional companion: `high_clearance`

## Required Data Sources

- `/scan` or `/scan_ira`
- `/odom`
- `/tf`
- `/map`
- `/move_base/GlobalPlanner/plan`
- robot footprint width and safety margin from `paet_v1.yaml`

## Scenario Design

Simulation scenarios:

1. Wide passage: width clearly above required robot width.
2. Borderline passage: width near required robot width plus safety margin.
3. Narrow passage: width below required robot width plus safety margin.
4. Route containing both wide and narrow segments.

Real-robot case study:

- Select one or two building passages.
- Manually measure passage width.
- Avoid recording identifiable people.
- Log only PAET events, navigation state, and non-sensitive metadata unless raw data storage is explicitly approved.

## Ground Truth

Ground truth should be interval/region labels:

```text
start_time, end_time, region_id, label, measured_width_m, notes
```

Positive label:

- passage width is less than `robot_width + 2 * safety_margin + narrow_margin_threshold`.

Negative label:

- passage width is safely above the threshold.

## Detector Rule Under Test

Emit `doorway_narrow` when:

```text
observed_gap_width - (robot_width + 2 * safety_margin) < narrow_margin_threshold
```

The event must persist for at least `min_event_duration_s`.

## Baselines

- Existing `move_base` + TEB + costmap without PAET token output.
- Simple distance-to-obstacle heuristic without path cross-section reasoning.

## Metrics

Token metrics:

- Precision.
- Recall.
- F1.
- Detection latency.
- False positive count per run.

Decision-support metrics, if connected to a rule layer:

- stuck/collision count;
- detour correctness;
- completion time.

## Minimum Trial Count

Simulation:

- at least 10 runs per scenario type before making performance claims.

Real robot:

- at least 3 cautious demonstration runs per passage for case-study evidence only.

## Privacy and Safety

- No human subjects are needed for this experiment.
- Real-robot runs should use safety supervision.
- Raw sensor data should remain outside Git.

## Completion Criteria

- PAET events are visible in RViz.
- Event log contains all emitted `doorway_narrow` events.
- Ground-truth labels exist for each run.
- Metrics can be computed from event logs and labels.
- Any manuscript claim maps to `claims_ledger.csv` and result registry rows.

