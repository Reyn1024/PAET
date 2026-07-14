# Current Status

## Infrastructure

- Workspace scaffold: created.
- Git: installed and configured; repository is synchronized with `Reyn1024/PAET` on branch `main`.
- Robot-side workflow: source changes and sanitized validation facts are synchronized through GitHub.
- ROS package: `ros/paet_ros` builds in the robot's ROS 1 Noetic catkin workspace.
- Zotero/BibTeX integration: planned.

## Research Stage

- Manuscript type: PAET method paper.
- Research maturity: PAET V1 geometry-first method and two minimum experiment protocols are defined; accuracy evaluation has not started.
- Experiment route: ROS/Gazebo simulation plus limited real-robot cases.
- Real robot platform: ROS 1 Noetic building robot; available topics and system facts are recorded under `04_experiments/`.

## Latest Validation

- Validation date: 2026-07-14.
- Validated revision: `6477bf9`.
- `paet_ros` passed `catkin_make` and launched with the robot navigation stack.
- `/paet/events` and `/paet/debug_markers` were published with the expected message types.
- One live `doorway_narrow` event and corresponding marker were observed.
- This is integration evidence only. It does not establish precision, recall, F1, or detector validity.
- The observed clearance margin was `-0.004 m`, so the sample is especially sensitive to scan noise, footprint calibration, and threshold choice.
- Commit `9a37b2b` added scan-rate event merging: one CSV/JSONL row now represents one event segment, with a default `0.75 s` gap threshold.
- The segment logger passes local syntax checks; robot-side boundary validation is still required before metric collection.

## Immediate Next Actions

1. Validate segment logging on the robot: sub-gap merging, over-gap splitting, shutdown flush, and unique `run_id` handling.
2. Run a stationary doorway-width calibration using measured wide, borderline, and narrow passages.
3. Save event logs and ground-truth interval CSV files outside Git; register paths and run configuration in `experiment_registry.csv`.
4. Check whether the current nearest-left/right scan rule produces false positives in open spaces and clutter.
5. Run the `temporary_obstacle` smoke test only after doorway logging and labeling are confirmed.

## Feasibility Review

- Robot platform facts have been synchronized from GitHub.
- PAET V1 feasibility has been assessed in `04_experiments/paet_feasibility_assessment.md`.
- Current recommendation: proceed with a scoped V1 focused on LiDAR/map/localization-driven physical traversal tokens; defer robust human-group and language-conditioned waiting tokens to Phase 2.
