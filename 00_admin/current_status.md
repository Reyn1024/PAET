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
- Commit `7dee88b` added unique launch-time `run_id` values and a synthetic ROS validation helper.
- Robot-side logger validation passed continuous merging, sub-gap merging, over-gap splitting, shutdown flush, unique `run_id`, and catkin build checks.
- These checks validate logging semantics only; they do not provide token-detection performance evidence.

## Immediate Next Actions

1. Run the stationary `doorway_narrow` geometry calibration protocol in `04_experiments/protocols/exp_v1_doorway_static_calibration.md`.
2. For each trial, record unique `run_id`, manual width, robot relative placement, config/threshold version, event CSV path, and manual should-trigger label.
3. Include negative controls for both open areas and cluttered non-doorway areas.
4. Summarize width error, event-segment stability, and false positives with `tools/evaluate_doorway_static_calibration.py`.
5. Do not move the robot, freeze thresholds, or compute task success rate until the static geometry calibration is reviewed.

## Feasibility Review

- Robot platform facts have been synchronized from GitHub.
- PAET V1 feasibility has been assessed in `04_experiments/paet_feasibility_assessment.md`.
- Current recommendation: proceed with a scoped V1 focused on LiDAR/map/localization-driven physical traversal tokens; defer robust human-group and language-conditioned waiting tokens to Phase 2.
