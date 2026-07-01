# PAET Feasibility Assessment

Date: 2026-07-01

Basis:

- `04_experiments/robot_platform_profile.md`
- `04_experiments/robot_system_report.md`
- `04_experiments/ros_topic_inventory.md`
- `03_method/token_taxonomy.md`
- `03_method/paet_schema.md`

## Executive Judgment

PAET is technically feasible on the current robot platform, but the first publishable version should be scoped carefully.

The platform already supports a strong geometry, localization, and navigation stack:

- ROS 1 Noetic.
- Cartographer localization and mapping.
- `move_base` with TEB local planner and layered costmaps.
- Front and rear 2D LiDAR at about 20 Hz.
- 3D LiDAR point cloud at about 10 Hz.
- IMU at about 100 Hz.
- Odometry at about 50 Hz.
- Existing global/local costmaps, virtual walls, scan fusion, and map server.

This is enough to build and evaluate a first PAET prototype for physical traversal events such as narrow passages, temporary obstacles, clearance constraints, and localization uncertainty.

The weakest part is reliable human-group understanding. The platform reports an Astra RGB-D camera and image topics, but the runtime report does not confirm live camera message rates, calibrated camera intrinsics, people detection, or privacy-safe human trajectory logging. Human-related tokens are feasible, but should be treated as Phase 2 unless camera and human-detection pipelines are verified.

## Recommended V1 Scope

V1 should focus on event tokens that can be detected from existing navigation sensors and maps:

- `doorway_narrow`
- `temporary_obstacle`
- `localization_uncertainty`
- `low_clearance`
- `high_clearance`
- `execution_blocked` as a derived token

V1 should treat these as optional or Phase 2:

- `human_group_crossing`
- `wait_required`

Reason: human and waiting tokens need dynamic actor recognition, temporal prediction, privacy handling, and ground-truth labeling. They are important for the paper, but risky as the first dependency.

## Token Feasibility Matrix

| Token | Feasibility | Current evidence channels | Missing requirement | V1 recommendation |
|---|---|---|---|---|
| `doorway_narrow` | High | `/map`, `/scan`, `/scan_ira`, `/points_raw`, robot footprint, costmap parameters | Door/passage labeling or geometric doorway extraction | Include |
| `temporary_obstacle` | High | Static map, local costmap, `/scan`, `/scan_ira`, `/virtual_wall_cloud`, `/points_raw` | Map-vs-current occupancy differencing policy | Include |
| `localization_uncertainty` | Medium-high | Cartographer outputs, `/odom`, `/robot_imu`, ICP status topics, `/constraint_list` | Decide measurable uncertainty proxy; raw pose covariance may not be directly available | Include with proxy |
| `low_clearance` | Medium | `/points_raw`, RGB-D depth topic if live, robot envelope | Confirm vertical clearance scenarios and 3D point-cloud processing | Include if scenario exists |
| `high_clearance` | Medium | Same as low clearance | Define safe-clearance threshold from robot geometry | Include as companion label |
| `execution_blocked` | Medium | Derived from high-risk tokens and planner failure/recovery status | Formal rule linking token state to reject/block decision | Include as derived token |
| `human_group_crossing` | Medium-low | RGB-D topics documented; LiDAR moving clusters possible | Live camera verification, people detection, privacy-safe labels | Phase 2 |
| `wait_required` | Medium-low | Could derive from temporary obstacles or human crossing over time | Temporal ground truth for wait-vs-detour decisions | Phase 2 or derived-only |

## Experiment Feasibility

### Simulation

ROS/Gazebo is plausible because the robot stack uses ROS 1 Noetic and standard navigation components. The first simulation experiments can be built around `move_base`, costmaps, and scripted scenarios:

- narrow doorway or corridor,
- temporary obstacle inserted into a static-map route,
- localization-degraded segment,
- low-clearance obstacle if the simulator model supports height constraints,
- blocked passage requiring detour or reject.

Simulation is feasible and should be the main controlled evaluation environment.

### Real Robot

Real-robot validation is feasible for limited case studies because the robot already has:

- active navigation mode,
- scan and point-cloud sensing,
- static map and Cartographer localization,
- global/local planning,
- action feedback and recovery status.

Real-robot experiments should be small and privacy-safe:

- avoid recording identifiable human imagery in V1,
- use non-human obstacles for temporary blockage,
- use measured doorway/passage widths,
- log only derived metadata when possible,
- keep raw bag/image data outside Git.

## Recommended Experimental Design

### V1 Experiments

1. Token detection benchmark:
   - scenarios: narrow passage, temporary obstacle, low/high clearance, localization-risk segment;
   - metrics: precision, recall, F1, detection latency;
   - ground truth: manually labeled scenario intervals and spatial regions.

2. Decision-support benchmark:
   - compare standard costmap navigation against PAET-augmented decision rules;
   - decisions: proceed, slow/proceed-with-risk, detour, reject;
   - metrics: task success rate, collision/stuck rate, average completion time, detour correctness, failure-reason accuracy.

3. Real-robot case study:
   - one or two building routes;
   - demonstrate that detected PAET tokens correspond to observable execution conditions;
   - avoid making broad performance claims unless repeated trials are completed.

### Baselines

Use baselines that are realistic for the current stack:

- existing `move_base` + TEB + layered costmap;
- costmap with static and obstacle layers only;
- geometric traversability heuristic;
- PAET rule layer on top of existing navigation outputs.

Avoid claiming comparison to large VLA/VLM navigation systems unless such systems are actually implemented.

## Main Risks

1. Human tokens may be under-supported by current verified runtime facts.
2. Localization uncertainty may require proxy metrics because direct covariance may not be exposed by Cartographer.
3. Low/high clearance requires 3D geometry and robot envelope definition; if the building lacks relevant clearance scenarios, this token becomes artificial.
4. The current reports do not include message payloads or bag files, so implementation details still require live robot-side validation.
5. Experimental claims will need repeated trials; one-off demonstrations should be framed as case studies, not performance proof.

## Go / No-Go Judgment

Go for a scoped PAET V1:

- physical traversal tokenization based on LiDAR, 3D point cloud, map, odometry, IMU, localization and costmap signals;
- ROS/Gazebo simulation as the main evaluation;
- limited real-robot validation without privacy-sensitive human data.

Do not make V1 depend on:

- robust human-group detection,
- language-conditioned task reasoning,
- large-scale multi-building generalization,
- full dynamic memory or counterfactual explanation.

## Immediate Next Steps

1. Verify live availability and rates for `/camera/color/image_raw` and `/camera/depth/image_raw`.
2. Record robot footprint dimensions and clearance envelope in `robot_platform_profile.md`.
3. Create a V1 experiment protocol for `doorway_narrow` and `temporary_obstacle`.
4. Define localization uncertainty proxies from available Cartographer, ICP, odometry, and IMU signals.
5. Build the first PAET output schema with required fields only: token, confidence, spatial anchor, time window, evidence channels, and decision effect.

